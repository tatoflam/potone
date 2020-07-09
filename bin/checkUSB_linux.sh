#!/bin/bash

for device in $(ls -1 /dev | grep -i usb)
do
    serial=`udevadm info -q property -n /dev/${device} | grep -E "ID_SERIAL_SHORT="`
    printf "/dev/%s %s\n" ${device} ${serial}
done
