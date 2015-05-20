# tinker-with-USBarmory #
This repository includs some documentation and examples for [USBarmory][1]. Everything here is just a braindump - use with caution!

Since the USBarmory can also be used as a ''host'' device, it is sometimes difficult to disdiguish textually between **U**SBarmory and the host **c**omputer (or **c**lient) armory is pluged into. To indicate on which device a command was entered we use the prefix **U$** and **C$** for bash commands e.g.
* `U$` marks commands executed on the shell of USBarmory 
* `C$` marks commands executed on the shell of the client/computer USBarmory is plugged into


## Modes of operation ##

The main modes of operation of USBarmory are:
* [CDC ethernet over USB](#cdc-ethernet-over-usb)
* [Mass storage](#mass-storage)
* [Mass storage and CDC ethernet](#mass-storage-and-cdc-ethernet)

### CDC ethernet over USB 
This mode enabls access to the USBarmory via network e.g. ssh. 

#### USBarmory config
```shell
U$ vim /etc/modules
g_ether use_eem=0 dev_addr=aa:bb:cc:dd:ee:f1 host_addr=aa:bb:cc:dd:ee:f2
```

Default config of `/etc/modules` in the default debian image:
```shell
# /etc/modules: kernel modules to load at boot time.
#
# This file contains the names of kernel modules that should be loaded
# at boot time, one per line. Lines beginning with "#" are ignored.
# Parameters can be specified after the module name.

ledtrig_heartbeat
ci_hdrc_imx
g_ether use_eem=0 dev_addr=1a:55:89:a2:69:41 host_addr=1a:55:89:a2:69:42
```

#### Host config

To initially connect via **SSH** to the USBarmory the following default credetials are used:
```
user: usbarmory
pass: usbarmory
```
The following commands are used to setup the interface on the **Host**.  
```
H$ /sbin/ip link set usb0 up
H$ /sbin/ip addr add 10.0.0.2/24 dev usb0
H$ ssh -l usbarmory 10.0.0.1 

# network forwarding to access internet with armory
H$ /sbin/iptables -t nat -A POSTROUTING -s 10.0.0.1/32 -o wlan0 -j MASQUERADE
H$ echo 1 > /proc/sys/net/ipv4/ip_forward
```

### Mass storage 
This describes how to configure usbarmory as a usb mass storage device. 
As a consequence it will be detected by your host computer as a ''normal'' usb stick.

```shell
U$ vim /etc/modules
ledtrig_heartbeat
ci_hdrc_imx

g_mass_storage file=/disk.img
```

The disk image can be created first as follows... 
```shell
U$ dd if=/dev/zero of=/disk.img bs=1M count=256
U$ mkfs.ext2 /disk.img
U$ sudo mount -o loop /disk.img /mnt/disk
```
This appraoch works, BUT the host system will not automatically
mount the storage device since it does not contain a valid partition table.
Nevertheless you can mount the storage device manually on the host device.
```shell
C$ mount /dev/sdb /mnt/disk
```

To avoid this create a partition on the ''storage device''
```shell
C$ fdisk /dev/sdb
# create a partition
C$ mkfs.vfat /dev/sdb1   
```

To mount the *disk.img* on the usbarmory successfully if it holds a partition,
some [extra steps][2] are required:
```shell
U$ fdisk -l /disk.img 

Disk /disk.img: 268 MB, 268435456 bytes
1 heads, 2 sectors/track, 262144 cylinders, total 524288 sectors
Units = sectors of 1 * 512 = 512 bytes
Sector size (logical/physical): 512 bytes / 512 bytes
I/O size (minimum/optimal): 512 bytes / 512 bytes
Disk identifier: 0x2b3a8b68

    Device Boot      Start         End      Blocks   Id  System
/disk.img1   *        2048      524287      261120    b  W95 FAT32

U$ mount -o loop,offset=$((2048 * 512)) /disk.img /mnt/disk
```

### Mass storage and CDC ethernet 
To use usbarmory as usb storage and via CDC ethernet in paralell, the following
settings are required on the usbarmory config:

```
U$ vim /etc/modules
ledtrig_heartbeat
ci_hdrc_imx

g_multi use_eem=0 dev_addr=1a:55:89:a2:69:41 host_addr=1a:55:89:a2:69:42 file=/disk.img
```

## FTDI serial connection ##
**TODO**

```shell
# connect to UART 
$ screen /dev/ttyUSB0 115200
```

## Configure USBarmory ##

### add user
```
U$ adduser aljosha
[...]
U$ sudo vim /etc/group
[...]
sudo:x:27:aljosha
[...]
```

### ntpdate & 'missing btime in /proc/stat'
This proble is caused due to missing hw-clock and ''back-in-time'' travel.
```shell
U$ ntpdate 0.at.pool.ntp.org #to get some current time
```

### GPIO 

The standard GPIO example from the homepage works via sysfs.
```
U$ echo 158 > /sys/class/gpio/export             # 128 (GPIO5[0]) + 30 = GPIO5[30]
U$ echo out > /sys/class/gpio/gpio158/direction
U$ echo 1 > /sys/class/gpio/gpio158/value
U$ echo 0 > /sys/class/gpio/gpio158/value
U$ echo 158 > /sys/class/gpio/unexport
```

To use a pin as input an react up-on changing values, a code sample can be found in



## References

* USBarmory doku 
https://github.com/inversepath/usbarmory/wiki/GPIOs

* USBarmory google groups
https://groups.google.com/forum/#!topic/usbarmory/1mIQI0h_UEk

* Kernel GPIO dokumentation
https://www.kernel.org/doc/Documentation/gpio/gpio.txt
https://www.kernel.org/doc/Documentation/gpio/sysfs.txt
http://www.mjmwired.net/kernel/Documentation/gpio.txt

* OpenWRT
http://wiki.openwrt.org/doc/hardware/port.gpio

<!--- 
internal references 
-->

[1]: http://www.inversepath.com/usbarmory.html
[2]: http://madduck.net/blog/2006.10.20:loop-mounting-partitions-from-a-disk-image/
