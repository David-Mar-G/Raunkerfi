from gpiozero import Motor, DigitalOutputDevice, MCP3008
from time import sleep

# Motor driver enable
slp = DigitalOutputDevice('GPIO17')

# Motors
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

# Distance sensor through MCP3008 CH0
sensor = MCP3008(channel=0)

STOP_VOLTAGE = 2.35
SPEED = 0.30

stopped = False

try:
    slp.on()

    while True:
        voltage = sensor.value * 3.3

        print(f"Sensor: {voltage:.2f} V")

        # Once stopped, remain stopped
        if stopped:
            mota.stop()
            motb.stop()
            print("LATCHED STOP - restart program to continue")
            sleep(0.2)
            continue

        # Normal collision detection
        if voltage >= STOP_VOLTAGE:
            mota.stop()
            motb.stop()

            stopped = True

            print("Obstacle detected - LATCHED STOP")

        else:
            mota.forward(SPEED)
            motb.forward(SPEED)

        sleep(0.1)

finally:
    mota.stop()
    motb.stop()
    slp.off()
