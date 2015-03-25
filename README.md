## cooker-daemon

A daemon to keep temperature in slow cooker for Raspberry Pi.  
This script checks temperature from MAX31855 and controls relay-connected slow cooker.

### Dependency

- Redis server and python3-redis
- [MAX31855 driver for Raspberry Pi](https://github.com/Tuckie/max31855) is required to run this code.

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

```
./set-target-temperature.py 70
```

