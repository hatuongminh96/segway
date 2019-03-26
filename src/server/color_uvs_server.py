"""
File name: uvs_server.py
Author: Minh Nguyen, Cody Labrecque, Canopus Tong
Python Version: 3.5
Description: color tracking server
"""

# !/usr/bin/python3

import socket
import cv2
from threading import Thread
from src.server.color_track import trackColor

(major_ver, minor_ver, subminor_ver) = (cv2.__version__).split('.')


class Solution:
    def __init__(self):
        self.video = cv2.VideoCapture(1)
        self.target = None
        self.curpos = (0, 0)
        self.tracker = None
        self.delta = 10
        self.initServer()
        self.current_angle = [0, 0]
        self._lambda = 0.2
        self.time = 1

    def initServer(self):
        self.serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.host = '169.254.154.4'
        print("host: ", self.host)
        self.port = 9999
        self.serversocket.bind((self.host, self.port))
        # queue up to 5 requests
        self.serversocket.listen(5)
        self.clientsocket, self.addr = self.serversocket.accept()
        print("Connected to: %s" % str(self.addr))


    def moveCar(self, r):
        print(r)
        self.clientsocket.send(r.encode())
        self.serversocket.setblocking(0)

        msg = ['']
        sk = self.clientsocket

        def save_msg():
            msg[0] = sk.recv(1024)

        t = Thread(target=save_msg)
        t.start()
        while True:
            # self.getEndPt()
            trackColor()
            if msg[0]: break
        t._stop()
        # self.getEndPt(False)

    def go(self):
        while True:
            try:x, y, radius, area = trackColor('blue')
            except: continue
            if x + radius < 200:
                self.moveCar('left')
            elif x - radius > 400:
                self.moveCar('right')

            try:x, y, radius, area = trackColor('blue')
            except: continue

            if area < 10000:
                self.moveCar('forward')
            elif area > 15000:
                self.moveCar('backward')


if __name__ == "__main__":
    s = Solution()
    s.go()
    cv2.destroyAllWindows()
