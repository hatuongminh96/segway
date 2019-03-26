#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
File name: PID_thread.py
Author: Canopus Tong
Date created: 20/11/2018
Python Version: 3.4.0
Description: 
'''
from ev3dev.ev3 import *
import time, threading, math

threadLock = threading.Lock()


class PID_thread(threading.Thread):
    def __init__(self, motor1, motor2, sensor):
        threading.Thread.__init__(self)
        print("Start")
        self.Motor1 = LargeMotor(motor1)
        self.Motor2 = LargeMotor(motor2)
        self.Gyro = GyroSensor(sensor)
        self.dt = 0.03
        self.dt_program_flow = 0
        self.Motor1.position = 0
        self.Motor2.position = 0
        self.ph = 0
        self.dph_dt = 0
        self.encoder_sum = 0
        self.th = 0
        self.dth_dt = 0
        self.ave_dth_dt = 0
        self.Gyro.mode = 'GYRO-CAL'
        self.Gyro.mode = 'GYRO-G&A'
        while True:
            if self.Gyro.value(1) == 0:
                break
        self.e_prev = 0
        self.edt = 0
        self.Kp = 0.95
        self.Ki = 0.01
        self.Kd = 0.002
        self.pid = 0
        self.timer_time = 0
        self.setpoint = 0
        self.last_command_type = "stand_still"
        self.ph_input = 0
        self.left_ph_c = 1
        self.right_ph_c = 1
        self.isRunning = True
        self.ccw = 0

    def run(self):
        threadLock.acquire()
        print("Starting " + threading.current_thread().name)
        threadLock.release()
        try:
            while self.isRunning:
                self.runMotors()
        except Exception as e:
            print(e)
        finally:
            self.Motor1.stop()
            self.Motor2.stop()


    def runMotors(self):
        e = self.calc_error()

        self.pid = self.calc_pid(e)

        speed1 = self.pid * 10 * self.left_ph_c + self.ccw
        if speed1 != 0:
            speed1 = speed1 / abs(speed1) * min(abs(speed1), 1050)

        speed2 = self.pid * 10 * self.right_ph_c - self.ccw
        if speed2 != 0:
            speed2 = speed2 / abs(speed2) * min(abs(speed2), 1050)

        self.Motor1.run_forever(speed_sp=speed1)
        self.Motor2.run_forever(speed_sp=speed2)

        self.calc_dt()

        if abs(self.th) > 35:
            self.terminate()

    def calc_dt(self):
        if self.dt_program_flow == 0:
            self.timer_time = time.time()
            self.dt_program_flow = 1
        elif self.dt_program_flow == 1:
            temp = self.timer_time
            self.timer_time = \
                time.time()
            self.dt = self.timer_time - temp
            self.dt_program_flow = 2
        elif self.dt_program_flow == 2:
            temp = time.time()
            self.dt = 0.7 * self.dt + 0.3 * (temp - self.timer_time)
            self.timer_time = temp

    def calc_pid(self, e):
        self.de_dt = (e - self.e_prev) / self.dt
        self.edt = (e * self.dt) + self.edt
        self.e_prev = e
        pid = self.Kp * e + self.Ki * self.edt + self.Kd * self.de_dt
        if pid > 100:
            pid = 100
        elif pid < -100:
            pid = -100
        return pid

    def calc_error(self):
        temp = self.ave_dth_dt
        rate = self.Gyro.value(1)
        self.ave_dth_dt = (0.001 * rate) + (0.999 * temp)
        self.dth_dt = rate - temp
        self.th = self.th + (self.dt * self.dth_dt)
        a = 15 * (self.th)
        b = 0.8 * self.dth_dt
        temp1 = self.encoder_sum
        self.encoder_sum = self.Motor1.position + self.Motor2.position
        temp2 = self.encoder_sum - temp1
        self.dph_dt = 0.75 * self.dph_dt + 0.25 * (temp2 / self.dt)
        self.cal_ph_input()
        self.ph = self.ph + temp2 + self.ph_input
        c = 0.08 * self.ph
        d = 0.08 * self.dph_dt
        e = a + b + c + d
        return e

    def move(self, command):
        print(command)
        if command == 'forward':
            self.forward()
            self.left_ph_c = 1
            self.right_ph_c = 1
            self.last_command_type = 'forward'
        elif command == 'backward':
            self.backward()
            self.left_ph_c = 1
            self.right_ph_c = 1
            self.last_command_type = 'backward'
        elif command == 'left_forward':
            self.forward()
            self.left_ph_c = 1.25
            self.right_ph_c = 0.8
            self.last_command_type = 'forward'
        elif command == 'right_forward':
            self.forward()
            self.left_ph_c = 0.8
            self.right_ph_c = 1.25
            self.last_command_type = 'forward'
        elif command == 'left_backward':
            self.backward()
            self.left_ph_c = 1.25
            self.right_ph_c = 0.8
            self.last_command_type = 'backward'
        elif command == 'right_backward':
            self.backward()
            self.left_ph_c = 0.8
            self.right_ph_c = 1.25
            self.last_command_type = 'backward'
        elif command == 'stop':
            self.move_stop()
            self.left_ph_c = 1
            self.right_ph_c = 1
            self.last_command_type = 'stand_still'
        elif command == 'turn_cw':
            self.move_stop()
            self.left_ph_c = 1
            self.right_ph_c = 1
            self.ccw = -10
            self.last_command_type = 'stand_still'            
        elif command == 'turn_ccw':
            self.move_stop()
            self.left_ph_c = 1
            self.right_ph_c = 1
            self.ccw = 10
            self.last_command_type = 'stand_still'            
    
    def cal_ph_input(self):
        if self.last_command_type == 'forward':
            self.forward()
        elif self.last_command_type == 'backward':
            self.backward()
        else: # stand_still
            self.move_stop()

    def forward(self):
        self.ph_input = min(-2,self.ph_input-0.04)

    def backward(self):
        self.ph_input = max(2,self.ph_input+0.04)

    def move_stop(self):
        self.ph_input *= 0.9

    def terminate(self):
        self.isRunning = False

    # ====== setters & getters =====
    def set_setpoint(self, setpoint):
        if self.setpoint != setpoint:
            self.setpoint = setpoint
            self.e_prev = 0
            self.edt = 0
        self.isRunning = True

    def get_setpoint(self):
        return self.setpoint

    def setKp(self, Kp):
        self.Kp = Kp

    def getKp(self):
        return self.Kp

    def setKi(self, Ki):
        self.Ki = Ki

    def getKi(self):
        return self.Ki

    def setKd(self, Kd):
        self.Kd = Kd

    def getKd(self):
        return self.Kd

    def getdt(self):
        return self.dt

    def getoutput(self):
        return self.pid
