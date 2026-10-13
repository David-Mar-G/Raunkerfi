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
SUDDEN_CHANGE = 0.40
SPEED = 0.15

stopped = False
previous_voltage = None

try:
    slp.on()

    while True:
        voltage = sensor.value * 3.3

        if previous_voltage is None:
            change = 0
        else:
            change = abs(voltage - previous_voltage)

        print(
            f"Sensor: {voltage:.2f} V   "
            f"Change: {change:.2f} V"
        )

        if stopped:
            mota.stop()
            motb.stop()
            print("LATCHED STOP - restart program to continue")
            sleep(0.2)
            continue

        # Normal ~20 cm detection
        if voltage >= STOP_VOLTAGE:
            mota.stop()
            motb.stop()
            stopped = True
            print("Obstacle near 20 cm - LATCHED STOP")

        # Sudden change detection
        elif previous_voltage is not None and change >= SUDDEN_CHANGE:
            mota.stop()
            motb.stop()
            stopped = True
            print("Sudden obstacle/change detected - LATCHED STOP")

        else:
            mota.forward(SPEED)
            motb.forward(SPEED)

        previous_voltage = voltage
        sleep(0.1)

finally:
    mota.stop()
    motb.stop()
    slp.off()
