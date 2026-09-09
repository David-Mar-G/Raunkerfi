from gpiozero import MCP3008
from time import sleep

sensor = MCP3008(channel=0)   # CH0, matching where your sensor's yellow wire lands

while True:
    v = sensor.value * 3.3
    print(f"raw: {sensor.value:.3f}   voltage: {v:.2f} V")
    sleep(0.3)
