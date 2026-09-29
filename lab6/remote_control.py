#! /usr/bin/env python3

import time
import curses

from gpiozero import DigitalOutputDevice, Motor, Robot

try:
    stdscr = curses.initscr()
    curses.cbreak()
    stdscr.keypad(1)

    stdscr.addstr(0, 10, "WASD to move, E to stop, Q to quit")
    stdscr.nodelay(1)

    direction = None

    slp = DigitalOutputDevice('GPIO17')
    slp.on()

    robot = Robot(
        left=Motor('GPIO12', 'GPIO18'),
        right=Motor('GPIO19', 'GPIO13')
    )

    while direction != ord('q'):
        stdscr.refresh()
        direction = stdscr.getch()

        if direction == ord('e'):
            stdscr.addstr(1, 10, "Stop     ")
            robot.stop()

        elif direction == ord('a'):
            stdscr.addstr(1, 10, "Left     ")
            robot.right()

        elif direction == ord('s'):
            stdscr.addstr(1, 10, "Backward ")
            robot.backward()

        elif direction == ord('d'):
            stdscr.addstr(1, 10, "Right    ")
            robot.left()

        elif direction == ord('w'):
            stdscr.addstr(1, 10, "Forward  ")
            robot.forward()

        time.sleep(0.04)

finally:
    robot.stop()
    slp.off()

    curses.nocbreak()
    stdscr.keypad(0)
    curses.endwin()
