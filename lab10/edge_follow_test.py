import time
import board
import adafruit_tcs34725

from gpiozero import Motor, DigitalOutputDevice


# ============================================================
# SETTINGS
# ============================================================

# Measured clear-channel values:
# black centre ≈ 8
# white        ≈ 93-103
#
# We follow the RIGHT edge of the black line.

TARGET_C = 78

BASE_SPEED = 0.10

# Proportional steering strength
KP = 0.0010

MIN_SPEED = 0.08
MAX_SPEED = 0.115

# Consider the line lost when the reading is clearly white
LOST_C = 92

LOOP_DELAY = 0.02


# ============================================================
# HARDWARE
# ============================================================

slp = DigitalOutputDevice('GPIO17')

# MOTA = right wheel
right = Motor(
    forward='GPIO12',
    backward='GPIO18',
    pwm=True
)

# MOTB = left wheel
left = Motor(
    forward='GPIO19',
    backward='GPIO13',
    pwm=True
)


# ============================================================
# TCS34725
# ============================================================

i2c = board.I2C()
sensor = adafruit_tcs34725.TCS34725(i2c)


def get_clear():
    return sensor.color_raw[3]


# ============================================================
# MOTOR CONTROL
# ============================================================

def clamp(value, minimum, maximum):
    return max(minimum, min(maximum, value))


def drive(left_speed, right_speed):
    left_speed = clamp(left_speed, 0, MAX_SPEED)
    right_speed = clamp(right_speed, 0, MAX_SPEED)

    if left_speed > 0:
        left.forward(left_speed)
    else:
        left.stop()

    if right_speed > 0:
        right.forward(right_speed)
    else:
        right.stop()


def stop():
    left.stop()
    right.stop()


# ============================================================
# MAIN
# ============================================================

try:
    slp.on()

    print("Proportional line follower")
    print(f"Target C = {TARGET_C}")
    print("Ctrl+C to stop")

    while True:
        c = get_clear()

        # ----------------------------------------------------
        # LINE LOST
        # ----------------------------------------------------

        if c >= LOST_C:

            # White detected.
            # Because we are following the RIGHT edge,
            # assume the black line is to the LEFT.

            left_speed = MIN_SPEED
            right_speed = MAX_SPEED

            drive(left_speed, right_speed)

            print(
                f"C={c:3d} LOST  "
                f"L={left_speed:.3f} "
                f"R={right_speed:.3f}"
            )

        # ----------------------------------------------------
        # PROPORTIONAL EDGE FOLLOWING
        # ----------------------------------------------------

        else:
            error = c - TARGET_C
            correction = KP * error

            # C too high -> too white -> steer LEFT
            # C too low  -> too black -> steer RIGHT

            left_speed = BASE_SPEED - correction
            right_speed = BASE_SPEED + correction

            left_speed = clamp(
                left_speed,
                MIN_SPEED,
                MAX_SPEED
            )

            right_speed = clamp(
                right_speed,
                MIN_SPEED,
                MAX_SPEED
            )

            drive(left_speed, right_speed)

            print(
                f"C={c:3d} "
                f"err={error:+3d} "
                f"L={left_speed:.3f} "
                f"R={right_speed:.3f}"
            )

        time.sleep(LOOP_DELAY)


except KeyboardInterrupt:
    print("\nStopped")


finally:
    stop()
    slp.off()
    print("Motors stopped")
