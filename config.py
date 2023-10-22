from typing import Union
import os
import configparser
import sys
from dataclasses import dataclass

@dataclass
class Logging:
    # path to log file
    log: os.PathLike

@dataclass
class Credentials:
    host: str
    verify_ssl: bool
    username: str
    password: str

    def __repr__(self):
        # Custom repr to prevent accidentally printing the password
        return f"Credentials(host={repr(self.host)}, verify_ssl={repr(self.verify_ssl)}, username={repr(self.username)}, password=*****)"

@dataclass
class Access:
    # comma separated list of groups to grant access to
    allowed_groups: set()

@dataclass
class Strike:
    # Make sure to keep these two lists in sync
    METHODS = ['fake', 'arduino', 'pi']
    method: Union['fake', 'arduino', 'pi']

@dataclass
class Reader:
    # Keep these two lists in sync
    MODES = ['stdin', 'rawkbd']
    mode: Union['stdin', 'rawkbd']

    # Path to keyboard device file. Required only when mode=rawkbd
    device: os.PathLike

@dataclass
class Config:
    logging: Logging
    credentials: Credentials
    access: Access
    strike: Strike
    reader: Reader

def load_config(config_path: os.PathLike) -> Config:
    '''
    Load and validate the config file. Exits the program if the config is invalid.
    '''

    # NOTE: This method logs directly to stderr instead of using the proper
    # logger, because the logger is not available before the config is loaded.

    try:
        cfg = configparser.ConfigParser()
        cfg.read(config_path)
    except Exception as e:
        print(f"Failed to load config file from {config_path}: {e}", file=sys.stderr)
        exit(1)

    try:
        logging = Logging(log=cfg.get("logging", "log"))

        credentials = Credentials(
            host=cfg.get('credentials', 'host'),
            verify_ssl=cfg.getboolean('credentials', 'verify_ssl'),
            username=cfg.get('credentials', 'username'),
            password=cfg.get('credentials', 'password')
        )

        access = Access(
            allowed_groups=set(cfg.get('access', 'allowed_groups').split(','))
        )

        strike_method = cfg.get('strike', 'method')
        if strike_method not in Strike.METHODS:
            raise TypeError(f'Expected strike.method to be one of {Strike.METHODS}')
        strike = Strike(
            method=strike_method
        )

        reader_mode = cfg.get('reader', 'mode')
        if reader_mode not in Reader.MODES:
            raise TypeError(f'Expected reader.mode to be one of {Reader.MODES}')
        reader_device = None
        if reader_mode == 'rawkbd':
            reader_device = cfg.get('reader', 'device')
        reader = Reader(
            mode=reader_mode,
            device=reader_device
        )

        config = Config(
            logging=logging,
            credentials=credentials,
            access=access,
            strike=strike,
            reader=reader,
        )
    except Exception as e:
        print(f"Error in config file {config_path}: {e}", file=sys.stderr)
        exit(1)

    return config
