from utils import Utils
import serial
import logging
import time
import serial.tools.list_ports

class Strike():
    """
    Parent class for ArduinoStrike and RasPiStrike. Used for testing purposes as well.
    """
    
    def __init__(self, logger: logging.Logger) -> None:
        self.logger = logger

    def strike(self):
        """
        Strike function for testing purposes.
        """
        
        self.logger.info("Fake strike activated!")

class RasPiStrike(Strike):
    """
    Class implementation of striking the door using the Raspberry Pi's pins.
    """

    channel = 1
    
    def __init__(self, logger: logging.Logger) -> None:
        import RPi.GPIO as GPIO

        self.logger = logger
        self.GPIO = GPIO
        self.GPIO.setmode(GPIO.Board)
        self.GPIO.setup(self.channel,GPIO.OUT)
        
    
    def strike(self):
        """
        Implementation of striking the door using the Raspberry Pi's pins.
        """
        self.logger.info("RasPi Striking!")
        self.GPIO.output(self.channel,self.GPIO.HIGH)
        time.sleep(5.0)
        self.GPIO.output(self.channel,self.GPIO.LOW)

class ArduinoStrike(Strike):
    """
    Class implementation of striking the door using an Arduino.
    """

    def __init__(self, logger: logging.Logger) -> None:
        self.logger = logger
        self.arduino = self.find_arduino()
        
    def find_arduino(self) -> serial.Serial:
        """
        Find the Arduino's serial connection by testing 
        all serial connections until the Arduino is found. 
        """
        
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
        return None
    
    def strike(self) -> None:
        """
        Implementation of striking the door using the Arduino.
        """

        if self.arduino is not None:
            try:
                self.arduino.write(b'1')
            except Exception as e:
                self.logger.error(f"Error striking: {str(e)}")
        else:
            self.logger.warning("Strike not sent; Arduino not available.")

def main():
    # Testing
    logger = Utils.setup_custom_logger(__name__)
    strike_controller = ArduinoStrike(logger)
    strike_controller.strike()

if __name__ == "__main__":
    main()