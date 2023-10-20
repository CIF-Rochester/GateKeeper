import logging
import sys
import os
import pathlib
import configparser


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
    
    def exit(logger: logging.Logger, msg = "Exiting...") -> None:
        """
        Logger behavior on exit.
        """

        logger.info(msg)
        sys.exit(0)
