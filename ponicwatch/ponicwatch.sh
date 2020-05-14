#!/usr/bin/env bash
### BEGIN INIT INFO
# Provides:          ponicwatch.sh
# Required-Start:    $remote_fs $syslog
# Required-Stop:     $remote_fs $syslog
# Default-Start:     2 3 4 5
# Default-Stop:      0 1 6
# Short-Description: Start ponicwatch daemon at boot time
# Description:       Enable service provided by daemon.
### END INIT INFO
# https://www.dexterindustries.com/howto/run-a-program-on-your-raspberry-pi-at-startup/
# to be executed in the same directory as ponicwatch.py i.e. the executable part of the project
#CWD=$(dirname $(readlink -f $BASH_SOURCE))
CWD=/home/pi/ponicwatch/ponicwatch
_IP=$(hostname -I | awk '{print $1}')
#if [ -n $_IP ]; then
#_IP=10.0.10.218
#fi
rc=0
PID=$(cat $CWD/ponicwatch.pid)
# See how we were called.
case "$1" in
start)
    export WORKON_HOME=/home/pi/.virtualenvs
    source $WORKON_HOME/ponicwatch/bin/activate

    sudo pigpiod

    cd $CWD
    /home/pi/.virtualenvs/ponicwatch/bin/python $CWD/ponicwatch.py -s $CWD/local_ponicwatch.db -d2 -b $_IP > $CWD/../Private/ponicwatch.log 2>&1 &
    echo http://$_IP:8080
    ;;
stop)
    kill -10 $PID
    ;;
status)
    echo "Current IP:" $_IP
    echo "Ponicwatch pid:" $PID
    ps -fp $PID
    ;;
restart|reload|force-reload)
    $0 stop
    $0 start
    rc=$?
    ;;
*)
    echo $"Usage: $0 {start|stop|status|restart|reload|force-reload}"
    exit 2
esac

exit $rc
