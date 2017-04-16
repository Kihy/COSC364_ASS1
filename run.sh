#!/bin/sh
for conf_file in ${1}/*.txt
do

  gnome-terminal -e "python3 main.py $conf_file"& 

done
