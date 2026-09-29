from gpiozero import RotaryEncoder
from time import sleep

enca = RotaryEncoder(
    'GPIO25',
    'GPIO20',
    max_steps=0
)

encb = RotaryEncoder(
    'GPIO26',
    'GPIO5',
    max_steps=0
)

while True:
    print(f"MOTA: {enca.steps}   MOTB: {encb.steps}")
    sleep(0.2)
