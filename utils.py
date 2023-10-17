import logging
import sys, os

SCRIPT_PATH = os.path.abspath(os.path.dirname(__file__))

class Utils():
    """
    Class that contains various utility functions.
    """

    def __init__(self) -> None:
        pass

    def setup_custom_logger(name, file: str=os.path.join(SCRIPT_PATH, 'logs', 'labswipe.log')) -> logging.Logger:
        """
        Function to return a Logger with all the previously specified options.
        """

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
