import time
import board
import adafruit_tcs34725

from gpiozero import Motor, DigitalOutputDevice


# ============================================================
# SETTINGS
# ============================================================

# Measured with:
# integration_time = 50 ms
# gain = 4
#
# black ≈ 180-300
# white ≈ 6500-7400

CLEAR_THRESHOLD = 3000

# Enough power so the motors do not stall
MOTOR_POWER = 0.14

# Slow movement pulses
FORWARD_TIME = 0.05

TURN_SMALL = 0.02
TURN_BIG = 0.04

BACK_TIME = 0.03

PAUSE_TIME = 0.02


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
# SENSOR
# ============================================================

i2c = board.I2C()
sensor = adafruit_tcs34725.TCS34725(i2c)

# Same settings used during calibration
sensor.integration_time = 50
sensor.gain = 4


def get_clear():
    return sensor.color_raw[3]


# ============================================================
# MOTOR FUNCTIONS
# ============================================================

def stop():
    left.stop()
    right.stop()


def forward_step():
    left.forward(MOTOR_POWER)
    right.forward(MOTOR_POWER)

    time.sleep(FORWARD_TIME)

    stop()
    time.sleep(PAUSE_TIME)


def left_step(duration):
    # Left wheel stops, right wheel moves
    left.stop()
    right.forward(MOTOR_POWER)

    time.sleep(duration)

    stop()
    time.sleep(PAUSE_TIME)


def right_step(duration):
    # Right wheel stops, left wheel moves
    left.forward(MOTOR_POWER)
    right.stop()

    time.sleep(duration)

    stop()
    time.sleep(PAUSE_TIME)


def back_step():
    left.backward(MOTOR_POWER)
    right.backward(MOTOR_POWER)

    time.sleep(BACK_TIME)

    stop()
    time.sleep(PAUSE_TIME)


def line_found():
    c = get_clear()

    print(f"Check C={c}")

    return c < CLEAR_THRESHOLD


# ============================================================
# MAIN
# ============================================================

try:
    slp.on()

    print("Slow line follower")
    print(f"Threshold = {CLEAR_THRESHOLD}")
    print("Ctrl+C to stop")

    while True:

        c = get_clear()

        print(f"C={c}")

        # ====================================================
        # BLACK -> FORWARD
        # ====================================================

        if c < CLEAR_THRESHOLD:

            print("BLACK -> FORWARD")

            forward_step()


        # ====================================================
        # WHITE -> SEARCH
        # ====================================================

        else:

            print("WHITE -> SEARCH")

            stop()

            found = False


            # -----------------------------------------------
            # 1. SMALL LEFT SEARCH
            # -----------------------------------------------

            print("SEARCH LEFT - SMALL")

            left_step(TURN_SMALL)

            if line_found():
                print("BLACK FOUND")
                found = True


            # -----------------------------------------------
            # 2. SMALL RIGHT SEARCH
            # -----------------------------------------------

            if not found:

                print("SEARCH RIGHT - SMALL")

                right_step(TURN_SMALL * 2)

                if line_found():
                    print("BLACK FOUND")
                    found = True


            # -----------------------------------------------
            # 3. WIDER LEFT SEARCH
            # -----------------------------------------------

            if not found:

                print("SEARCH LEFT - WIDE")

                left_step(TURN_BIG * 2)

                if line_found():
                    print("BLACK FOUND")
                    found = True


            # -----------------------------------------------
            # 4. WIDER RIGHT SEARCH
            # -----------------------------------------------

            if not found:

                print("SEARCH RIGHT - WIDE")

                right_step(TURN_BIG * 2)

                if line_found():
                    print("BLACK FOUND")
                    found = True


            # -----------------------------------------------
            # STILL LOST -> BACK UP
            # -----------------------------------------------

            if not found:

                print("LINE NOT FOUND -> BACK")

                back_step()


except KeyboardInterrupt:

    print("\nStopped")


finally:

    stop()
    slp.off()

    print("Motors stopped")
