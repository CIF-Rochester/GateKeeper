from utils import Utils
import serial
import logging
import time
import serial.tools.list_ports

class Strike():
    def __init__(self, logger: logging.Logger) -> None:
        self.logger = logger
        self.arduino = self.find_arduino()

    def strike(self):
        logger.info("Fake strike activated!")

class ArduinoStrike(Strike):
    def __init__(self, logger: logging.Logger) -> None:
        self.logger = logger
        self.arduino = self.find_arduino()
        
    def find_arduino(self) -> serial.Serial:
        ports = serial.tools.list_ports.comports()
        for port in ports:
            try:
                ser = serial.Serial(port.device, 9600, timeout=1)
                time.sleep(2)  # Allow some time for connection stabilization
                ser.write(b'Q')  # Query the device
                response = ser.readline().decode().strip()
                if response == "Arduino_Online":
                    self.logger.info(f"Arduino found on port {port.device}")
                    return ser
            except Exception as e:
                self.logger.warning(f"Exception: {str(e)}")
                continue  # Go to the next port
        
        self.logger.error("Arduino not found")
        return None  # Return None if Arduino is not found
    
    def strike(self) -> None:
        if self.arduino is not None:  # Check if Arduino is available before sending commands
            try:
                self.arduino.write(b'1')
                #self.logger.info("Strike activated")
            except Exception as e:
                self.logger.error(f"Error striking: {str(e)}")
        else:
            self.logger.warning("Strike not sent; Arduino not available.")

def main():
    # Example usage:
    logger = Utils.setup_custom_logger(__name__)
    strike_controller = ArduinoStrike(logger)
    strike_controller.strike()

if __name__ == "__main__":
    main()