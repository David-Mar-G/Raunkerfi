import board
import adafruit_tcs34725
from time import sleep

i2c = board.I2C()
sensor = adafruit_tcs34725.TCS34725(i2c)

print("Move the sensor across black -> edge -> white")
print("Press Ctrl+C to stop\n")

while True:
    r, g, b, c = sensor.color_raw

    print(
        f"R={r:4} G={g:4} B={b:4} C={c:4}"
    )

    sleep(0.2)
