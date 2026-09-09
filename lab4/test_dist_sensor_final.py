from gpiozero import MCP3008
from time import sleep

sensor = MCP3008(channel=0)

values = []

for i in range(6):
    voltage = sensor.value * 3.3
    values.append(voltage)

    print(f"Measurement {i + 1}: {voltage:.3f} V")
    sleep(0.5)

mean = sum(values) / len(values)

print(f"Mean: {mean:.3f} V")
