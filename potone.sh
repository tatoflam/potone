#!/bin/bash

qjack_pid=$(ps -ef | grep -i "qjackctl" | grep -v "grep" | wc -l)
qsynth_pid=$(ps -ef | grep -i "qsynth" | grep -v "grep" | wc -l)
potone_pid=$(ps -ef | grep -i "potone.py" | grep -v "grep" | wc -l)

if [ "$qjack_pid" -le 0 ]; then
    qjackctl &
else
    echo "qjackctl is running"
fi
if [ "$qsynth_pid" -le 0 ]; then
    qsynth &
else
    echo "qsynth is running"
fi
if [ "$potone_pid" -le 0 ]; then
    python3 ${HOME}/repo/tatoflam/potone/potone.py 
else
    echo "python3 potone.py is runnig"
fi
