#!/usr/bin/env python

from select import poll, POLLERR, POLLPRI
from os import system, path
from time import sleep 
import sys

flag = False

GPIO_1 = 152
GPIO_2 = 153
GPIO_3 = 154
GPIO_4 = 155
GPIO_5 = 156
GPIO_6 = 157
GPIO_7 = 158

# sysfs GPIO paths
GPIO_PREFIX = "/sys/class/gpio/"
GPIO_EXP = GPIO_PREFIX + "export"
GPIO_UXP = GPIO_PREFIX + "unexport"

GPIO1 = GPIO_PREFIX + "gpio" + str(GPIO_1) + "/"
GPIO2 = GPIO_PREFIX + "gpio" + str(GPIO_2) + "/" 
GPIO3 = GPIO_PREFIX + "gpio" + str(GPIO_3) + "/"
GPIO4 = GPIO_PREFIX + "gpio" + str(GPIO_4) + "/"
GPIO5 = GPIO_PREFIX + "gpio" + str(GPIO_5) + "/"
GPIO6 = GPIO_PREFIX + "gpio" + str(GPIO_6) + "/"
GPIO7 = GPIO_PREFIX + "gpio" + str(GPIO_7) + "/"
# sysfs GPIO files
GPIO_VAL = "value"
GPIO_EDG = "edge" 
GPIO_DIR = "direction"
# sysfs GPIO direction settings
DIR_IN = "in"
DIR_OUT = "out"
# sysfs GPIO edge settings
EDG_RISE = "rising"
EDG_FALL = "falling"
EDG_NONE = "none"


def setup_gpio():
    if not path.exists(GPIO7):
        try:
            print "Setting GPIO 7"
            with open(GPIO_EXP, "w") as fp:
                fp.write(str(GPIO_7))
            with open(GPIO7 + GPIO_DIR, "w") as fp:
                fp.write(DIR_IN)
            with open(GPIO7 + GPIO_EDG, "w") as fp:
                fp.write(EDG_RISE)
        except:
            raise


def udisk_mount(path):
    global flag
    if (flag):
        return
    flag=True
    system("echo 155 > /sys/class/gpio/export") 
    system("echo out > /sys/class/gpio/gpio155/direction")
    system("echo 1 > /sys/class/gpio/gpio155/value")
    sleep(3)
    system("echo 0 > /sys/class/gpio/gpio155/value")
    system("echo 155 > /sys/class/gpio/unexport") 
    flag=False
    return 

setup_gpio()

fp = open(GPIO7 + GPIO_VAL, "r")

p = poll()
p.register(fp.fileno(), POLLPRI | POLLERR)

i=0
while True:
    events = p.poll(2000)
    while len(events) > 0:
        e = events.pop()
        fp.seek(0)
        print "Event: ",e," value=",fp.read(-1)[0]," len=",len(events)," i=",i    
        sys.stdout.flush()
        i += 1
        udisk_mount("foo")
