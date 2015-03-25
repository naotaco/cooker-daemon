#!/usr/bin/python
import RPi.GPIO as GPIO
import time
import sys
import atexit

atexit.register(GPIO.cleanup)

pin = 35 # as board
GPIO.setmode(GPIO.BOARD)
GPIO.setup(pin, GPIO.OUT)

command = sys.argv[1]

if (command == 'on'):
    GPIO.output(pin, True)
    print ("Turing on")
elif (command == 'off'):
    GPIO.output(pin, False)
    print ("Turning off")

while 1:
    time.sleep(100)

print("Program exit\n")

