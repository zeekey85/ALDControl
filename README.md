# ALDControl
Repo for ALD control custom hardware with Python

28June2024
- Added the setValve function, which should work now once I get the relay card from Numato lab.

26June2024 Currently, the following seems to be working:
- Read pressure from Pfeiffer gauge
- setMFC state
- Read in a recipe file (though some of the required functions to actually execute the recipe are still in progress)

Other updates:
- The valve actuation is waiting for arrival of the relay card (https://numato.com/docs/8-channel-usb-relay-module/)
- The plasma controller *should* be working, see the Jupyter notebook with the test functions. It was returning some weird and unexpected strings, and appears buggy. Need to investigate.
