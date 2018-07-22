## cooker-daemon

A daemon to keep temperature of slow cooker runs on for Raspberry Pi.  
This script checks temperature from DS18B20 and controls relay to on/off connected slow cooker.

### Dependency

- Redis server and python3-redis
- [RPi.GPIO](https://pypi.org/project/RPi.GPIO/)
- [W1ThermSensor](https://github.com/timofurrer/w1thermsensor)
- urllib, json, etc.

### Usage

Don't forget to make it executable.

#### Run directly

```
$ sudo ./cooker-daemon.py
```

Ctrl-C to stop.


#### Run as daemon

Using Supervisor is recommended.

```
# /etc/supervisor/conf.d/cooker.conf
[program:cooker]
command=/etc/cooker/script/cooker-daemon.py
process_name=%(program_name)s_%(process_num)02d
numprocs=1
autostart=false
autorestart=true
redirect_stderr=true
```

#### Set target temperature from outside

Use bundled script.

```
./set-target-temperature.py 70
```

