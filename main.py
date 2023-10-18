from swipe import Swipe
from account import Account
from strike import Strike, get_strike_for_method
from utils import Utils
from python_freeipa import ClientMeta
from config import load_config, Config
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
    
    while(True):
        # card reader acts as keyboard, so input() is
        # used to get the output of the card reader
        try:
            data_from_swipe = input()
        except EOFError:
            break

        if data_from_swipe.lower() in EXIT_TOKENS:
            break

        swipe = Swipe(data_from_swipe, logger)

        account = Account(swipe, client, logger, config)

        try:
            if account.has_access:
                logger.info(f"Access granted to {account.netid}")
                strike.strike()
            else:
                logger.info(f"Denied access to ID: {swipe.id} LCC: {swipe.lcc}")
        except:
            logger.warning(f"Unable to insantiate account from ID: {swipe.id}, LCC: {swipe.lcc}")

    Utils.exit(logger)

if __name__ == "__main__":
    main()
