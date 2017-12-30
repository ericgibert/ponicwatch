#!/bin/sh -e
# modify below the path of the first /ponicwatch folder:
export PROJECT_HOME=$HOME/ponicwatch

_IP=$(hostname -I)
echo "My IP:" $_IP

export WORKON_HOME=$HOME/.virtualenvs
source $WORKON_HOME/ponicwatch/bin/activate

sudo pigpiod

cd $PROJECT_HOME/ponicwatch
python ponicwatch.py -s local_ponicwatch.db -d2 -b $_IP > $PROJECT_HOME/Private/ponicwatch.log 2>&1 &

exit 0
