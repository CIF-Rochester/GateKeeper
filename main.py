from swipe import Swipe
from account import Account
from strike import Strike
from utils import Utils
from python_freeipa import ClientMeta
import configparser
import sys
import urllib3

EXIT_TOKENS = ['q', 'exit', 'quit']
PATH_TO_CRED_CFG = "cred.cfg"
LOGGER_NAME = "lab_swipe"

logger = Utils.setup_custom_logger(LOGGER_NAME)

urllib3.disable_warnings()

def main():
    try:
        config = configparser.ConfigParser()
        config.read(PATH_TO_CRED_CFG)
        username = config.get('credentials', 'username')
        password = config.get('credentials', 'password')
    except Exception as e:
        logger.critical("Something is wrong with the credentials config file.")
        logger.exception(e)
        sys.exit(1)

    try:
        client = ClientMeta('citadel.cif.rochester.edu', verify_ssl=False)
        client.login(username, password)
        logger.info(f"Successfuly logged in to Citadel IPA as: {username}")
    except Exception as e:
        logger.critical("Unable to connect to Citadel IPA server. Check credentials.")
        sys.exit(1)
    
    while(True):
        data_from_swipe = input()

        if data_from_swipe.lower() in EXIT_TOKENS:
            break

        swipe = Swipe(data_from_swipe, logger)

        account = Account(swipe, client, logger)

        try:
            if account.has_access:
                logger.info(f"Access granted to {account.netid}")
                Strike.strike()
            else:
                logger.info(f"Denied access to ID: {swipe.id} LCC: {swipe.lcc}")
        except:
            logger.warning(f"Unable to insantiate account from ID: {swipe.id}, LCC: {swipe.lcc}")
    
    logger.info("Exiting...")

if __name__ == "__main__":
    main()
