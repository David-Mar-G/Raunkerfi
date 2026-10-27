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

SENSOR_SETTLE_TIME = 0.055


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
# SPEED SETTINGS
# =====================================

# Compensate for rover drifting left
RIGHT_FORWARD_SPEED = 0.095
LEFT_FORWARD_SPEED = 0.10

LEFT_TURN_SPEED = 0.095
RIGHT_TURN_SPEED = 0.105

BACK_SPEED = 0.08


# =====================================
# MOVEMENT SETTINGS
# =====================================

FORWARD_TIME = 0.03

# Small forward movement after recovery
RECOVERY_FORWARD_TIME = 0.015
RECOVERY_STEPS = 2

# Fixed search sizes
SEARCH_LEFT_TIME = 0.06
SEARCH_RIGHT_TIME = 0.12
RETURN_TIME = 0.06

# Small backup after every search cycle
BACK_TIME = 0.06

# Larger reset backup after repeated failures
RESET_BACK_TIME = 0.15
RESET_AFTER = 3

PAUSE_TIME = 0.01


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

    first = is_black()

    time.sleep(SENSOR_SETTLE_TIME)

    second = is_black()

    return first and second


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

    print("SLOW REACQUIRE")

    for step in range(RECOVERY_STEPS):

        print(
            f"REACQUIRE STEP "
            f"{step + 1}/{RECOVERY_STEPS}"
        )

        forward()

        time.sleep(RECOVERY_FORWARD_TIME)

        stop()

        time.sleep(PAUSE_TIME)

    if confirm_black():

        print("LINE STABLE")
        return True

    else:

        print("LINE LOST DURING REACQUIRE")
        return False


# =====================================
# SEARCH FOR LINE
# =====================================

def search_line():

    print("SEARCH STARTED")

    stop()

    attempts = 0

    while True:

        attempts += 1

        print(
            f"SEARCH ATTEMPT {attempts}"
        )


        # =================================
        # 1. SEARCH LEFT
        # =================================

        print("LOOK LEFT")

        if move_and_check(
            left,
            SEARCH_LEFT_TIME
        ):

            if confirm_black():

                print("BLACK FOUND LEFT")

                if reacquire_line():
                    return True


        # =================================
        # 2. SEARCH RIGHT PAST CENTRE
        # =================================

        print("LOOK RIGHT")

        if move_and_check(
            right,
            SEARCH_RIGHT_TIME
        ):

            if confirm_black():

                print("BLACK FOUND RIGHT")

                if reacquire_line():
                    return True


        # =================================
        # 3. RETURN APPROXIMATELY TO CENTRE
        # =================================

        print("RETURN TO CENTRE")

        left()

        time.sleep(RETURN_TIME)

        stop()

        time.sleep(PAUSE_TIME)


        # =================================
        # 4. BACK UP SLIGHTLY
        # =================================

        print("BACKING UP")

        if move_and_check(
            backward,
            BACK_TIME
        ):

            if confirm_black():

                print("BLACK FOUND BACKWARD")

                if reacquire_line():
                    return True


        # =================================
        # 5. BIGGER BACKUP RESET
        # =================================

        if attempts % RESET_AFTER == 0:

            print("LARGER BACKUP RESET")

            backward()

            time.sleep(RESET_BACK_TIME)

            stop()

            time.sleep(PAUSE_TIME)


        print("RETRY SMALL SEARCH")


# =====================================
# MAIN PROGRAM
# =====================================

try:

    slp.on()

    print("==========================")
    print("SMART BLACK LINE FOLLOWER")
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

            search_line()

            print("TRACK FOUND")

            stop()


except KeyboardInterrupt:

    print("\nSTOPPING ROVER")


finally:

    stop()

    slp.off()

    print("MOTORS OFF")
