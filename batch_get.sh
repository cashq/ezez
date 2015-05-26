#!/bin/bash
#http://easyfm.azurewebsites.net/mod.cri.cn/eng/ez/morning/2014/ezm140620.mp3

for (( i=1; i<2; i++ ))
do
    mon=$i
    for (( j=9; j<31; j++ ))
    do
        day=$j
        ./ezez.py -o ~/Music/ezmorning/podcast/output -y 2015 -m $mon -d $day -a ~/Music/ezmorning/podcast/thumb.jpg
    done
done
