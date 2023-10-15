from swipe import Swipe
from account import Account
from strike import Strike
from python_freeipa import ClientMeta
import configparser
import logging
import sys
import urllib3

urllib3.disable_warnings()

logging.getLogger().setLevel(logging.INFO)
logging.basicConfig(filename='labswipe.log', encoding='utf-8', level=logging.INFO)

EXIT_TOKENS = ['q', 'exit', 'quit']
PATH_TO_CRED_CFG = "cred.cfg"

def main():
    try:
        config = configparser.ConfigParser()
        config.read(PATH_TO_CRED_CFG)
        username = config.get('credentials', 'username')
        password = config.get('credentials', 'password')

        client = ClientMeta('citadel.cif.rochester.edu', verify_ssl=False)
        client.login(username, password)
    except:
        logging.critical("Unable to connect to Citadel IPA server. Check credentials.")
        sys.exit(1)
    
    while(True):
        data_from_swipe = input()

        if data_from_swipe.lower() in EXIT_TOKENS:
            break

        swipe = Swipe(data_from_swipe)

        account = Account(swipe, client)

        try:
            if account.has_access:
                logging.info(f"Access granted to {account.netid}")
                Strike.strike()
            else:
                logging.info(f"Denied access to ID: {swipe.id} LCC: {swipe.lcc}")
        except:
            logging.warning(f"Unable to insantiate account from ID: {swipe.id}, LCC: {swipe.lcc}")
    
    logging.info("Exiting...")

if __name__ == "__main__":
    main()
