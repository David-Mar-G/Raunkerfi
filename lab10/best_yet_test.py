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
# SPEED SETTINGS
# =====================================

# Compensate for rover drifting left
RIGHT_FORWARD_SPEED = 0.095
LEFT_FORWARD_SPEED = 0.10

# Separate turning strengths
LEFT_TURN_SPEED = 0.095
RIGHT_TURN_SPEED = 0.105

BACK_SPEED = 0.08


# =====================================
# MOVEMENT SETTINGS
# =====================================

# Normal movement
FORWARD_TIME = 0.03

# Very small movement after line recovery
RECOVERY_FORWARD_TIME = 0.01
RECOVERY_STEPS = 3

# Search begins small
SEARCH_TIME = 0.06

# Increase search size after each failed cycle
SEARCH_INCREASE = 0.025

# Do not allow individual searches to become ridiculous
MAX_SEARCH_TIME = 0.25

# Back up after each complete left/right sweep
BACK_TIME = 0.06

PAUSE_TIME = 0.03


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

    # Right turn
    mota.backward(RIGHT_TURN_SPEED)
    motb.forward(RIGHT_TURN_SPEED)


def left():

    # Left turn
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

        # Check that black is really still there
        if not confirm_black():

            print("LINE LOST DURING REACQUIRE")
            return False


        print(
            f"REACQUIRE STEP "
            f"{step + 1}/{RECOVERY_STEPS}"
        )


        # Very small forward movement
        forward()

        time.sleep(RECOVERY_FORWARD_TIME)

        stop()

        time.sleep(PAUSE_TIME)


    print("LINE STABLE")

    return True


# =====================================
# SEARCH FOR LINE
# =====================================

def search_line():

    print("SMART SEARCH STARTED")

    stop()

    search_time = SEARCH_TIME
    attempt = 0


    while True:

        attempt += 1

        print(
            f"SEARCH ATTEMPT {attempt} "
            f"TIME={search_time:.3f}"
        )


        # =================================
        # 1. SEARCH LEFT
        # =================================

        print("LOOK LEFT")

        if move_and_check(left, search_time):

            stop()

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
            search_time * 2
        ):

            stop()

            if confirm_black():

                print("BLACK FOUND RIGHT")

                if reacquire_line():
                    return True


        # =================================
        # 3. RETURN ROUGHLY TO CENTRE
        # =================================

        print("RETURN TO CENTRE")

        left()

        time.sleep(search_time)

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

            stop()

            if confirm_black():

                print("BLACK FOUND BACKWARD")

                if reacquire_line():
                    return True


        # =================================
        # 5. INCREASE SEARCH SIZE
        # =================================

        search_time += SEARCH_INCREASE


        if search_time > MAX_SEARCH_TIME:

            search_time = MAX_SEARCH_TIME


        print(
            f"SEARCHING WIDER -> "
            f"{search_time:.3f}"
        )

        time.sleep(PAUSE_TIME)


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

            time.sleep(PAUSE_TIME)


except KeyboardInterrupt:

    print("\nSTOPPING ROVER")


finally:

    stop()

    slp.off()

    print("MOTORS OFF")
