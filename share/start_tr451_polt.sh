#!/bin/bash
#set -x

# XXX temporarily (a) install gdb/valgrind and (b) edit polt.cli to replace
#     ONUSIM with cterm1 IP address

EXE=`which $0`
START_DIR=`dirname $EXE`
export LD_LIBRARY_PATH=$START_DIR/lib:$LD_LIBRARY_PATH

PREFIX=
if [ "$1" = "gdb" ]; then
    apt-get update && apt-get --yes install gdb
    shift
    RUN=
    if [ "$1" = "run" ]; then
        RUN="--eval-command=run"
        shift
    fi
    PREFIX="gdb $RUN --args"
elif [ "$1" = "valgrind" ]; then
    apt-get update && apt-get --yes install valgrind
    PREFIX="valgrind"
    shift
fi

CTERM1=$(getent ahostsv4 cterm1 | sed -ne 's/ *DGRAM//p')
sed -e "s/ONUSIM/$CTERM1/" /app/share/polt.cli >/app/share/polt.cli.tmp

$PREFIX $START_DIR/tr451_polt_daemon $*
