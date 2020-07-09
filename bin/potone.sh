#!/bin/bash

if [ $# -ne 1 ];then
    echo "Usage: ./potone.sh start"
    echo "       ./potone.sh stop"
    exit 1
fi

qjack_pcount=$(ps -ef | grep -i "jackdbus" | grep -v "grep" | wc -l)
qsynth_pcount=$(ps -ef | grep -i "qsynth" | grep -v "grep" | wc -l)
potone_pcount=$(ps -ef | grep -i "potone.py" | grep -v "grep" | wc -l)

if [ $1 = "start" ];then

    if [ "$qjack_pcount" -le 0 ];then
        jack_control start
        sleep 3
    else
        echo "jackd is running"
    fi
    if [ "$qsynth_pcount" -le 0 ];then
        qsynth &
        sleep 10
    else
        echo "qsynth is running"
    fi
    if [ "$potone_pcount" -le 0 ];then
        python3 ${HOME}/repo/tatoflam/potone/potone.py 
    else
        echo "python3 potone.py is runnig"
    fi

elif [ $1 = "stop" ];then
    if [ "$qjack_pcount" -eq 1 ];then
	qjack_pid=$(ps -ef | grep -i "jackdbus" | grep -v "grep" | awk '{print($2)}')
	echo "jackd process: "$qjack_pid""
	kill -9 "$qjack_pid"
	echo "killed $qjack_pid"
    elif [ "$qjack_pcount" -ge 2 ];then
	echo "More than 2 processes of qjack. Check it up."
    fi
    if [ "$qsynth_pcount" -eq 1 ];then
        qsynth_pid=$(ps -ef | grep -i "qsynth" | grep -v "grep" | awk '{print($2)}')
	echo "qsynth process: "$qsynth_pid""
	kill -9 $qsynth_pid
	echo "killed $qsynth_pid"
    elif [ "$qsynth_pcount" -ge 2 ];then
	echo "More than 2 processes of qsynth. Check it up."
    fi

#    if [ "$potone_pcount" -eq 1 ];then
#	potone_pid=$(ps -ef | grep -i "potone.py" | grep -v "grep" | awk 'print($2)'
#	echo "potone process: "$potone_pid""
#	kill -9 $potone_pid
#	echo "killed $potone_pid"
#    elif [ "$potone_pcount" -ge 2 ];then
#	echo "More than 2 processes of potone. Check it up."
#    fi
fi    
