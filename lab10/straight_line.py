import board
import adafruit_tcs34725
from gpiozero import Motor, DigitalOutputDevice
from time import sleep

i2c = board.I2C()
sensor = adafruit_tcs34725.TCS34725(i2c)

slp = DigitalOutputDevice('GPIO17')

mota = Motor(
    forward='GPIO12',
    backward='GPIO18',
    pwm=True
)

motb = Motor(
    forward='GPIO19',
    backward='GPIO13',
    pwm=True
)

THRESHOLD = 50
SPEED = 0.20

try:
    slp.on()

    while True:
        r, g, b, c = sensor.color_raw

        if c < THRESHOLD:
            print(f"C={c} BLACK -> forward")
            mota.forward(SPEED)
            motb.forward(SPEED)

        else:
            print(f"C={c} WHITE -> stop")
            mota.stop()
            motb.stop()

        sleep(0.05)

finally:
    mota.stop()
    motb.stop()
    slp.off()
