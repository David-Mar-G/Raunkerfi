import time
import board
import adafruit_tcs34725
from gpiozero import Motor, DigitalOutputDevice


# =====================================
# COLOUR SENSOR
# =====================================

i2c = board.I2C()
sensor = adafruit_tcs34725.TCS34725(i2c)

sensor.integration_time = 50
sensor.gain = 4

BLACK_THRESHOLD = 3000


# =====================================
# MOTORS
# =====================================

slp = DigitalOutputDevice("GPIO17")

# MOTA = right wheel
mota = Motor(
    forward="GPIO12",
    backward="GPIO18",
    pwm=True
)

# MOTB = left wheel
motb = Motor(
    forward="GPIO19",
    backward="GPIO13",
    pwm=True
)


# =====================================
# SPEED / TIMING SETTINGS
# =====================================

# Straight-driving calibration
RIGHT_FORWARD_SPEED = 0.095
LEFT_FORWARD_SPEED = 0.10

# Recovery turning
LEFT_TURN_SPEED = 0.095
RIGHT_TURN_SPEED = 0.105

BACK_SPEED = 0.08

# Normal forward pulse
FORWARD_TIME = 0.03

# Much shorter pulse immediately after recovery
RECOVERY_FORWARD_TIME = 0.01
RECOVERY_STEPS = 3

# Slightly smaller searches than before
SEARCH_LEFT_TIME = 0.06
SEARCH_RIGHT_TIME = 0.12

RETURN_TIME = 0.06

# Normal recovery backup
BACK_TIME = 0.06

# Bigger reset backup after repeated failures
RESET_BACK_TIME = 0.12

PAUSE_TIME = 0.03

# Recovery limits
RESET_AFTER_ATTEMPTS = 5
MAX_SEARCH_ATTEMPTS = 25


# =====================================
# SENSOR FUNCTIONS
# =====================================

def is_black():
    r, g, b, clear = sensor.color_raw

    black = clear < BLACK_THRESHOLD

    print(
        f"CLEAR={clear} -> "
        f"{'BLACK' if black else 'WHITE'}"
    )

    return black


def confirm_black():
    black_count = 0

    for _ in range(3):

        if is_black():
            black_count += 1

        time.sleep(0.02)

    return black_count >= 2


# =====================================
# MOTOR FUNCTIONS
# =====================================

def stop():
    mota.stop()
    motb.stop()


def forward():
    mota.forward(RIGHT_FORWARD_SPEED)
    motb.forward(LEFT_FORWARD_SPEED)


def backward():
    mota.backward(BACK_SPEED)
    motb.backward(BACK_SPEED)


def right():
    mota.backward(RIGHT_TURN_SPEED)
    motb.forward(RIGHT_TURN_SPEED)


def left():
    mota.forward(LEFT_TURN_SPEED)
    motb.backward(LEFT_TURN_SPEED)


# =====================================
# MOVE WHILE CHECKING SENSOR
# =====================================

def move_and_check(move_function, duration):

    move_function()

    start = time.monotonic()

    try:

        while time.monotonic() - start < duration:

            if is_black():
                return True

            time.sleep(0.01)

        return False

    finally:
        stop()


# =====================================
# SLOW REACQUIRE
# =====================================

def reacquire_line():
    """
    After recovery, do not immediately return
    to normal forward movement.

    Move forward in very small steps and make
    sure the sensor continues seeing black.
    """

    print("SLOW REACQUIRE")

    for step in range(RECOVERY_STEPS):

        if not confirm_black():
            print("LINE LOST DURING REACQUIRE")
            return False

        print(
            f"REACQUIRE STEP "
            f"{step + 1}/{RECOVERY_STEPS}"
        )

        forward()
        time.sleep(RECOVERY_FORWARD_TIME)
        stop()

        time.sleep(PAUSE_TIME)

    print("LINE STABLE")

    return True


# =====================================
# LINE SEARCH
# =====================================

def search_line():

    print("SEARCH STARTED")

    stop()

    attempts = 0

    while attempts < MAX_SEARCH_ATTEMPTS:

        attempts += 1

        print(
            f"SEARCH ATTEMPT "
            f"{attempts}/{MAX_SEARCH_ATTEMPTS}"
        )


        # ---------------------------------
        # 1. Search left
        # ---------------------------------

        print("SEARCH LEFT")

        if move_and_check(left, SEARCH_LEFT_TIME):

            stop()

            if confirm_black():

                print("BLACK CONFIRMED LEFT")

                if reacquire_line():
                    return True


        # ---------------------------------
        # 2. Search right past centre
        # ---------------------------------

        print("SEARCH RIGHT")

        if move_and_check(right, SEARCH_RIGHT_TIME):

            stop()

            if confirm_black():

                print("BLACK CONFIRMED RIGHT")

                if reacquire_line():
                    return True


        # ---------------------------------
        # 3. Return approximately to centre
        # ---------------------------------

        print("RETURN TO CENTRE")

        left()
        time.sleep(RETURN_TIME)
        stop()

        time.sleep(PAUSE_TIME)


        # ---------------------------------
        # 4. Small backup
        # ---------------------------------

        print("BACK UP")

        if move_and_check(backward, BACK_TIME):

            stop()

            if confirm_black():

                print("BLACK CONFIRMED WHILE BACKING")

                if reacquire_line():
                    return True


        # ---------------------------------
        # 5. Bigger reset after 5 failures
        # ---------------------------------

        if attempts % RESET_AFTER_ATTEMPTS == 0:

            print("RECOVERY RESET")

            backward()
            time.sleep(RESET_BACK_TIME)
            stop()

            time.sleep(PAUSE_TIME)


        print("RETRY SEARCH")

        time.sleep(PAUSE_TIME)


    # ---------------------------------
    # Recovery failed completely
    # ---------------------------------

    print("RECOVERY FAILED - STOPPING")

    stop()

    return False


# =====================================
# MAIN PROGRAM
# =====================================

try:

    slp.on()

    print("==========================")
    print("BLACK LINE FOLLOWER")
    print("==========================")
    print("Ctrl+C to stop")

    time.sleep(2)

    while True:

        if is_black():

            print("BLACK -> FORWARD")

            forward()

            time.sleep(FORWARD_TIME)

        else:

            stop()

            print("BLACK LOST")

            recovered = search_line()

            if recovered:

                print("TRACK FOUND")

                stop()

                time.sleep(PAUSE_TIME)

            else:

                print("COULD NOT RECOVER LINE")

                break


except KeyboardInterrupt:

    print("\nSTOPPING ROVER")


finally:

    stop()
    slp.off()

    print("MOTORS OFF")
