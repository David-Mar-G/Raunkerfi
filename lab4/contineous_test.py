from gpiozero import MCP3008
from time import sleep

sensor = MCP3008(channel=0)

while True:
    voltage = sensor.value * 3.3
    print(f"Voltage: {voltage:.3f} V")
    sleep(0.2)
