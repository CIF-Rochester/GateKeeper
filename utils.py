import logging
import sys
import os
import pathlib
import configparser
from account import Account
from python_freeipa import ClientMeta
from config import Config

class Utils():
    """
    Class that contains various utility functions.
    """

    SCRIPT_PATH = os.path.abspath(os.path.dirname(__file__))
    PATH_TO_CFG = os.path.join(SCRIPT_PATH, "config.cfg")
    LOG_FILENAME = 'gatekeeper.log'

    def __init__(self) -> None:
        pass


    def setup_custom_logger(name: str, log_file: str) -> logging.Logger:
        """
        Function to return a Logger with all the previously specified options.
        """

        # Ensure directory containing the log_file exists
        pathlib.Path(log_file).parent.mkdir(parents=True, exist_ok=True)
        
        formatter = logging.Formatter(fmt='[%(asctime)s] %(levelname)-8s %(message)s',
                                    datefmt='%Y-%m-%d %H:%M:%S')
        handler = logging.FileHandler(log_file, mode='a')
        handler.setFormatter(formatter)
        screen_handler = logging.StreamHandler(stream=sys.stdout)
        screen_handler.setFormatter(formatter)
        logger = logging.getLogger(name)
        logger.setLevel(logging.DEBUG)
        logger.addHandler(handler)
        logger.addHandler(screen_handler)
        return logger
    
    def check_log_path_cfg():
        config = configparser.ConfigParser()
        config.read(Utils.PATH_TO_CFG)
        
        try:
            path = config.get('log', 'path')
        except:
            Utils.setup_custom_logger(__name__).warning("Unable to load custom log path from config.cfg. Falling back to default log location...")
            path = None
        
        return path
    
    def setup_ipa_client(logger: logging.Logger, config: Config) -> ClientMeta:
        client = None

        try:
            client = ClientMeta(config.credentials.host, verify_ssl=config.credentials.verify_ssl)
            client.login(config.credentials.username, config.credentials.password)

            logger.info(f"Successfuly logged in to IPA at {config.credentials.host} as: {config.credentials.username}")
        except Exception as e:
            logger.critical(f"Unable to connect to IPA server at {config.credentials.host}. Check credentials.", exc_info=e)
            Utils.exit(logger, msg = "Forcing exit...")

        return client

    def get_account_from_ipa(id: str, lcc: str, logger: logging.Logger, client: ClientMeta, config: Config) -> Account:
        account = None

        try:
            account = Account(id, lcc, client, logger, config)
        except Exception as e:
            # Note: This may log errors from python-freeipa. Inspecting the
            # library source shows this will not leak any credentials into the
            # log: https://github.com/waldur/python-freeipa/blob/develop/src/python_freeipa/exceptions.py
            logger.warning(f"Unable to instantiate account from ID: {id}, LCC: {lcc}", exc_info=e)

        return account
    
    def exit(logger: logging.Logger, msg = "Exiting...") -> None:
        """
        Logger behavior on exit.
        """

        logger.info(msg)
        sys.exit(0)
