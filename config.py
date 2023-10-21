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
class Config:
    logging: Logging
    credentials: Credentials
    access: Access
    strike: Strike

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

        config = Config(
            logging=logging,
            credentials=credentials,
            access=access,
            strike=strike
        )
    except Exception as e:
        print(f"Error in config file {config_path}: {e}", file=sys.stderr)
        exit(1)

    return config
