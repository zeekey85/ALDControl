import asyncio
from alicat import FlowController
fc3 = '/dev/serial/by-id/usb-FTDI_FT232R_USB_UART_B001OROR-if00-port0'
async def set():
	async with FlowController(address=fc3, unit="C") as flow_controller:
		print(await flow_controller.set_flow_rate(30))
		
asyncio.run(set())

