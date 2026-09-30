from gpiozero import RotaryEncoder
from time import sleep

encoder = RotaryEncoder(
    'GPIO25',
    'GPIO20',
    max_steps=0
)

print("Rotate MOTA wheel exactly one full revolution.")

start = encoder.steps

sleep(5)

end = encoder.steps

print("Encoder count change:", end - start)
