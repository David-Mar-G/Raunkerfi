import time
import math
import board
import adafruit_icm20x

i2c = board.I2C()
imu = adafruit_icm20x.ICM20948(i2c, address=0x68)

while True:
    x, y, z = imu.magnetic

    heading = math.degrees(math.atan2(y, x))
    heading = (heading + 360) % 360

    print("Heading:", round(heading, 1))
    time.sleep(0.5)
