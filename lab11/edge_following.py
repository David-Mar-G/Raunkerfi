
import time
import board
import adafruit_tcs34725
from gpiozero import Motor, DigitalOutputDevice

# =====================================
# SENSOR
# =====================================

sensor = adafruit_tcs34725.TCS34725(board.I2C())
sensor.integration_time = 12
sensor.gain = 4

THRESHOLD = 900

# =====================================
# MOTORS
# =====================================

slp = DigitalOutputDevice("GPIO17")

# Right wheel
mota = Motor(
    forward="GPIO12",
    backward="GPIO18",
    pwm=True
)

# Left wheel
motb = Motor(
    forward="GPIO19",
    backward="GPIO13",
    pwm=True
)

# =====================================
# SPEED
# =====================================

SPEED = 0.14

# NEW: Slight reverse on right wheel
RIGHT_REVERSE_SPEED = 0.06

# =====================================
# MAIN
# =====================================

try:
    slp.on()

    print("RIGHT EDGE FOLLOWER - STRONGER RIGHT TURN")
    print("Starting in 2 seconds...")
    time.sleep(2)

    while True:

        r, g, b, clear = sensor.color_raw

        if clear < THRESHOLD:
            # BLACK -> STRONGER RIGHT TURN
            mota.backward(RIGHT_REVERSE_SPEED)
            motb.forward(SPEED)

        else:
            # WHITE -> NORMAL LEFT TURN
            mota.forward(SPEED)
            motb.stop()

        print(f"C={clear}")

except KeyboardInterrupt:
    print("Stopping")

finally:
    mota.stop()
    motb.stop()
    slp.off()

