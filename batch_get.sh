#!/bin/bash
#http://easyfm.azurewebsites.net/mod.cri.cn/eng/ez/morning/2014/ezm140620.mp3

for (( i=1; i<12; i++ ))
do
    mon=$i
    for (( j=1; j<32; j++ ))
    do
        day=$j
        ./ezez.py -o output -y 2014 -m $mon -d $day -a ./thumb.jpg
    done
done
