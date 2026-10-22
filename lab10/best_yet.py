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

# Your calibration:
# black roughly below 3000
# white well above 3000
BLACK_THRESHOLD = 3000


# =====================================
# MOTORS
# =====================================

slp = DigitalOutputDevice("GPIO17")

mota = Motor(
    forward="GPIO12",
    backward="GPIO18",
    pwm=True
)

motb = Motor(
    forward="GPIO19",
    backward="GPIO13",
    pwm=True
)


# =====================================
# SPEED / TIMING SETTINGS
# =====================================

FORWARD_SPEED = 0.10
TURN_SPEED = 0.10
BACK_SPEED = 0.08

FORWARD_TIME = 0.03

SEARCH_LEFT_TIME = 0.08
SEARCH_RIGHT_TIME = 0.16

RETURN_TIME = 0.08

BACK_TIME = 0.08

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
    """
    Confirm that black is really under the sensor.
    At least 2 out of 3 readings must be black.
    """

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
    mota.forward(FORWARD_SPEED)
    motb.forward(FORWARD_SPEED)


def backward():
    mota.backward(BACK_SPEED)
    motb.backward(BACK_SPEED)


def right():
    mota.forward(TURN_SPEED)
    motb.backward(TURN_SPEED)


def left():
    mota.backward(TURN_SPEED)
    motb.forward(TURN_SPEED)


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
# LINE SEARCH
# =====================================

def search_line():

    print("SEARCH STARTED")

    stop()

    while True:

        # ---------------------------------
        # 1. Search left
        # ---------------------------------

        print("SEARCH LEFT")

        if move_and_check(left, SEARCH_LEFT_TIME):

            stop()

            if confirm_black():

                print("BLACK CONFIRMED LEFT")
                return


        # ---------------------------------
        # 2. Search right past centre
        # ---------------------------------

        print("SEARCH RIGHT")

        if move_and_check(right, SEARCH_RIGHT_TIME):

            stop()

            if confirm_black():

                print("BLACK CONFIRMED RIGHT")
                return


        # ---------------------------------
        # 3. Return approximately to centre
        # ---------------------------------

        print("RETURN TO CENTRE")

        left()
        time.sleep(RETURN_TIME)
        stop()

        time.sleep(PAUSE_TIME)


        # ---------------------------------
        # 4. Back up slightly
        # ---------------------------------

        print("BACK UP")

        if move_and_check(backward, BACK_TIME):

            stop()

            if confirm_black():

                print("BLACK CONFIRMED WHILE BACKING")
                return


        # ---------------------------------
        # 5. Repeat search
        # ---------------------------------

        print("RETRY SEARCH")

        time.sleep(PAUSE_TIME)


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

        # ---------------------------------
        # Black detected -> move forward
        # ---------------------------------

        if is_black():

            print("BLACK -> FORWARD")

            forward()

            time.sleep(FORWARD_TIME)


        # ---------------------------------
        # White detected -> stop and recover
        # ---------------------------------

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
