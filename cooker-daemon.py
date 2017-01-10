#!/usr/bin/python3

import time
from datetime import datetime
import urllib.request
import json

import sys
import os
import atexit
import redis

import RPi.GPIO as GPIO

import CookerFeedbackController
from w1thermsensor import W1ThermSensor


redis_db = redis.Redis(host='127.0.0.1', port=6379, db=0)

# setup pin numbers
cooker_pin = 35 # pin number connected to relay for the cooker

influx_host = 'http://192.168.xxx.xxx:8086/write?db=home' # InfluxDB

GPIO.setmode(GPIO.BOARD) # it seems default mode doesn't work on RPi2

GPIO.setup(cooker_pin, GPIO.OUT)

print("init controller.")

def turn_on():
    GPIO.output(cooker_pin, True)
    redis_db.set('cooker_is_heating', 'true')

def turn_off():
    GPIO.output(cooker_pin, False)
    redis_db.set('cooker_is_heating', 'false')

def save_temperature(temp, name):
    try:
        url = influx_host
        data = ("cooker_%s value=%3.3f" % (name, temp)).encode('ascii')

        cont_len = len(data)
        req = urllib.request.Request(url, data, {'Content-Type': 'application/json', 'Content-Length': cont_len})
        f = urllib.request.urlopen(req)
        response = f.read()
        f.close()
    except Exception as e:
        print ("Failed to push temperature")
        print (e)

def save_setpoint(temp):
    try:
        url = influx_host
        data = "cooker_setpoint value={}".format(temp).encode('ascii')

        cont_len = len(data)
        req = urllib.request.Request(url, data, {'Content-Type': 'application/json', 'Content-Length': cont_len})
        f = urllib.request.urlopen(req)
        response = f.read()
        f.close()
    except Exception as e:
        print ("Failed to push temperature")
        print (e)

def save_data(data):
    url = influx_host
    cont_len = len(data)
    req = urllib.request.Request(url, data, {'Content-Type': 'application/json', 'Content-Length': cont_len})
    f = urllib.request.urlopen(req)
    response = f.read()
    f.close()

def save_pid_params(p, i, d):
    try:
        dp = "cooker_pid_p value={}".format(p).encode('ascii')
        save_data(dp)
        di = "cooker_pid_i value={}".format(i).encode('ascii')
        save_data(di)
        dd = "cooker_pid_d value={}".format(d).encode('ascii')
        save_data(dd)

    except Exception as e:
        print ("Failed to push temperature")
        print (e)

def saveCookerPower(p):
    try:
        url = influx_host
        data = "cooker_power value={}".format(p).encode('ascii')

        cont_len = len(data)
        req = urllib.request.Request(url, data, {'Content-Type': 'application/json', 'Content-Length': cont_len})
        f = urllib.request.urlopen(req)
        response = f.read()
        f.close()
    except Exception as e:
        print ("Failed to push status")
        print (e)
        
setpoint = 64.0 # default, and best temperature for chicken breast

pwm_cycle = 3 # in sec.
new_controller = GPIO.PWM(cooker_pin, 0.3) # 0.3Hz
new_controller.start(0)

# tuned parameters
kp = 2.0
ki = 5.0
kd = 140.0
i_hist_size = 500
d_hist_size = 20
i_clamp = 0.4
d_clamp = 3
pid = CookerFeedbackController.CookerFeedbackController(setpoint, kp, ki, i_hist_size, i_clamp, kd, d_hist_size, d_clamp, save_pid_params)

def setCookerPower(p):
    new_controller.ChangeDutyCycle(p * 100)
    saveCookerPower(p)

def _on_exit():
    print ("at exit")
    redis_db.set('cooker_current_temperature', '-1')
    turn_off()
    controller.stop()
    time.sleep(1)
    GPIO.cleanup()
    print ("exit handler triggered")
    time.sleep(1)

def on_exit(sig, func=None):
    _on_exit()

# register function to run before shutdown
import signal
signal.signal(signal.SIGTERM, on_exit)
atexit.register(_on_exit)

running = True

sensor = W1ThermSensor()

while(running):
    
    new_setpoint = 0.0
    try:
        new_setpoint = float(redis_db.get('cooker_target_temperature'))
    except ValueError:
        new_setpoint = 0.0

    if (new_setpoint > 0 and new_setpoint != setpoint):
        print ("setpoint updated from " + str(setpoint) + " to " + str(new_setpoint))
        setpoint = new_setpoint

    pid.setTarget(setpoint)

    try:    
        tc = 0
        output = 0
        try:
            temp_ds18 = 0.0
            for sensor in W1ThermSensor.get_available_sensors():
                print("Sensor %s has temperature %.2f" % (sensor.id, sensor.get_temperature()))
                if (sensor.id == "xxxxxxxxxxxx"): # sensor's ID
                    temp_ds18 = sensor.get_temperature()
                    break

            if (temp_ds18 == 0.0):
                print("Warning: temperature is 0.0f.")

            sys.stdout.write(" done. ")
            sys.stdout.flush

            pid.setCurrentTemperature(temp_ds18)

            # save current temperature
            if temp_ds18 > 1.0:
                redis_db.set('cooker_current_temperature', str(temp_ds18))

            save_temperature(temp_ds18, "temp_ds18")
            save_setpoint(setpoint);

            power = pid.calcCookerPower()
            print("power: " + str(power))
            setCookerPower(power)
        except:
            print ("Unexpected error." + sys.exc_info()[0])

    except KeyboardInterrupt:
        running = False
        turn_off()
        controller.stop()
        time.sleep(1)
        

    time.sleep(1)

thermocouple.cleanup()


