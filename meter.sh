#!/bin/bash
export PATH="/bin:/sbin:/usr/sbin:/usr/bin:/usr/local/bin"
# Water meter
# B0:79:94:F1:7A:8C
#
PWD=`pwd`
WORKDIR=/Users/yamato/OneDrive/WaterMeterLogs
cd $WORKDIR
printf "\n\n----------------------------\n  "
date +"%F %H:%M:%S"
printf "\nTurning on LED...\n"
curl --connect-timeout 10 --retry 10 http://10.0.1.4:8080/enabletorch
sleep 10
printf "\nTurning on LED...(again!)\n"
curl --connect-timeout 10 --retry 10 http://10.0.1.4:8080/enabletorch
sleep 1
printf "\nTurning on Autofocus...\n"
curl --connect-timeout 10 --retry 5 http://10.0.1.4:8080/focus 
sleep 3
DATE=`date +%F_%H_%M`
RAW=raw_$DATE.jpg
READING=reading_$DATE.jpg
printf "\nTaking a photo...\n"
curl --connect-timeout 10 --retry 5 http://10.0.1.4:8080/photo.jpg -o $RAW 
sleep 1
printf "\nTurning off Autofocus...\n"
curl --connect-timeout 10  --retry 5 http://10.0.1.4:8080/nofocus
sleep 1
printf "\nTurning off LED...\n"
curl --connect-timeout 10 --retry 5 http://10.0.1.4:8080/disabletorch
printf "\nCropping the photo...\n"
# convert $RAW -rotate 86.5 -crop 480x160+385+120 -colorspace gray $READING
convert $RAW -rotate 86.5 -crop 480x160+330+240 -colorspace gray $READING
cd $PWD
    