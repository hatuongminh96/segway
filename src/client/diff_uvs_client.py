"""
File name: uvs_client.py
Author: Minh Nguyen, Cody Labrecque, Canopus Tong
Python Version: 3.5
Description: visual servoing client
"""

import socket
import json
import time
from ev3dev.ev3 import *
from math import pi


left = LargeMotor(OUTPUT_A)
right = LargeMotor(OUTPUT_B)

# 90 deg turn variables
STRAIGHT_SPEED = 120
WHEEL_RADIUS = 4.08
LENGTH_BETWEEN_WHEELS = 15
TURN_DURATION = 0.5
PADDING_TIME = 0.17
CIRCLE_RADIUS = 0


def setup_client(host, port):
    # create a socket object
    print("setting up client")
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # connect to hostname on the port.
    s.connect((host, port))
    # Receive no more than 1024 bytes
    while True:
        msg = s.recv(1024)
        msg = msg.decode().split()
        # msg = input().split()
        msg[1] = float(msg[1])
        if len(msg) > 0:
            print("Received: ", msg)
            if msg[0] == 'forward':
                left.run_timed(speed_sp=-STRAIGHT_SPEED, time_sp=msg[1] * 1000, stop_action='brake')
                right.run_timed(speed_sp=-STRAIGHT_SPEED, time_sp=msg[1] * 1000, stop_action='brake')
                time.sleep(msg[1])
            elif msg[0] == 'backward':
                left.run_timed(speed_sp=STRAIGHT_SPEED, time_sp=msg[1] * 1000, stop_action='brake')
                right.run_timed(speed_sp=STRAIGHT_SPEED, time_sp=msg[1] * 1000, stop_action='brake')
                time.sleep(msg[1])
            elif msg[0] == 'left':
                TURN_ANGLE = float(msg[1])
                wr_minus_wl = TURN_ANGLE * LENGTH_BETWEEN_WHEELS / WHEEL_RADIUS

                wr_plus_wl = CIRCLE_RADIUS * wr_minus_wl / (LENGTH_BETWEEN_WHEELS / 2)

                wl = (wr_plus_wl - wr_minus_wl) / 2
                wr = wr_plus_wl - wl

                wl_in_deg = wl * (180 / pi) * 2
                wr_in_deg = wr * (180 / pi) * 2

                left.run_timed(speed_sp=-wl_in_deg / TURN_DURATION, time_sp=(TURN_DURATION + PADDING_TIME) * 1000)
                right.run_timed(speed_sp=-wr_in_deg / TURN_DURATION, time_sp=(TURN_DURATION + PADDING_TIME) * 1000)
                time.sleep(TURN_DURATION + PADDING_TIME)

            elif msg[0] == 'right':
                TURN_ANGLE = -float(msg[1])
                wr_minus_wl = TURN_ANGLE * LENGTH_BETWEEN_WHEELS / WHEEL_RADIUS

                wr_plus_wl = CIRCLE_RADIUS * wr_minus_wl / (LENGTH_BETWEEN_WHEELS / 2)

                wl = (wr_plus_wl - wr_minus_wl) / 2
                wr = wr_plus_wl - wl

                wl_in_deg = wl * (180 / pi) * 2
                wr_in_deg = wr * (180 / pi) * 2
                left.run_timed(speed_sp=-wl_in_deg / TURN_DURATION, time_sp=(TURN_DURATION + PADDING_TIME) * 1000)
                right.run_timed(speed_sp=-wr_in_deg / TURN_DURATION, time_sp=(TURN_DURATION + PADDING_TIME) * 1000)
                time.sleep(TURN_DURATION + PADDING_TIME)

            msg = "Moved"
            s.send(msg.encode())
        else:
            break
    s.close()
    left.stop()
    right.stop()
    left.reset()
    right.reset()

if __name__ == "__main__":
    host = socket.gethostname()
    # host = input("Host: ")
    host = "169.254.238.55"
    port = 9999
    try:
        setup_client(host, port)
    except Exception as e:
        print(e)
    finally:
        left.stop()
        right.stop()
        left.reset()
        right.reset()
