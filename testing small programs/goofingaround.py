import numpy as np
import time
from pylablib.devices import Pfeiffer
import serial
import matplotlib.pyplot as plt

pressaddr = "/dev/serial/by-id/usb-Pfeiffer_Vacuum_DPG202-if00"
gauge = Pfeiffer.DPG202(pressaddr)

t_start=time.time()
pressure = np.array([gauge.get_pressure()*.00750062])
t_array = np.array([time.time()-t_start])

def readPressure(): #DPG202 USB interface
    gauge = Pfeiffer.DPG202(pressaddr)
    press = gauge.get_pressure()*.00750062
    gauge.close()
    return(press)


for i in range(0,20,1):
	pressure = np.append(pressure, readPressure())
	t_array = np.append(t_array, time.time()-t_start)
	time.sleep(.2)
	
print(pressure)
print(t_array)

plt.plot(t_array, pressure)
plt.show()

gauge.close()
