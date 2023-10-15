from swipe import Swipe
from python_freeipa import ClientMeta
import logging

logging.getLogger().setLevel(logging.INFO)
logging.basicConfig(filename='labswipe.log', encoding='utf-8', level=logging.INFO)

ONE_USER_MATCHED = '1 user matched'

class Account():
    def __init__(self, swipe: Swipe, client: ClientMeta) -> None:
        self.user = client.user_find(o_employeenumber=swipe.id)
        self.summary = self.getSummary()
        self.swiped_lcc = swipe.lcc

        try:
            self.netid = self.getNetID()
            self.lcc = self.getLCC()
            self.groups = self.getGroups()
            self.has_access = self.hasAccess()
        except:
            self.has_access = False

    def getNetID(self):
        return self.user['result'][0]['uid'][0]
    
    def getSummary(self):
        return self.user['summary']
    
    def getLCC(self):
        return self.user['result'][0]['employeetype'][0]
    
    def getGroups(self):
        return self.user['result'][0]['memberof_group']
    
    def hasAccess(self):
        if self.summary != ONE_USER_MATCHED:
            return False

        if 'users' not in self.groups:
            return False
        
        try:
            if int(self.swiped_lcc) < int(self.lcc):
                return False
            elif int(self.swiped_lcc) > int(self.lcc):
                self.updateLCC()
        except:
            logging.warning("LCC String to Int conversion failed. Automatically denying access.")
            return False

        return True
    
    def updateLCC():
        #TODO
        pass
