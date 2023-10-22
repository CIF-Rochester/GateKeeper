from typing import Callable, Literal, NoReturn, Iterator
from dataclasses import dataclass
import os
import sys
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
        match evt:
            case SwipeEvent(id, lcc):
                # do something with card data

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

def get_cardreader(config: ReaderConfig, logger: Logger) -> CardReader:
    match config.mode:
        case "stdin":
            return StdinReader(logger)
        case _:
            # unreachable
            return None
