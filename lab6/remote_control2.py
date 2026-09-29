#! /usr/bin/env python3

import curses
from gpiozero import DigitalOutputDevice, Motor, Robot

slp = DigitalOutputDevice('GPIO17')

robot = Robot(
    left=Motor('GPIO12', 'GPIO18'),
    right=Motor('GPIO19', 'GPIO13')
)

def main(stdscr):
    slp.on()

    curses.cbreak()
    stdscr.keypad(True)

    # Wait up to 300 ms for another key press
    stdscr.timeout(600)

    stdscr.addstr(0, 0, "Hold WASD to move, release to stop, Q to quit")

    try:
        while True:
            key = stdscr.getch()

            if key == ord('w'):
                stdscr.addstr(1, 0, "Forward   ")
                robot.forward()

            elif key == ord('s'):
                stdscr.addstr(1, 0, "Backward  ")
                robot.backward()

            elif key == ord('a'):
                stdscr.addstr(1, 0, "Left      ")
                robot.right(0.1)   # swapped for rover

            elif key == ord('d'):
                stdscr.addstr(1, 0, "Right     ")
                robot.left(0.1)    # swapped for rover

            elif key == ord('q'):
                break

            elif key == -1:
                # No key received -> stop
                stdscr.addstr(1, 0, "Stopped   ")
                robot.stop()

    finally:
        robot.stop()
        slp.off()

curses.wrapper(main)
