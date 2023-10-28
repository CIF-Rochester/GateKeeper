from typing import Callable, Literal, NoReturn, Iterator
from dataclasses import dataclass
import os
import sys
import struct
import io
from logging import Logger
from config import Reader as ReaderConfig

'''
Module for reading data from a MODEL:ET-MS90 ETEKJOY card reader.

Use StdinReader or RawKbdReader for reading from the card. Once created, call
read_loop on them and pass in a callback to handle events.

The get_cardreader(reader_config) may be used to create the correct CardReader
class based on the configuration settings.

Example code:

    def handle_cardreader_event(evt: ReaderEvent):
        if isinstance(evt, SwipeEvent):
            # do something with evt.id and evt.lcc

    config = load_config("config.cfg")
    cardreader = get_cardreader(config.reader)
    cardreader.read_loop(handle_cardreader_event)

Data Format:

The MODEL:ET-MS90 ETEKJOY card reader sends data in the following format:

    ;9<id:\d{8}><lcc:\d{2}><garbage>NEWLINE
'''

class ReaderEvent:
    pass

@dataclass
class SwipeEvent(ReaderEvent):
    '''
    Emitted when card data is received.
    '''
    id: str
    lcc: str

@dataclass
class InvalidDataEvent(ReaderEvent):
    '''
    Emitted when unknown input is received in a CardReader.
    '''
    data: str
    exc_info: Exception

class CouldNotInitializeReader(Exception):
    '''
    Raised when a critical error occurs while trying to initialize a CardReader
    object.
    '''
    message: str

    def __init__(self, message: str):
        self.message = message

ReaderEventHandler = Callable[[ReaderEvent], None]

class CardReader:
    '''
    Base class for card reader implementations.
    '''

    def events() -> Iterator[ReaderEvent]:
        '''
        Returns an iterator that yields events from the card reader, in order.
        '''
        pass


def _parse_reader_line(data: str) -> ReaderEvent:
    '''
    Private function to parse lines of input from the card reader. See this
    module's doc comment for a description of the expected format.
    '''
    try:
        if data.startswith(";9"):
            # swipe received
            id = data[2:10]
            lcc = data[10:12]
            return SwipeEvent(id=id, lcc=lcc)
        else:
            return InvalidDataEvent(data=data, exc_info=None)
    except Exception as e:
        return InvalidDataEvent(data=data, exc_info=e)

class StdinReader(CardReader):
    '''
    Reads card data from stdin.
    '''

    def __init__(self, logger: Logger):
        self.logger = logger

    def events(self) -> Iterator[ReaderEvent]:
        logger = self.logger

        while True:
            data = None
            try:
                data = input()
            except EOFError:
                logger.info(f"stdin closed: no more events from the card reader will be received")
                break

            yield _parse_reader_line(data)

class RawKbdReader(CardReader):
    '''
    Reads card data from a raw Linux keyboard device file.
    '''
    device: io.BytesIO
    logger: Logger

    def __init__(self, device: str, logger: Logger):
        self.logger = logger

        try:
            self.device = open(device, mode='rb', buffering=0)
        except FileNotFoundError:
            raise CouldNotInitializeReader(
                message=f"Keyboard device file '{device}' not found"
            )
        except PermissionError:
            raise CouldNotInitializeReader(
                message=f"Lacking permission to open keyboard device file '{device}'"
            )

    def events(self) -> Iterator[ReaderEvent]:
        EVENT_FORMAT = 'llHHi'
        EVENT_SIZE = struct.calcsize(EVENT_FORMAT)

        # kinda cursed way for parsing keyboard events. index the keycode into here
        # and you'll get something reasonable. this doesnt cover all keycodes.
        #
        # control keys are replaced with space.
        #
        # reference: https://github.com/torvalds/linux/blob/v5.5-rc5/include/uapi/linux/input-event-codes.h
        TY_KEY = 1
        KEYS = "  1234567890-= \tqwertyuiop[]\n asdfghjkl;'` \\zxcvbnm,./ "
        VL_KEYDOWN = 1
        VL_KEYUP = 0

        logger = self.logger

        buf = ''

        while True:
            event = self.device.read(EVENT_SIZE)
            if not event:
                logger.info(f"no more data from rawkbd: no more events from the card reader will be received")
                break

            try:
                (tv_sec, tv_usec, type, code, value) = struct.unpack(EVENT_FORMAT, event)
            except Exception as e:
                logger.warning("failed to read key event", exc_info=e)

            if type == TY_KEY and value == VL_KEYDOWN:
                # key was just pressed
                # https://github.com/torvalds/linux/blob/v5.5-rc5/include/uapi/linux/input-event-codes.h#L39
                if code < len(KEYS):
                    # convert keycode to character
                    buf += KEYS[code]
                else:
                    logger.warn(f"received out-of-bounds keycode {code} while reading rawkbd device")

            if buf.endswith('\n'):
                # entire line has been read, parse it and yield it.
                yield _parse_reader_line(buf[0:-1])
                buf = ''

def get_cardreader(config: ReaderConfig, logger: Logger) -> CardReader:
    if config.mode == "stdin":
        return StdinReader(logger)
    elif config.mode == "rawkbd":
        return RawKbdReader(config.device, logger)
    else:
        # unreachable
        return None

# RAW KBD INPUT TESTING CODE
if __name__ == '__main__':
    import logging
    import sys

    logger = logging.getLogger('logger')
    handler = logging.StreamHandler(stream=sys.stdout)
    logger.setLevel(logging.DEBUG)
    logger.addHandler(handler)

    device = sys.argv[1]
    reader = RawKbdReader(device, logger)
    for evt in reader.events():
        logger.info(f"EVENT: {evt}")
