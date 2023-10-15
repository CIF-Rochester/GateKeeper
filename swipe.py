import logging

class Swipe():

    def __init__(self, data: str) -> None:
        self.id, self.lcc = Swipe.parseReader(data)

    def parseReader(data: str):
        try:
            id = data[2:10]
            lcc = data[10:12]
        except:
            logging.warning("Swipe data was not recieved in the correct format.")
            id, lcc = ""
        return id, lcc
    