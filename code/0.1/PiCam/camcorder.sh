#!/bin/sh

if [ $# -ne 2 ]; then
    echo 'Incorrect Usage!'
    echo 'sh camcorder.sh <N Images> <Sleep>'
    exit
fi

for i in `seq 1 $1`; do
    echo 'Snapping Image '$i'/'$1
    python picam.py snap_save 192.168.1.229
    sleep $2; clear;
done

# EOF