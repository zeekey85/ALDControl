#This will be in a header file, later
import time
import pandas as pd
#import ALD_library_alpha1 as aldLIB
import csv
from pathlib import Path
import numpy as np
import logging
import serial
import asyncio
import nest_asyncio
nest_asyncio.apply()
from alicat import FlowController
from pylablib.devices import Pfeiffer

#testing, delete this sometime.
#setup logger
logging.basicConfig(filename='ALD_runtimeLog.log',level=logging.INFO,format="%(asctime)s %(levelname)-8s %(message)s",datefmt="%m/%d/%Y %I:%M:%S %p")

#ALL VARIABLES DEFINED HERE

#flow_controller_1 = FlowController(address='/dev/ttty.usbserial-FTF5FCCC',unit="B") #Unit read off the front panel
#flow_controller_2 = FlowController(address='/dev/tty.PL2303G-USBtoUART114410',unit="D") #Unit read off the front panel

pressaddr = "/dev/tty.usbmodem114401"
relayaddr = "/dev/tty..."
#Open port for communication with relays borrowed from https://github.com/numato/samplecode/tree/master/RelayAndGPIOModules/USBRelayAndGPIOModules/python/usbrelay1_2_4_8
relayPort = serial.Serial(relayaddr, 19200, timeout=1)


valv2addr = "..."
aldv1addr = "..."
plasmaaddr = "..."


################## DON'T TOUCH ANYTHING BELOW THIS LINE ###################
#Let's write what will eventually be in the library
def fileInput():
    # Prompt the user to enter the file name 
    file_name = input("Please enter the name of the file you want to open: ") 
    try: 
        # Attempt to open the file in read mode 
        with open(file_name, 'r') as file: 
            # Read the content of the file 
            content = file.read() 
    except FileNotFoundError: 
        print(f"The file '{file_name}' does not exist.") 
    except Exception as e: 
        print(f"An error occurred while trying to read the file: {e}") 
    return file_name

async def setMFC(flowcontroller, value):
    if flowcontroller == "Ar":
        await flow_controller_1.set_flow_rate(value)
        logging.info("set mfc at " + flowcontroller + "to " + str(f'{value}'))
        msg = "success! I think."
    elif flowcontroller == "N2":
        await flow_controller_2.set_flow_rate(value)
        logging.info("set mfc at " + flowcontroller + "to " + str(f'{value}'))
        msg = "success! I think."
    else:
        msg = ("Not sure what to do!")
    return msg
    #print("mfc conditons are " + addr.get())
    

def setValve(addr, value):
    if value == 1:
        relayPort.write("relay on"+ " "+ str(addr) + "\n\r")
        logging.info("set valve "+ str(addr)+ "to " str(value))
    elif value == 0:
        relayPort.write("relay off"+ " "+ str(addr) + "\n\r")
        logging.info("set valve "+ str(addr)+ "to " str(value))
    elif value == "close":
        relayPort.close()
        
def setPlasmaPower(addr, power):
    print("set plasma power here")
    
def setPlasmaState(addr, state):
    if state == 1:
        print("send command to turn on")
    else:
        print("send command to turn off")
    
#This function will call the functions above and take an entire line in the CSV file and set the values of everything accordingly
def setVar(line, oldline):
    addresses=np.array([flow_controller_1, flow_controller_2, flow_controller_3, flow_controller_4, plasmaaddr, plasmaaddr, aldv1addr, aldv2addr, aldv3addr, aldv4addr, mfcv1addr, mfcv2addr, mfcv3addr, mfcv4addr])
    for i in range(0,len(addresses),1):
        if line[i] != -1 & line[i] != oldline[i]: #Set value to -1 for cue to ignore
            if i <= 3: #MFCs
                setMFC(addresses[i], line[i])
            elif i >3 & i<=5:
                #plasmas
            elif i <= 14:
                setValve(i+2, line[i])
        else:
            print("here I am")

def readPressure(): #DPG202 USB interface
    print('pressaddr is {}'.format(pressaddr))
    gauge = Pfeiffer.DPG202(pressaddr)
    press = gauge.get_pressure()*.00750062
    gauge.close()
    return(press)

    
def allOff():
    setVar[np.array([0,0,0,0,0,0,0,0,0,0,0,0,0])]
    
#Main lib to run, calling functions defined above
def aldRun(file, loops):
    data = pd.read_csv(file)
    dataNP = data.to_numpy()
    #This is the number of loops the user wants to iterate the current file
    for i in range(loops):
        logging.info(readPressure())
        #For each row in the .csv file, we want to set the experimental parameters accordingly
        for j in range(0,len(dataNP),1):
            if j >> 0: #Sending the current line and previous line for comparison in setVar
                setVar(dataNP[j], dataNP[j-1])
                time.sleep(dataNP[j][14])
            elif j == 0: #sending the first line and the first line changed by a bit to ensure all values are set
                setVar(dataNP[j], dataNP[j]+1)
                
