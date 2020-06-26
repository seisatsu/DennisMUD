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
# Some messages during Dennis shutdown won't make it to STDOUT if this script is ended by signal.
# Check the log.
# Usage: ./run.sh <start/restart/stop>
# Background Start: nohup ./run.sh start &

python3="python3.7"                    # Python3 executable name.
syspath="/home/seisatsu/Source/Dennis" # The absolute path to the Dennis folder.
sysuser="seisatsu"                     # Make sure we are running as this user, or else exit.
pidfile="run.sh.pid"                   # File for storing this script's PID, relative or absolute.
lckfile="dennis.lock"                  # Lock file so we don't run twice, relative or absolute.

# Check user.
if [ "$(whoami)" != "$sysuser" ]; then
    echo "Script must be run as user: $sysuser"
    exit 1
fi

# Change to Dennis directory, or exit if impossible.
cd "$syspath" || exit 1

# Trap SIGINT and SIGTERM to clean up lock file and pid file.
trap 'rm -f $lckfile $pidfile; echo "Run script terminating."; exit 0' 2 15

# Save PID of this script, enter infinite loop of starting Dennis if it exits,
# and send the output to the log file. Make a lock file.
if [ "$1" = "start" ]; then
    if [ -f "$lckfile" ]; then
        echo "Lockfile exists. Is Dennis already running? Not starting."
        exit 1
    fi
    touch "$lckfile"
    echo "Starting Dennis..."
    echo $$ > "$pidfile"
    while true; do
        $python3 server.py
        echo "Dennis stopped, restarting in 2 seconds..."
        sleep 2
    done
    exit 0 # as if
fi

# Restart Dennis by stopping it while leaving the parent script running.
if [ "$1" = "restart" ]; then
    if [ ! -f "$pidfile" ]; then
        echo "Dennis does not appear to be running."
        exit 1
    fi
    echo "Restarting Dennis..."
    currpid=$(cat "$pidfile")
    dnnspid=$(pgrep -x -P "$currpid" "$python3")
    kill "$dnnspid"
    exit 0
fi

# Stop Dennis by stopping it and the parent script. Remove the lockfile.
if [ "$1" = "stop" ]; then
    if [ ! -f "$pidfile" ]; then
        echo "Dennis does not appear to be running."
        exit 1
    fi
    echo "Stopping Dennis..."
    currpid=$(cat "$pidfile")
    dnnspid=$(pgrep -x -P "$currpid" "$python3")
    kill "$dnnspid"
    sleep 2
    kill "$currpid"
    rm -f "$lckfile" "$pidfile" # Most likely this already happened in the signal trap.
    exit 0
fi

# We didn't get a recognizable option.
echo "Invalid or no arguments."
echo "Usage: ./run.sh <start/restart/stop>"
exit 1
