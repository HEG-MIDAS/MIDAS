#!/bin/bash
echo "Starting Runner Job"  >> /proc/1/fd/1
YDate=$(date -d "yesterday" +'%Y-%m-%d')
python /app/Climacity/climacity.py -s $YDate -e $YDate >> /proc/1/fd/1
echo "Sleeping for 60 seconds"  >> /proc/1/fd/1
sleep 60
python /app/SABRA/sabra.py -s $YDate -e $YDate >> /proc/1/fd/1
