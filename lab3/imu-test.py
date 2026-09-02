import board
import adafruit_icm20x

i2c = board.I2C()

imu = adafruit_icm20x.ICM20948(i2c, address=0x68)

print("Acceleration:", imu.acceleration)
print("Gyroscope:", imu.gyro)
print("Magnetometer:", imu.magnetic)
