# GateKeeper
Lab Card Reader Program for CIF Lab. Updated 2023.

This repository is intended to permanently replace the previously used Cerberus system.

# Quick Start
- install Python 3.11.4
- run `python3 -m pip install -r requirements.txt`
- fill out the `cred.cfg` file with your credentials
- run `python3 main.py`

# Info
- So far, the only code written is for interfacing with the card reader and the IPA server.
- No code has been written for dealing with the actual door strike.
- The name `GateKeeper` subject to change. Think of it as a codename for the time being.

# Classes
### Account
- For getting the info from an IPA user, such as netid.
- Also has a function `hasAccess()` to determine if the user should, based on their IPA account credentials, be allowed to swipe into the lab.

### Strike
- For controlling the door strike.
- Not implemented yet.

### Swipe
- For parsing the raw data from the swipe.
- Stores 8 digit ID number and 2 digit LCC number.
- expects data as sent by the MODEL:ET-MSR90 ETEKJOY card reader. Example data: `;9333333331108700000?\n`
- The format is `;9<8ID><2LCC><Garbage><New Line>`. In the example, `33333333` is the `8` digit ID and 11 is the 2 digit LCC.

### Utils
- For various utilities.
- Right now, just used for making the logger.