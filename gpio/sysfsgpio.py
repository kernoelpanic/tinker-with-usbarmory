#!/usr/bin/env python

from select import poll, POLLERR, POLLPRI
from os import system
from time import sleep 
import sys

flag = False

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

fvalue = "/sys/class/gpio/gpio158/value"
#TODO: set edge
#fedge = "/sys/class/gpio/gpio158/edge"

#TODO: check for files 
fp = open(fvalue, "r")

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
