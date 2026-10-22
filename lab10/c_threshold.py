import board
import adafruit_tcs34725
from time import sleep

i2c = board.I2C()
sensor = adafruit_tcs34725.TCS34725(i2c)

print("TCS34725 black/white test")
print("Press Ctrl+C to stop\n")

while True:
    r, g, b, c = sensor.color_raw

    print(
        f"R={r:5}  G={g:5}  B={b:5}  C={c:5}"
    )

    sleep(0.2)
