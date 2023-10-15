class Swipe():

    def __init__(self, data: str, logger) -> None:
        self.data = data
        self.logger = logger
        self.id, self.lcc = self.parseReader()

    def parseReader(self):
        try:
            id = self.data[2:10]
            lcc = self.data[10:12]
        except:
            self.logger.warning(f"Swipe data was not recieved in the correct format: {self.data}")
            id, lcc = ""
        return id, lcc
    