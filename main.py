from swipe import Swipe
from account import Account
from strike import Strike, ArduinoStrike, RasPiStrike
from utils import Utils
from python_freeipa import ClientMeta
import configparser
import signal
import urllib3
import logging
import argparse
import os

EXIT_TOKENS = ['q', 'exit', 'quit']

urllib3.disable_warnings()

def parse_args() -> (logging.Logger, Strike):
    parser = argparse.ArgumentParser(description="GateKeeper program for the Computer Interest Floor Lab's door strike.")
    parser.add_argument('--strike', '-s', help='Method used for striking the door. Fake is used for testing purposes.', choices=['fake', 'arduino', 'pi'], default=None)
    parser.add_argument('--log', '-l', help="Use specified log path", default=None)

    args = parser.parse_args()

    cfg_log_path = Utils.check_log_path_cfg()
    if args.log:
        logger: logging.Logger = Utils.setup_custom_logger(__name__, file_path = args.config)
    elif cfg_log_path:
        logger: logging.Logger = Utils.setup_custom_logger(__name__, file_path = cfg_log_path)
    else:
        logger: logging.Logger = Utils.setup_custom_logger(__name__)

    if args.strike:
        method = args.strike
    else:
        try:
            config = configparser.ConfigParser()
            config.read(Utils.PATH_TO_CFG)
            method = config.get('strike', 'method')
        except Exception as e:
            logger.exception(f"Something is wrong with the config file: {e}")
            logger.warning("Setting output method to \"fake\"...")
            method = 'fake'
    
    if method == 'fake':
        strike = Strike(logger)
    elif method == 'arduino':
        strike = ArduinoStrike(logger)
    elif method == 'pi':
        strike = RasPiStrike(logger)

    return logger, strike

logger: logging.Logger
logger, strike = parse_args()

def signal_handler(sig, frame):
    Utils.exit(logger, msg = "Exiting due to CTRL-C...")

signal.signal(signal.SIGINT, signal_handler)

def main():
    try:
        config = configparser.ConfigParser()
        config.read(Utils.PATH_TO_CFG)
        username = config.get('credentials', 'username')
        password = config.get('credentials', 'password')
    except Exception as e:
        logger.exception(f"Something is wrong with the config file: {e}")
        Utils.exit(logger, msg = "Forcing exit...")

    try:
        client = ClientMeta('citadel.cif.rochester.edu', verify_ssl=False)
        client.login(username, password)
        logger.info(f"Successfuly logged in to Citadel IPA as: {username}")
    except Exception as e:
        logger.critical("Unable to connect to Citadel IPA server. Check credentials.")
        Utils.exit(logger, msg = "Forcing exit...")
    
    while(True):
        try:
            data_from_swipe = input()
            # card reader acts as keyboard, so input() is
            # used to get the output of the card reader

            if data_from_swipe.lower() in EXIT_TOKENS:
                break

            swipe = Swipe(data_from_swipe, logger)

            account = Account(swipe, client, logger)

            try:
                if account.has_access:
                    logger.info(f"Access granted to {account.netid}")
                    strike.strike()
                else:
                    logger.info(f"Denied access to ID: {swipe.id} LCC: {swipe.lcc}")
            except:
                logger.warning(f"Unable to insantiate account from ID: {swipe.id}, LCC: {swipe.lcc}")
        except Exception as e:
            logger.exception(f"Encountered error: {e}")

    Utils.exit(logger)

if __name__ == "__main__":
    main()
