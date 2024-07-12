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

#setup logger
logging.basicConfig(filename='ALD_runtimeLog.log',level=logging.INFO,format="%(asctime)s %(levelname)-8s %(message)s",datefmt="%m/%d/%Y %I:%M:%S %p")
logging.info("Starting a new run")
#ALL VARIABLES DEFINED HERE

fc1 ='/dev/serial/by-id/usb-FTDI_FT232R_USB_UART_B001OROI-if00-port0' #Ar
fc2 ='/dev/serial/by-id/usb-FTDI_FT232R_USB_UART_B001OROM-if00-port0'
fc3 = '/dev/serial/by-id/usb-FTDI_FT232R_USB_UART_B001ORON-if00-port0'

pressaddr = "/dev/serial/by-id/usb-Pfeiffer_Vacuum_DPG202-if00"
relayaddr = "/dev/serial/by-id/usb-Numato_Systems_Pvt._Ltd._Numato_Lab_8_Channel_USB_Relay_Module_NLRL220216A0258-if00"
#Open port for communication with relays borrowed from https://github.com/numato/samplecode/tree/master/RelayAndGPIOModules/USBRelayAndGPIOModules/python/usbrelay1_2_4_8
relayPort = serial.Serial(relayaddr, 19200, timeout=1)



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
        async with FlowController(address=fc1, unit="B") as flow_controller:
            await flow_controller.set_flow_rate(value)
        logging.info("set mfc at " + str(f'{flowcontroller}') + "to " + str(f'{value}'))
        msg = "success! I think."
    elif flowcontroller == "N2":
        async with FlowController(address=fc2, unit="D") as flow_controller:
            await flow_controller.set_flow_rate(value)
        logging.info("set mfc at " + str(f'{flowcontroller}') + "to " + str(f'{value}'))
        msg = "success! I think."
    elif flowcontroller == "ArP":
        async with FlorController(address=fc3, unit="B") as flow_controller:
            await flow_controller.set_flow_rate(value)
        logging.info("set mfc at " + str(f'{flowcontroller}') + "to " + str(f'{value}'))
        msg = "success! I think."
    else:
        msg = ("Not sure what to do!")
    return msg
    #print("mfc conditons are " + addr.get())
    

def setValve(addr, value):
    if value == 1:
        relayPort.write(("relay on"+ " "+ str(addr) + "\n\r").encode())
        logging.info("set valve "+ str(f'{addr}')+ "to " + str(f'{value}'))
    elif value == 0:
        relayPort.write(("relay off"+ " "+ str(addr) + "\n\r").encode())
        logging.info("set valve "+ str(addr)+ "to "  + str(value))
    elif value == "close":
        relayPort.close()

def getValve():
    for i in range(0,9,1):
        relayPort.write(("relay read " + str(i) + "\n\r").encode())
        response = relayPort.read(25)
        if str(response).find("on")>0:
            print("relay "+str(i)+" is on")
        elif str(response).find("off")>0:
            print("relay"+str(i)+" is off")
        else:
            print(response)

def closeValve():
    for i in range(0,9,1):
        relayPort.write(("relay off "+str(i)+"\n\r").encode())

        
def setPlasmaPower(addr, power):
    print("set plasma power here")
    
def setPlasmaState(addr, state):
    if state == 1:
        print("send command to turn on")
    else:
        print("send command to turn off")
    
#This function will call the functions above and take an entire line in the CSV file and set the values of everything accordingly
def setVar(line, oldline):
    #addresses=np.array([flow_controller_1, flow_controller_2, flow_controller_3, flow_controller_4, plasmaaddr, plasmaaddr, aldv1addr, aldv2addr, aldv3addr, aldv4addr, mfcv1addr, mfcv2addr, mfcv3addr, mfcv4addr])
    for i in range(0,14,1):
        print(str(line[i])+","+str(oldline[i]))
        if line[i] != -1 and line[i] != oldline[i]: #Set value to -1 for cue to ignore
            if i <= 3: #MFCs
                setMFC(addresses[i], line[i])
            elif i >> 3 and i<=5:
                print("plasma")
            elif i <= 14:
                setValve(i-5, line[i])
                print("made it to setvalve!")
        else:
            print("here I am"+str(i))

def readPressure(): #DPG202 USB interface
    gauge = Pfeiffer.DPG202(pressaddr)
    press = gauge.get_pressure()*.00750062
    logging.info("The pressure is " + str(press))
    gauge.close()
    return(press)

    
def allOff():
    setVar[np.array([0,0,0,0,0,0,0,0,0,0,0,0,0])]
    
#Main lib to run, calling functions defined above
def aldRun(file, loops):
    data = pd.read_csv(file)
    dataNP = data.to_numpy()
    print(dataNP)
    #This is the number of loops the user wants to iterate the current file
    for i in range(loops):
        logging.info(readPressure())
        #For each row in the .csv file, we want to set the experimental parameters accordingly
        for j in range(0,len(dataNP),1):
            if j >= 0: #Sending the current line and previous line for comparison in setVar
                setVar(dataNP[j], dataNP[j-1])
                time.sleep(dataNP[j][13])
            elif j == 0: #sending the first line and the first line changed by a bit to ensure all values are set
                setVar(dataNP[j], dataNP[j]+1)
                
