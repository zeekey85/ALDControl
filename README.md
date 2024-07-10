# ALDControl
Repo for ALD control custom hardware with Python

10July2024
-Basic Usage instructions for manual actuation of MFCs, valves, etc. Still haven’t tested recipe running, though I think it’s basically ready:
->In the zakjeffALDlibrary.py header, enter the address to each device connected to the control system. On my mac, they are in /dev/tty.XYZ
->Run the program by navigating to the proper folder in a terminal, and typing ‘python mainprogram.py’ this will start a new log in the .log file.
->’done’ will terminate the program operation
->’setMFC’ will ask questions, and then set the MFC
->’setValve’ will allow you to open or close one of the relays. Will update this once I get those hardwired, but for now: Relay 0 = MFC isolation relays, Relay 1 = ALD precursor 1 (leftmost)
->’getP’ will log the pressure, and print it to the terminal
-> Plasma settings are not yet available. I think it might be an issue with the Mac, so I need to get this all setup with the Raspberry Pi to see if I can control things that way. 

28June2024
- Added the setValve function, which should work now once I get the relay card from Numato lab.

26June2024 Currently, the following seems to be working:
- Read pressure from Pfeiffer gauge
- setMFC state
- Read in a recipe file (though some of the required functions to actually execute the recipe are still in progress)

Other updates:
- The valve actuation is waiting for arrival of the relay card (https://numato.com/docs/8-channel-usb-relay-module/)
- The plasma controller *should* be working, see the Jupyter notebook with the test functions. It was returning some weird and unexpected strings, and appears buggy. Need to investigate.
