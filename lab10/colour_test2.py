import board
import adafruit_tcs34725
from time import sleep

i2c = board.I2C()
sensor = adafruit_tcs34725.TCS34725(i2c)

sensor.integration_time = 12
sensor.gain = 4

print("Move the sensor across black -> edge -> white")
print("Press Ctrl+C to stop\n")

while True:
    r, g, b, c = sensor.color_raw

    print(
        f"R={r:5} G={g:5} B={b:5} C={c:5}"
    )

    sleep(0.1)
