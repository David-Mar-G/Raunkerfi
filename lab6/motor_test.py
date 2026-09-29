from gpiozero import Motor, DigitalOutputDevice
from time import sleep

slp = DigitalOutputDevice('GPIO17')

mota = Motor(
    forward='GPIO12',
    backward='GPIO18',
    pwm=True
)

motb = Motor(
    forward='GPIO19',
    backward='GPIO13',
    pwm=True
)

try:
    slp.on()

    print("MOTA forward")
    mota.forward()
    sleep(2)
    mota.stop()

    sleep(1)

    print("MOTA backward")
    mota.backward()
    sleep(2)
    mota.stop()

    sleep(1)

    print("MOTB forward")
    motb.forward()
    sleep(2)
    motb.stop()

    sleep(1)

    print("MOTB backward")
    motb.backward()
    sleep(2)
    motb.stop()

    sleep(1)

    print("Both motors forward")
    mota.forward()
    motb.forward()
    sleep(3)
    mota.stop()
    motb.stop()

    sleep(1)

    print("Both motors backward")
    mota.backward()
    motb.backward()
    sleep(3)

finally:
    mota.stop()
    motb.stop()
    slp.off()

print("Stopped")
