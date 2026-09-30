from gpiozero import Motor, DigitalOutputDevice, RotaryEncoder
from simple_pid import PID
from time import sleep, monotonic

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

TARGET_SPEED = 2.0

BASE_POWER = 0.30

KP = 0.10
KI = 0.05
KD = 0.0

pid_a = PID(KP, KI, KD, setpoint=TARGET_SPEED)
pid_b = PID(KP, KI, KD, setpoint=TARGET_SPEED)

# PID only makes small corrections
pid_a.output_limits = (-0.20, 0.20)
pid_b.output_limits = (-0.20, 0.20)

SAMPLE_TIME = 0.5

try:
    slp.on()

    # Start motors before measuring
    mota.forward(BASE_POWER)
    motb.forward(BASE_POWER)

    sleep(1)

    last_a = enca.steps
    last_b = encb.steps
    last_time = monotonic()

    for _ in range(30):
        sleep(SAMPLE_TIME)

        now = monotonic()
        dt = now - last_time

        current_a = enca.steps
        current_b = encb.steps

        delta_a = abs(current_a - last_a)
        delta_b = abs(current_b - last_b)

        speed_a = (delta_a / COUNTS_PER_REV_A) / dt
        speed_b = (delta_b / COUNTS_PER_REV_B) / dt

        correction_a = pid_a(speed_a)
        correction_b = pid_b(speed_b)

        power_a = BASE_POWER + correction_a
        power_b = BASE_POWER + correction_b

        power_a = max(0, min(1, power_a))
        power_b = max(0, min(1, power_b))

        mota.forward(power_a)
        motb.forward(power_b)

        print(
            f"MOTA: {speed_a:.2f} rev/s, power={power_a:.2f} | "
            f"MOTB: {speed_b:.2f} rev/s, power={power_b:.2f}"
        )

        last_a = current_a
        last_b = current_b
        last_time = now

finally:
    mota.stop()
    motb.stop()
    slp.off()
