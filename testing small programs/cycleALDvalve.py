#TestALDValve
import time
import serial
relayaddr = "/dev/serial/by-id/usb-Numato_Systems_Pvt._Ltd._Numato_Lab_8_Channel_USB_Relay_Module_NLRL220216A0258-if00"
#Open port for communication with relays borrowed from https://github.com/numato/samplecode/tree/master/RelayAndGPIOModules/USBRelayAndGPIOModules/python/usbrelay1_2_4_8
relayPort = serial.Serial(relayaddr, 19200, timeout=1)
addr=1

for i in range(0, 5, 1):
	relayPort.write(("relay on"+ " "+ str(addr) + "\n\r").encode())
	print("open")
	time.sleep(.05)
	relayPort.write(("relay off"+ " "+ str(addr) + "\n\r").encode())
	print("close")
	time.sleep(5)
