#!/usr/bin/python3
import redis
import sys

argvs = sys.argv
if (len(argvs) < 2):
    print ("specify target temerature for first argument.")
    exit

r = redis.Redis(host='127.0.0.1', port=6379, db=0)

# check argument
try:
    tmp = float(argvs[1])
except ValueError:
    print ("Invalid argument. specify float value.")
    exit

if (r.set('cooker_target_temperature', argvs[1])):
    print ("succeed.")
else:
    print ("failed to set value")


print (b"setpoint: " + r.get('cooker_target_temperature'))
