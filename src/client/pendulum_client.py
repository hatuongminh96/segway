#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
Author: Canopus Tong
Date created: 21/11/2018
Python Version: 3.4.0
Description: 
Ref: https://www.tutorialspoint.com/python/python_multithreading.htm
'''
from ev3dev.ev3 import *
from src.client.pendulum_thread import *
import time
import socket

SLEEPTIME = 0.5


def start_controller():
    threads = []
    # Create new threads
    thread1 = PID_thread(OUTPUT_A, OUTPUT_B,INPUT_2)
    thread1.setDaemon(True)

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect(('169.254.154.4', 9999))

    # Start new Threads
    thread1.start()

    # Start timer
    t0 = time.time()

    # Add threads to thread list
    threads.append(thread1)

    # Do something here...
    # commands = ["forward","backward","left_forward","right_forward","left_backward","right_backward","turn_cw","turn_ccw","stop"]
    # texts = ["Forward","Backward","Left Forward","Right Forward","Left Backward","Right Backward","Turn CW","Turn CCW","Stop"]
    # print("Select command:")
    while True:
        msg = s.recv(1024)
        msg = msg.decode()
        if msg == 'left':
            thread1.move('left_forward')
        elif msg == 'right':
            thread1.move('right_forward')
        elif msg == 'forward':
            thread1.move('forward')
        elif msg == 'backward':
            thread1.move('backward')
        time.sleep(SLEEPTIME)
        thread1.move('stop')
        msg = "Moved"
        s.send(msg.encode())
        thread1.move('stop')
    # Wait for all threads to complete
    for t in threads:
        t.join()
    print("Time taken: ", str(time.time()-t0))
    print("Exiting Main Thread")

if __name__ == "__main__":
    start_controller()

