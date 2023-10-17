import logging

class Swipe():
    """
    Class to represent a "swipe" by parsing an input 
    string and storing the 8 digit ID and 2 digit LCC.
    """

    def __init__(self, data: str, logger: logging.Logger) -> None:
        self.data = data
        self.logger = logger
        self.id, self.lcc = self.parse_reader()

    def parse_reader(self) -> (str, str):
        """
        Parses the raw data from the swipe to obtain the
        8 digit ID and LCC. Returns both as empty strings 
        if the data was in an incorrect format.
        """
        
        try:
            id = self.data[2:10]
            lcc = self.data[10:12]
        except:
            self.logger.warning(f"Swipe data was not recieved in the correct format: {self.data}")
            id, lcc = ""
        return id, lcc
    