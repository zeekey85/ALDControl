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
import matplotlib.pyplot as plt

#setup logger
logging.basicConfig(filename='ALD_runtimeLog.log',level=logging.INFO,format="%(asctime)s %(levelname)-8s %(message)s",datefmt="%m/%d/%Y %I:%M:%S %p")
logging.info("Starting a new run")
#ALL VARIABLES DEFINED HERE

fc1 ='/dev/serial/by-id/usb-FTDI_FT232R_USB_UART_B001OROI-if00-port0' #Ar unit B
fc2 ='/dev/serial/by-id/usb-FTDI_FT232R_USB_UART_B001OROU-if00-port0' #N2 unit D
fc3 = '/dev/serial/by-id/usb-FTDI_FT232R_USB_UART_B001OROR-if00-port0' #Ar unit C MO line

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
    elif flowcontroller == "ArMo":
        async with FlowController(address=fc3, unit="C") as flow_controller:
            await flow_controller.set_flow_rate(value)
        logging.info("set mfc at " + str(f'{flowcontroller}') + "to " + str(f'{value}'))
        msg = "success! I think."

    else:
        msg = ("Not sure what to do!")
        print(msg)
    return msg
    #print("mfc conditonsArMo  are " + addr.get())
    

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
    addresses=["Ar","N2","ArMo","H2","plasmaaddr","plasmastate","",2,3,"",1,"","",""] #String inputs expected by each function for MFC, plasma, relay/solenoid controller
    for i in range(len(line)):
        if int(line[i]) == -1:#Set value to -1 for cue to ignore
            print('the value should be -1, and is {}'.format(line[i]))
        elif line[i] != oldline[i]: #only run this if the new line is not equal to the old line
            if i <= 3: #MFCs
                asyncio.get_event_loop().run_until_complete(setMFC(addresses[i], int(line[i])))           
            elif 3 < i <=5:
                logging.info("plasma")
            elif 5 < i < 10:#ALD valve operation does the sleep in here to get the timing right
                setValve(addresses[i], int(line[i]))
                time.sleep(line[14])
                setValve(addresses[i], 0)
            elif 10 <= i < 14:
                setValve(addresses[i], line[14]) #This is for the MFC protection valves only. May want to just open those manually at the start, and leave the recipe file as all -1's here. 
                 
                
        else:
            print('line[{}] is: {} and oldline[{}] is {}'.format(i,line[i],i,oldline[i]))

def readPressure(): #DPG202 USB interface
    gauge = Pfeiffer.DPG202(pressaddr)
    press = gauge.get_pressure()*.00750062
    logging.info("The pressure is " + str(press))
    gauge.close()
    return(press)
 
#Main lib to run, calling functions defined above
def aldRun(file, loops):
    data = pd.read_csv(file)
    dataNP = data.to_numpy()
    print(dataNP)
    t_start=time.time()
    pressure = np.array([readPressure])
    t_array = np.array([time.time()])
    #This is the number of loops the user wants to iterate the current file
    for i in range(loops):
        #For each row in the .csv file, we want to set the experimental parameters accordingly
        for j in range(0,len(dataNP),1):
            #np.append(pressure,readPressure)
            #np.append(t_array, time.time())
            #plt.plot(t_array,pressure)
            #plt.show()
            if j >> 0: #Sending the current line and previous line for comparison in setVar
                setVar(dataNP[j], dataNP[j-1])
                logging.info('going to sleep for {} seconds'.format(dataNP[j][14]))
                time.sleep(dataNP[j][14]) #I had to move the sleep for the ALD pulses into the setVar, so we have a redundant sleep here on recipe lines where the ald valves cycle. But, this one happens after the ald valve opens and closes, so it shouldn't be a big deal.
            elif j == 0: #sending the first line and the first line changed by a bit to ensure all values are set
                #print('for j = 0, I am sending over {} and {}'.format(dataNP[j], dataNP[j]+1))
                setVar(dataNP[j], dataNP[j]+1)
                
