#!/usr/bin/env bash
# to be executed in the same durectory as ponicwatch.py i.e. the executable part of the project
CWD=$(dirname $(readlink -f $BASH_SOURCE))
_IP=$(hostname -I | awk '{print $1}')
rc=0
PID=$(cat "$CWD"/ponicwatch.pid)
# See how we were called.
case "$1" in
start)
    export WORKON_HOME=$HOME/.virtualenvs
    source $WORKON_HOME/ponicwatch/bin/activate

    sudo pigpiod

    cd "$CWD"
    python ponicwatch.py -s local_ponicwatch.db -d2 -b $_IP > "$CWD"/../Private/ponicwatch.log 2>&1 &
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
