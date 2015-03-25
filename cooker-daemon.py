#!/usr/bin/python3

import time
from datetime import datetime

import sys
sys.path.append('/etc/cooker/max31855')
from max31855 import MAX31855, MAX31855Error

import atexit
import RPi.GPIO as GPIO

# setup pin numbers
cooker_pin = 35 # pin number connected to relay for the cooker
cs_pin = 24 # MAX31855's chip select
clock_pin = 23
data_pin = 21
units = "c" # Fahrenheight? what's that?

GPIO.setmode(GPIO.BOARD) # it seems default mode doesn't work on RPi2
GPIO.setup(cooker_pin, GPIO.OUT)

def turn_on():
    GPIO.output(cooker_pin, True)

def turn_off():
    GPIO.output(cooker_pin, False)

def _on_exit():
    print ("at exit")
    turn_off()
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



log_file_name = "/etc/cooker/log/log_" + datetime.now().isoformat() + ".txt"
logfile = open(log_file_name, "w")
print ("log file: " + log_file_name)

thermocouple = MAX31855(cs_pin, clock_pin, data_pin, units, GPIO.BOARD)

# setpoint = 64.0 # default, and best temperature for chicken breast
setpoint = 80

running = True
while(running):

    try:    
        tc = 0
        output = 0
        try:
            tc = thermocouple.get()
            # print ("tc: {}".format(tc))
            if (tc < setpoint):
                # print ("turing on")
                turn_on()
                output = 1
            else:
                # print ("turning off")
                turn_off()
                output = 0
        
        except MAX31855Error as e:
            # print ("Error: " + e.value)
            output = -1

        log_text = datetime.now().isoformat(), str(tc), str(setpoint), str(output)
        # print ('\t'.join(log_text))
        logfile.write('\t'.join(log_text).replace("T", "\t") + "\n")

    except KeyboardInterrupt:
        running = False
        turn_off()
        time.sleep(1)
        

    time.sleep(1)

thermocouple.cleanup()
