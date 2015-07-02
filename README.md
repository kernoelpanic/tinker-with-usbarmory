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
* [Host](#host)

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

### Host
**TODO**

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
The USBarmory exposes GPIO via sysfs to userspace. Documentation on Linux GPIO
can be found here:
* [gpio][4]
* [gpio-legacy][5]
* [gpio-sysfs][3]

The standard GPIO example from the homepage works via sysfs.
```shell
U$ echo 158 > /sys/class/gpio/export             # 128 (GPIO5[0]) + 30 = GPIO5[30]
U$ echo out > /sys/class/gpio/gpio158/direction
U$ echo 1 > /sys/class/gpio/gpio158/value
U$ echo 0 > /sys/class/gpio/gpio158/value
U$ echo 158 > /sys/class/gpio/unexport
```

To read some `value` from a GPIO pin the direction has to be set to `in`, 
wire your GPIOs properly and observe changes of `value` e.g.
```shell
U$ echo 158 > /sys/class/gpio/export
U$ echo in > /sys/class/gpio/gpio158/direction
U$ watch cat /sys/class/gpio/gpio158/value
U$ echo 158 > /sys/class/gpio/unexport # if your are finished useing
```

To use a pin as input and react up-on changing values, a little bit more is required
for smooth operation. Code sample can be found in [gpio](./gpio).

#### React up-on input change
Now one might be tempted to use **inotify(7)** and its usespace program **inotifywait(1)** 
to monitor changes/events on the `value` file.
```shell
U$ inotifywait -t 5 /sys/class/gpio/gpio158/value
```
BUT this does **not work**. 

> In Linux, everythin is a file...

but some files are more files than others :)

Since `sysfs` is a special sort of memory file system it is not supported by **inotify(7)**.
> Inotify reports only events that a user-space program triggers through the filesystem API.  As a result, it does not  catch
> remote  events  that  occur  on  network filesystems.  (Applications must fall back to polling the filesystem to catch such
> events.)  Furthermore, various pseudo-filesystems such as /proc, /sys, and /dev/pts are not monitorable with inotify.

So we need another approach. How about useing **poll(2)** through python via [select.poll][6].
```python
#!/usr/bin/env python
from select import poll, POLLIN
filename = "/sys/class/gpio/gpio158/value"
file = open(filename, "r")
p = poll()
p.register(file.fileno(), POLLIN)

while True:
    events = p.poll(100)
    for e in events:
        print e
```
BUT this can also **not work**.

Since **poll(2)** is mainly for reading pipes and sockets, `POLLIN` does not quite work
on files since a file will always be ''readable''. Therfore we have to use the configuration described 
in [gpio-sysfs][3].

To react on chaning `values` the documentation of [gpio-sysfs][3] suggests to 
use **poll(2)** for the events `POLLPRI | POLLERR` and 
configure the GPIO pin as interrupt-generating via `edge`. 

> If the pin can be configured as interrupt-generating interrupt
> and if it has been configured to generate interrupts (see the
> description of "edge"), you can poll(2) on that file and
> poll(2) will return whenever the interrupt was triggered. If
> you use poll(2), set the events POLLPRI and POLLERR. [...] After
> poll(2) returns, either lseek(2) to the beginning of the sysfs
> file and read the new value or close the file and re-open it
> to read the value.

So to use **poll(2)** setting an `edge` is required.
> "edge" ... reads as either "none", "rising", "falling", or
> 	"both". Write these strings to select the signal edge(s)
>	that will make poll(2) on the "value" file return.

>	This file exists only if the pin can be configured as an
>	interrupt generating input pin.

To set up a GPIO for useing **poll(2)** the following settings should be made.
```shell
U$ echo 158 > /sys/class/gpio/export
U$ echo in > /sys/class/gpio/gpio158/direction
U$ echo "falling" > /sys/class/gpio/gpio158/edge
```

Now we can use the following python code snippet, a full example can be found in [here](./gpio).
```python
#!/usr/bin/env python
from select import poll, POLLERR, POLLPRI
fvalue = "/sys/class/gpio/gpio158/value"
fp = open(fvalue, "r")
p = poll()
p.register(fp.fileno(), POLLPRI | POLLERR)
i=0

while True:
    events = p.poll(2000)
    while len(events) > 0:
        e = events.pop()
        fp.seek(0) # always start at the beginning of file 
	# always read() the whole file, otherwise we run in endless loop!
        print "Event: ",e," value=",fp.read(-1)[0]," len=",len(events)," i=",i
	i += 1
```

### Randomness

To check if the USBarmory provides solid cryptographically usable randomness we ran some tests:
```
U$ apt-get install dieharder
U$ cat /dev/urandom | ./dieharder -a -g 200
# this gona take a lot of time. 
```
The results can be found in the [./tests](./tests) folder in this repository.
The Test containing `load` in their name have been run while the USBarmory
was under haevy load e.g. compiling stuff. 


For quickly check the currently available entropy:
```
U$ cat /proc/sys/kernel/random/entropy_avail
```

## Examples

### Bitcoin offline/cold storage

Just install [vanitygen][7] as a fast Bitcoin address generator for the command line. 

Install missing dependencies:
```
# in cas of the following error when installing vanity
#  pcre.h: No such file or directory
U$ apt-get install libpcre3-dev
```

To quickly generate an address on the USBarmory the following command can be used:
```shell
U$ ./vanitygen 1btc
Difficulty: 4553521
Pattern: 1btc                                                                  
Address: 1btc8zjDetGAkRRD5JpNdSdpNcxCzymTu
Privkey: 5JrAdQp23Zkqi4NFwSGoh6kftHochz56ctxuFVemX1vy4KozLvV 
```

The following address can now be used to send Bitcoins to it. 

**NOTE:** If you lose the Privkey, your Bitcoins are gone!

**NOTE:** This public/private key pair does not hold any coins - so its not worth a try :)

To use the Bitcoin address/the ECDSA public-private key pair with Bitcoin on an online device,
you can import the private key in an regular `bitoind` client useing the following command:
```shell
C$ ./bitcoin-cli importprivkey 5JrAdQp23Zkqi4NFwSGoh6kftHochz56ctxuFVemX1vy4KozLvV usbarmory
```


### Bitcoin wallet

Download and install [mmgen][6] which is a command line wallet. 


Install missing dependencies for `mmgen`:
```
# in case of following error:
#  Python.h: No such file or directory or directory
U$ apt-get install python-dev
```

#### Install bitcoind manually
```
U$ apt-get install libboost-system-dev libboost-filesystem-dev  libboost-program-options-dev libboost-chrono-dev libboost-test-dev libboost-thread-dev autoconf libtool pkg-config libdb++-dev libdb-dev
# just in case something missing: libboost-dev-all and libglib2.0-dev

# get latest version of bitcoin
U$ git clone https://github.com/bitcoin/bitcoin.git
U$ cd bitcoin
U$ git fetch
# checkout the latest stable branch - we want to be sure :)
U$ git checkout remotes/origin/0.10

# build it 
U$ ./autogen.sh 
# take care that autogen.sh does not report erros regardin
# your locale and LANG settings. If so run: dpkg-reconfigure locales
# Then run configure and deactivate GUI and UPNP. 
# NOTE: If you use the 'with-incompatible-bdb' flag, your 'wallet.dat' will not be 
# compatible with the binary of bitcoind shiped at bitcoin.org.  
U$ ./configure --without-gui --with-incompatible-bdb --without-miniupnpc 
U$ make
```

Start bitcoind:
```
U$ ./bitcoind -daemon -maxconnections=0 -listen=0
```

Now you are free to use `mmgen`

#### mmgen
```
U$ mmgen-walletgen
U$ mmgen-addrgen 89ABCDEF-76543210[256,3].mmdat 1-10
U$ cp '89ABCDEF[1-10].addrs' my.addrs
 
C$ mmgen-addrimport my.addrs
U$ mmgen-tool listaddresses
```

## References

* USBarmory docu 
https://github.com/inversepath/usbarmory/wiki/GPIOs

* USBarmory google groups
https://groups.google.com/forum/#!topic/usbarmory/1mIQI0h_UEk

* Kernel GPIO dokumentation
https://www.kernel.org/doc/Documentation/gpio/gpio.txt
https://www.kernel.org/doc/Documentation/gpio/gpio-legacy.txt
https://www.kernel.org/doc/Documentation/gpio/sysfs.txt

* OpenWRT GPIO
http://wiki.openwrt.org/doc/hardware/port.gpio

* MMGen Bitcoin command line wallet based on bitcoind
https://github.com/mmgen/mmgen

* Bitcoin address generator for command line
https://github.com/samr7/vanitygen

<!--- 
internal references 
-->

[1]: http://www.inversepath.com/usbarmory.html
[2]: http://madduck.net/blog/2006.10.20:loop-mounting-partitions-from-a-disk-image/
[3]: https://www.kernel.org/doc/Documentation/gpio/sysfs.txt
[4]: https://www.kernel.org/doc/Documentation/gpio/gpio.txt
[5]: https://www.kernel.org/doc/Documentation/gpio/gpio-legacy.txt
[6]: https://github.com/mmgen/mmgen/wiki/Install-MMGen-on-Debian-or-Ubuntu-Linux 
[6]: https://docs.python.org/2.7/library/select.html
[7]: https://github.com/samr7/vanitygen
