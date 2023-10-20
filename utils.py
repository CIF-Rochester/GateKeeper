import logging
import configparser
import sys, os

class Utils():
    """
    Class that contains various utility functions.
    """

    SCRIPT_PATH = os.path.abspath(os.path.dirname(__file__))
    PATH_TO_CFG = os.path.join(SCRIPT_PATH, "config.cfg")
    LOG_FILENAME = 'gatekeeper.log'

    def __init__(self) -> None:
        pass

    def check_log_path_cfg():
        config = configparser.ConfigParser()
        config.read(Utils.PATH_TO_CFG)
        
        try:
            path = config.get('log', 'path')
        except:
            Utils.setup_custom_logger(__name__).warning("Unable to load custom log path from config.cfg. Falling back to default log location...")
            path = None
        
        return path

    def setup_custom_logger(name, file_path: str=os.path.join(SCRIPT_PATH, 'logs')) -> logging.Logger:
        """
        Function to return a Logger with all the previously specified options.
        """
        
        if not file_path.endswith(Utils.LOG_FILENAME):
            file = os.path.join(file_path, Utils.LOG_FILENAME)
        else:
            file = file_path
        
        formatter = logging.Formatter(fmt='[%(asctime)s] %(levelname)-8s %(message)s',
                                    datefmt='%Y-%m-%d %H:%M:%S')
        handler = logging.FileHandler(file, mode='a')
        handler.setFormatter(formatter)
        screen_handler = logging.StreamHandler(stream=sys.stdout)
        screen_handler.setFormatter(formatter)
        logger = logging.getLogger(name)
        logger.setLevel(logging.DEBUG)
        logger.addHandler(handler)
        logger.addHandler(screen_handler)
        return logger
    
    def exit(logger: logging.Logger, msg = "Exiting...") -> None:
        """
        Logger behavior on exit.
        """

        logger.info(msg)
        sys.exit(0)
