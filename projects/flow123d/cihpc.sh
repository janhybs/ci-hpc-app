#!/bin/bash


WORKDIR=/storage/liberec3-tul/home/jan-hybs/ci-hpc
PIDFILE=$WORKDIR/".ci-hp.-pidfile"
LOGFILE=$WORKDIR/.log
LOGSIZE=30
RED=`tput setaf 1`
GREEN=`tput setaf 2`
YELLOW=`tput setaf 3`
BLUE=`tput setaf 5`
RESET=`tput setaf 7`
PROGRAM="sleep 2"
PROGRAM="python3 src/cihpc/worker/schedule_worker.py -c projects/flow123d/config.yaml"
SCHEDULE="python3 src/cihpc/scheduler/scheduler.py   -c projects/flow123d/config.yaml --rnd=.jenkins.latest --per-branch 20"
ACTION=status
cd $WORKDIR

while [[ $# -gt 0 ]]
    do
    key="$1"

    case $key in
        -h|--help|help)
            echo "status, start, stop, restart, debug, log [-n LINES], schedule, check"
            exit 0
            ;;
        --status|status)
            ACTION="status"
            shift
            ;;
        --start|start)
            ACTION="start"
            shift
            ;;
        --stop|stop)
            ACTION="stop"
            shift
            ;;
        --restart|restart)
            ACTION="restart"
            shift
            ;;
        --debug|debug)
            ACTION="debug"
            shift
            ;;
        --schedule|schedule|plan)
            ACTION="schedule"
            shift
            ;;
        --check|check)
            ACTION="check"
            shift
            ;;
        --log|log)
            ACTION="log"
            shift
            ;;
        -n)
            LOGSIZE="$2"
            shift
            shift
            ;;
        *)
            shift # past argument
            ;;
    esac
done


pid=`cat $PIDFILE`


function getStatus() {
    # read pidfile
    # ps -p $pid -o pid,state,time,command

    if ps -p ${pid} > /dev/null
        then
            echo -e "${GREEN}•${RESET} service [$pid] is running"
        else
            echo -e "${RED}•${RESET} service [$pid] is not running"
    fi
}

function checkService() {
    if ps -p ${pid} > /dev/null
        then
            echo -e "${GREEN}•${RESET} service [$pid] is running"
        else
            echo -e "${RED}•${RESET} service [$pid] is not running"
            startService
    fi
}

function getLog() {
    echo -e "${BLUE}last $LOGSIZE lines of log${RESET}"
    echo -e "${YELLOW}===============================================================${RESET}"
    tail -n $LOGSIZE $LOGFILE 
    echo -e "${YELLOW}===============================================================${RESET}"
}


function startService() {
    source env.sh
    echo -e "${YELLOW}•${RESET} starting service"
    echo -e "${YELLOW}•${RESET} running: $PROGRAM"
    $PROGRAM > $LOGFILE 2>&1 &
    pid=$!
    echo -e "${GREEN}•${RESET} started process [$pid]"
    echo -e $pid > $PIDFILE
    getStatus
}

function stopService() {
    echo -e "${YELLOW}•${RESET} stopping service [$pid]"
    kill -9 $pid
    echo -e "${RED}•${RESET} process stopped [$pid]"
    echo -e $pid > $PIDFILE
    getStatus;
}

if [[ $ACTION == "status" ]]; then
    getStatus;
fi

if [[ $ACTION == "log" ]]; then
    getLog;
fi

if [[ $ACTION == "start" ]]; then
    startService;
fi

if [[ $ACTION == "stop" ]]; then
    stopService;
fi

if [[ $ACTION == "restart" ]]; then
    stopService;
    startService;
fi

if [[ $ACTION == "schedule" ]]; then
    source env.sh
    $SCHEDULE
fi

if [[ $ACTION == "check" ]]; then
    checkService;
fi


if [[ $ACTION == "debug" ]]; then
    stopService
    source env.sh
    echo -e "${YELLOW}•${RESET} starting service live"
    echo -e "${YELLOW}•${RESET} running: $PROGRAM"
    $PROGRAM
fi

