from gpiozero import RotaryEncoder
from time import sleep

encoder = RotaryEncoder(
    'GPIO26',
    'GPIO5',
    max_steps=0
)

print("Rotate MOTB wheel exactly one full revolution.")

start = encoder.steps

sleep(5)

end = encoder.steps

print("Encoder count change:", end - start)
