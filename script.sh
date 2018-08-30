#! /bin/bash

function openfiles(){
    lsof -p $1 | wc -l
}
export -f openfiles
./portscanner.py > output 2> output &
watch -n 0.1 -x bash -c "openfiles $!"
