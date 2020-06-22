#!/bin/sh

#####################
# Dennis MUD        #
# run.sh            #
# Copyright 2020    #
# Michael D. Reiley #
#####################

# **********
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to
# deal in the Software without restriction, including without limitation the
# rights to use, copy, modify, merge, publish, distribute, sublicense, and/or
# sell copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS
# IN THE SOFTWARE.
# **********

# This is a quick and dirty script to run Dennis and restart in a couple seconds if it crashes,
# while also keeping a log and PID file. It should work on any sane Linux/Unix system.
# Usage: ./run.sh <start/restart/stop>
# Background Usage: nohup ./run.sh <start/restart/stop> &

syspath="/home/seisatsu/Source/Dennis" # The absolute path to the Dennis folder.
sysuser="seisatsu"                     # The user Dennis will run as.
logname="dennis.log"                   # The name of the log file, relative or absolute.
pidfile="run.sh.pid"                   # File for storing this script's PID, relative or absolute.
lckfile="dennis.lock"                  # Lock file so we don't run twice, relative or absolute.

cd $syspath

# Check user.
if [ "$(whoami)" != "$sysuser" ]; then
    echo "Script must be run as user: $sysuser"
    exit 1
fi

# Save PID of this script, enter infinite loop of starting Dennis if it exits,
# and send the output to the log file. Make a lock file.
if [ "$1" = "start" ]; then
    if [ -f "$lckfile" ]; then
        echo "Lockfile exists. Is Dennis already running? Not starting."
        exit 1
    fi
    touch $lckfile
    echo "Starting Dennis..."
    echo $$ > $pidfile
    while true; do
        python3 server.py 2>&1 | tee -a $logname
        echo "Dennis stopped, restarting in 2 seconds..."
        sleep 2
    done
    exit 0 # as if
fi

# Restart Dennis by stopping it while leaving the parent script running.
if [ "$1" = "restart" ]; then
    echo "Restarting Dennis..."
    currpid=`cat $pidfile`
    dnnspid=`pgrep -P $currpid | head -n1`
    kill $dnnspid
    exit 0
fi

# Stop Dennis by stopping it and the parent script. Remove the lockfile.
if [ "$1" = "stop" ]; then
    echo "Stopping Dennis..."
    currpid=`cat $pidfile`
    dnnspid=`pgrep -P $currpid | head -n1`
    kill $dnnspid
    sleep 2
    kill $currpid
    rm $lckfile
    exit 0
fi

# We didn't get a recognizable option.
echo "Invalid or no arguments."
echo "Usage: ./run.sh <start/restart/stop>"
echo "Background Usage: nohup ./run.sh <start/restart/stop> &"
exit 1
