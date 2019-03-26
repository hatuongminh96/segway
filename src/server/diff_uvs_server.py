"""
File name: uvs_server.py
Author: Minh Nguyen, Cody Labrecque, Canopus Tong
Python Version: 3.5
Description: visual servoing server
"""

# !/usr/bin/python3

import socket
import cv2
import sys
import time
from threading import Thread
from math import *

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
        self.host = '169.254.238.55'
        print("host: ", self.host)
        self.port = 9999
        self.serversocket.bind((self.host, self.port))
        # queue up to 5 requests
        self.serversocket.listen(5)
        self.clientsocket, self.addr = self.serversocket.accept()
        print("Connected to: %s" % str(self.addr))

    def invMatrix(self, mt):  # inverse a 2x2 matrix
        det = mt[0][0] * mt[1][1] - mt[0][1] * mt[1][0]
        if det == 0:
            print('Cannot inverse', mt)
            return mt
        return [[mt[1][1] / det, -mt[0][1] / det], [-mt[1][0] / det, mt[0][0] / det]]

    # Return x y position of target
    # Ready to delete
    def getTarget(self):
        ix, iy = -1, -1

        # mouse callback function
        def draw_circle(event, x, y, flags, param):
            global ix, iy
            if event == cv2.EVENT_LBUTTONDBLCLK:
                cv2.circle(frame, (x, y), 100, (255, 0, 0), -1)
                ix, iy = x, y
                self.target = (ix, iy)
                print("Target", x, y)

        # Create a black image, a window and bind the function to window
        cv2.namedWindow('image')
        cv2.setMouseCallback('image', draw_circle)

        while (1):
            ok, frame = self.video.read()
            cv2.imshow('image', frame)
            k = cv2.waitKey(20) & 0xFF
            if k == 27:
                break
        cv2.destroyAllWindows()

    # Create tracker
    def initTracker(self):
        tracker_types = ['BOOSTING', 'MIL', 'KCF', 'TLD', 'MEDIANFLOW', 'GOTURN', 'MOSSE', 'CSRT']
        self.tracker_type = tracker_types[1]

        if int(minor_ver) < 3:
            self.tracker = cv2.Tracker_create(self.tracker_type)
        else:
            if self.tracker_type == 'BOOSTING':
                self.tracker = cv2.TrackerBoosting_create()
            if self.tracker_type == 'MIL':
                self.tracker = cv2.TrackerMIL_create()
            if self.tracker_type == 'KCF':
                self.tracker = cv2.TrackerKCF_create()
            if self.tracker_type == 'TLD':
                self.tracker = cv2.TrackerTLD_create()
            if self.tracker_type == 'MEDIANFLOW':
                self.tracker = cv2.TrackerMedianFlow_create()
            if self.tracker_type == 'GOTURN':
                self.tracker = cv2.TrackerGOTURN_create()
            if self.tracker_type == 'MOSSE':
                self.tracker = cv2.TrackerMOSSE_create()
            if self.tracker_type == "CSRT":
                self.tracker = cv2.TrackerCSRT_create()

        # Exit if video not opened.
        if not self.video.isOpened():
            print("Could not open video")
            sys.exit()

        # Read first 30 frame.
        for i in range(30):
            ok, self.frame = self.video.read()
            if not ok:
                print('Cannot read video file')
                sys.exit()

        # Define an initial bounding box
        self.bbox = (287, 23, 86, 320)

        # Uncomment the line below to select a different bounding box
        self.bbox = cv2.selectROI(self.frame, False)

        # Initialize tracker with first frame and bounding box
        ok = self.tracker.init(self.frame, self.bbox)

        # Destroy window
        cv2.destroyAllWindows()

    def getEndPt(self, savepos=True):

        # Read a new frame
        ok, self.frame = self.video.read()
        if not ok:
            return False

        # Start timer
        timer = cv2.getTickCount()

        # Update tracker
        ok, self.bbox = self.tracker.update(self.frame)

        # Calculate Frames per second (FPS)
        fps = cv2.getTickFrequency() / (cv2.getTickCount() - timer)

        # mouse callback function
        def draw_circle(event, x, y, flags, param):
            global ix, iy
            if event == cv2.EVENT_LBUTTONDBLCLK:
                cv2.circle(self.frame, (x, y), 100, (255, 0, 0), -1)
                ix, iy = x, y
                self.target = (ix, iy)
                print("Target", x, y)

        # Create a black image, a window and bind the function to window
        cv2.namedWindow('Tracking')
        cv2.setMouseCallback('Tracking', draw_circle)

        # Draw bounding box
        if ok:
            # Tracking success
            p1 = (int(self.bbox[0]), int(self.bbox[1]))
            p2 = (int(self.bbox[0] + self.bbox[2]), int(self.bbox[1] + self.bbox[3]))
            cv2.rectangle(self.frame, p1, p2, (255, 0, 0), 2, 1)
            if self.target:
                cv2.rectangle(self.frame, (self.target[0] - 2, self.target[1] - 2),
                              (self.target[0] + 2, self.target[1] + 2), (0, 225, 0), 2, 1)

            # Display FPS on frame
            cv2.putText(self.frame, "FPS : " + str(int(fps)), (100, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (50, 170, 50),
                        2)

            cv2.imshow("Tracking", self.frame)

            k = cv2.waitKey(1) & 0xff
            if k == 27: pass

            if savepos:
                self.curpos = (p1[0] + (p2[0] - p1[0]) // 2, p1[1] + (p2[1] - p1[1]) // 2)
                return self.curpos
        else:
            # Tracking failure
            cv2.putText(self.frame, "Tracking failure detected", (100, 80), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (0, 0, 255),
                        2)

    def getDxy(self, prev_x, prev_y):
        return self.curpos[0] - prev_x, self.curpos[1] - prev_y

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
            self.getEndPt()
            if msg[0]: break
        t._stop()
        self.getEndPt(False)

    def go(self, pos1=None, pos2=None):
        target = self.target
        _lbda = 0.2
        self.getEndPt(True)
        distance = sum(i ** 2 for i in self.getDxy(target[0], target[1])) ** 0.5
        while distance < 30:
            print("distance",distance)
            self.getEndPt(True)
            target = self.target
            distance = sum(i ** 2 for i in self.getDxy(target[0], target[1])) ** 0.5

        if pos1 == None and pos2 == None:
            pos1 = self.curpos
            dxy = self.getDxy(target[0], target[1])

            self.moveCar("forward 1")
            self.getEndPt(True)
            pos2 = self.curpos
            dxy2 = self.getDxy(target[0], target[1])
            self.moveCar("backward 1")
        else:
            self.curpos = pos1
            dxy = self.getDxy(target[0], target[1])
            self.curpos = pos2
            dxy2 = self.getDxy(target[0], target[1])
            self.getEndPt(True)

        ab = ((pos2[0] - pos1[0]) ** 2 + (pos2[1] - pos1[1]) ** 2) ** 0.5
        ac = ((target[0] - pos1[0]) ** 2 + (target[1] - pos1[1]) ** 2) ** 0.5
        bc = ((pos2[0] - target[0]) ** 2 + (pos2[1] - target[1]) ** 2) ** 0.5

        try:angle = acos((ab ** 2 + ac ** 2 - bc ** 2) / (2 * ab * ac))
        except: angle = 0
        velocity = ((dxy2[0] - dxy[0]) ** 2 + (dxy2[1] - dxy[1]) ** 2) ** 0.5 / self.time

        if abs(angle) < 5 / 180 * pi:
            self.getEndPt(True)
            startpos = self.curpos
            if sum([i ** 2 for i in dxy]) < sum([i ** 2 for i in dxy2]):
                self.moveCar("backward {}".format(distance / velocity * _lbda))
            else:
                self.moveCar("forward {}".format(distance / velocity * _lbda))
            self.getEndPt(True)
            endpos = self.curpos
        else:
            d = (target[0] - pos1[0]) * (pos2[1] - pos1[1]) - (target[1] - pos1[1]) * (pos2[0] - pos1[0])
            if angle <= pi/2:
                if d > 0:
                    self.moveCar("left {}".format(angle))
                else:
                    self.moveCar("right {}".format(angle))

                self.getEndPt(True)
                startpos = self.curpos
                self.moveCar("forward {}".format(distance / velocity * _lbda))
                self.getEndPt(True)
                endpos = self.curpos
            else:
                if d < 0:
                    self.moveCar("left {}".format(pi - angle))
                else:
                    self.moveCar("right {}".format(pi -angle))

                self.getEndPt(True)
                endpos = self.curpos
                self.moveCar("backward {}".format(distance / velocity * _lbda))
                self.getEndPt(True)
                startpos = self.curpos
        self.time = (distance / velocity * _lbda)
        self.getEndPt(True)
        self.go(startpos, endpos)


if __name__ == "__main__":
    s = Solution()
    s.initTracker()
    while not s.target:
        s.getEndPt()
    s.go()
    cv2.destroyAllWindows()
