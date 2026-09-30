from gpiozero import Motor, DigitalOutputDevice, RotaryEncoder
from time import sleep

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

enca = RotaryEncoder('GPIO25', 'GPIO20', max_steps=0)
encb = RotaryEncoder('GPIO26', 'GPIO5', max_steps=0)

COUNTS_PER_REV_A = 694
COUNTS_PER_REV_B = 695

MEASURE_TIME = 3.0

try:
    slp.on()

    mota.forward(0.5)
    motb.forward(0.5)

    # Let motors reach a steady speed
    sleep(1)

    start_a = enca.steps
    start_b = encb.steps

    sleep(MEASURE_TIME)

    end_a = enca.steps
    end_b = encb.steps

    mota.stop()
    motb.stop()

    delta_a = abs(end_a - start_a)
    delta_b = abs(end_b - start_b)

    speed_a = (delta_a / COUNTS_PER_REV_A) / MEASURE_TIME
    speed_b = (delta_b / COUNTS_PER_REV_B) / MEASURE_TIME

    print(f"MOTA count change: {delta_a}")
    print(f"MOTA speed: {speed_a:.2f} rev/s")

    print(f"MOTB count change: {delta_b}")
    print(f"MOTB speed: {speed_b:.2f} rev/s")

finally:
    mota.stop()
    motb.stop()
    slp.off()
