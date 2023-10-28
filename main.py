from account import Account
from strike import Strike, get_strike_for_method
from utils import Utils
from python_freeipa import ClientMeta
from config import load_config, Config
import cardreader
import signal
import urllib3
import logging
import argparse
import os

SCRIPT_PATH = os.path.abspath(os.path.dirname(__file__))
DEFAULT_CFG_PATH = os.path.join(SCRIPT_PATH, "config.cfg")
EXIT_TOKENS = ['q', 'exit', 'quit']
LOGGER_NAME = 'lab_swipe'

urllib3.disable_warnings()

def signal_handler(sig, frame):
    Utils.exit(logging.getLogger(LOGGER_NAME), msg = "Exiting due to CTRL-C...")

signal.signal(signal.SIGINT, signal_handler)

def main():
    parser = argparse.ArgumentParser(description="GateKeeper program for controlling an electronic door strike with a card reader.")
    parser.add_argument('--strike', '-s', help='Method used for controlling the door strike. Fake is used for testing purposes.', choices=['fake', 'arduino', 'pi'], default=None)
    parser.add_argument('--config', '-c', help='Path to GateKeeper config file.', default=DEFAULT_CFG_PATH)

    args = parser.parse_args()

    path_to_cfg = args.config
    config: Config = load_config(path_to_cfg)

    logger: logging.Logger = Utils.setup_custom_logger(LOGGER_NAME, log_file=config.logging.log)
    logger.info(f"Loaded configuration from {path_to_cfg}: {repr(config)}")

    strike_method = config.strike.method
    if args.strike:
        strike_method = args.strike
    strike = get_strike_for_method(strike_method, logger)

    try:
        client = ClientMeta(config.credentials.host, verify_ssl=config.credentials.verify_ssl)
        client.login(config.credentials.username, config.credentials.password)
        logger.info(f"Successfuly logged in to IPA at {config.credentials.host} as: {config.credentials.username}")
    except Exception as e:
        logger.critical(f"Unable to connect to IPA server at {config.credentials.host}. Check credentials.")
        Utils.exit(logger, msg = "Forcing exit...")

    reader = cardreader.get_cardreader(config.reader, logger)
    for evt in reader.events():
        if isinstance(evt, cardreader.SwipeEvent):
            id = evt.id
            lcc = evt.lcc
            try:
                account = Account(id, lcc, client, logger, config)
            except Exception as e:
                # Note: This may log errors from python-freeipa. Inspecting the
                # library source shows this will note leak any credentials into the
                # log: https://github.com/waldur/python-freeipa/blob/develop/src/python_freeipa/exceptions.py
                logger.warning(f"Unable to instantiate account from ID: {id}, LCC: {lcc}", exc_info=e)

            if account.has_access:
                logger.info(f"Access granted to {account.netid}")
                strike.strike()
            else:
                logger.info(f"Denied access to ID: {id} LCC: {lcc}")
        elif isinstance(evt, cardreader.InvalidDataEvent):
            logger.warning(f"Invalid data received from card reader: {evt.data}", exc_info=evt.exc_info)
        else:
            logger.warning(f"Ignoring unimplemented reader event {evt}")

    Utils.exit(logger)

if __name__ == "__main__":
    # Catch any exceptions that bubble up all the way through `main` to make
    # sure the exception gets logged properly.
    try:
        main()
    except Exception as e:
        logger = logging.getLogger(LOGGER_NAME)
        if logger is None:
            # Unhandled exception was raised before logger could be created, so
            # we can't do anything better than just letting Python crash.
            raise e

        logger.critical('Unexpected exception. Crashing...', exc_info=e)
        exit(1)
