from gpiozero import Motor, DigitalOutputDevice, RotaryEncoder
from simple_pid import PID
from time import sleep, monotonic

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

# Encoders
enca = RotaryEncoder('GPIO25', 'GPIO20', max_steps=0)
encb = RotaryEncoder('GPIO26', 'GPIO5', max_steps=0)

COUNTS_PER_REV_A = 694
COUNTS_PER_REV_B = 695

TARGET_SPEED = 2.0     # revolutions per second

# Start with proportional control only
KP = 0.2
KI = 0.0
KD = 0.0

pid_a = PID(KP, KI, KD, setpoint=TARGET_SPEED)
pid_b = PID(KP, KI, KD, setpoint=TARGET_SPEED)

# Motor command must stay between 0 and 1
pid_a.output_limits = (0, 1)
pid_b.output_limits = (0, 1)

SAMPLE_TIME = 0.2

try:
    slp.on()

    last_a = enca.steps
    last_b = encb.steps
    last_time = monotonic()

    for _ in range(50):      # about 10 seconds
        sleep(SAMPLE_TIME)

        now = monotonic()
        dt = now - last_time

        current_a = enca.steps
        current_b = encb.steps

        delta_a = abs(current_a - last_a)
        delta_b = abs(current_b - last_b)

        speed_a = (delta_a / COUNTS_PER_REV_A) / dt
        speed_b = (delta_b / COUNTS_PER_REV_B) / dt

        power_a = pid_a(speed_a)
        power_b = pid_b(speed_b)

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
