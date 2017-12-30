#!/usr/bin/env bash
# verifies all the necessary packages
export WORKON_HOME=$HOME/.virtualenvs
source $WORKON_HOME/ponicwatch/bin/activate

for package in 'bottle' 'APScheduler' 'Markdown' 'matplotlib' 'pigpio'
    do
        echo "Package" $package
        pip search $package | grep 'INSTALLED\|LATEST'
    done