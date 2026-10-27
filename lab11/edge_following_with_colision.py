
import time
import board
import adafruit_tcs34725
from gpiozero import Motor, DigitalOutputDevice, MCP3008

# =====================================
# COLOUR SENSOR
# =====================================

color_sensor = adafruit_tcs34725.TCS34725(board.I2C())
color_sensor.integration_time = 12
color_sensor.gain = 4

THRESHOLD = 900

# =====================================
# DISTANCE SENSOR
# =====================================

distance_sensor = MCP3008(channel=0)

STOP_VOLTAGE = 2.35
RESUME_VOLTAGE = 2.15

DISTANCE_INTERVAL = 0.5  # Check every 500 ms

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
# SPEED
# =====================================

SPEED = 0.14
RIGHT_REVERSE_SPEED = 0.06

# =====================================
# MAIN
# =====================================

try:
    slp.on()

    print("LINE FOLLOWER WITH OBSTACLE DETECTION")
    print("Starting in 2 seconds...")
    time.sleep(2)

    counter = 0
    obstacle_detected = False
    voltage = 0.0
    last_distance_check = 0.0

    while True:

        now = time.monotonic()

        # Check distance every 50 ms
        if now - last_distance_check >= DISTANCE_INTERVAL:
            voltage = distance_sensor.value * 3.3
            last_distance_check = now

            if not obstacle_detected and voltage >= STOP_VOLTAGE:
                obstacle_detected = True
                print(f"OBSTACLE DETECTED - STOP ({voltage:.2f} V)")

            elif obstacle_detected and voltage <= RESUME_VOLTAGE:
                obstacle_detected = False
                print("OBSTACLE REMOVED - RESUMING")

        # Obstacle has priority over line following
        if obstacle_detected:
            mota.stop()
            motb.stop()
            continue

        # Normal line following
        r, g, b, clear = color_sensor.color_raw

        if clear < THRESHOLD:
            mota.backward(RIGHT_REVERSE_SPEED)
            motb.forward(SPEED)
        else:
            mota.forward(SPEED)
            motb.stop()

        counter += 1

        if counter % 10 == 0:
            print(f"C={clear} | Distance voltage={voltage:.2f} V")

except KeyboardInterrupt:
    print("Stopping")

finally:
    mota.stop()
    motb.stop()
    slp.off()

