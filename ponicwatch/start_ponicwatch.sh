#!/bin/sh -e

sudo pigpiod

export WORKON_HOME=$HOME/.virtualenvs
export PROJECT_HOME=$HOME

_IP=$(hostname -I)
echo "My IP:" $_IP
cd /home/pi/ponicwatch/ponicwatch
/home/pi/.virtualenvs/ponicwatch/bin/python ponicwatch.py -s local_ponicwatch.db -d2 -b $_IP >> /home/pi/ponicwatch/Private/ponicwatch.log 2>&1 &

exit 0
