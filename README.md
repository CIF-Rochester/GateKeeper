# GateKeeper
Lab Card Reader Program for CIF Lab. Updated 2023.

This repository is intended to permanently replace the previously used Cerberus system.

# Quick Start
- install Python >= 3.8
- **(Recommended)** Create a virtual environment with `python3 -m venv .venv` and activate it with `source .venv/bin/activate`
- run `python3 -m pip install -r requirements.txt`
- copy `config.example.cfg` to `config.cfg` and adjust the configuration
- run `python3 main.py`

# Info
- The name `GateKeeper` subject to change. Think of it as a codename for the time being.

# Command Line Arguments
```
usage: main.py [-h] [--strike {fake,arduino,pi}] [--config CONFIG]

GateKeeper program for controlling an electronic door strike with a card
reader.

options:
  -h, --help            show this help message and exit
  --strike {fake,arduino,pi}, -s {fake,arduino,pi}
                        Method used for controlling the door strike. Fake is
                        used for testing purposes.
  --config CONFIG, -c CONFIG
                        Path to GateKeeper config file.
```

# Classes
### Account
- For getting the info from an IPA user, such as netid.
- Also has a function `hasAccess()` to determine if the user should, based on their IPA account credentials, be allowed to swipe into the lab.

### Strike
- For controlling the door strike.
- Contains three classes: `Strike`, `ArduinoStrike`, `RasPiStrike`.
- `Strike` is for testing purposes, it doesn't send any electrical signals.
- `ArduinoStrike` is for activating the strike with the arduino.
- `RasPiStrike` is for activating the strike with the GPIO pins of a Raspberry Pi.

### Swipe
- For parsing the raw data from the swipe.
- Stores 8 digit ID number and 2 digit LCC number.
- expects data as sent by the MODEL:ET-MSR90 ETEKJOY card reader. Example data: `;9333333331108700000?\n`
- The format is `;9<8ID><2LCC><Garbage><New Line>`. In the example, `33333333` is the 8 digit ID and `11` is the 2 digit LCC.

### Utils
- For various utilities.
- Right now, just used for making the logger and the `exit()` function
