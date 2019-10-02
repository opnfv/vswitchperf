#!/bin/bash

#This script will used to prepare local host to use vsperf client and containers.

#first change the permission for prepare.sh file 
chmod a+x prepare.sh

#Install python3 for local host
sudo apt-get install python3

#Install python3-pip 
sudo apt-get install python3-pip

#Install grpcio, grpcio-tools and configparser
pip3 install grpcio==1.4.0 grpcio-tools==1.4.0 configparser

#copy libs/proto into client at appropriate location.
cp -r libs/proto client/proto

#copy libs/proto and libs/utils into deployment and testcontrol containers at appropriate location.
cp -r libs/proto deployment/interactive/controller/vsperf/proto
cp -r libs/utils deployment/interactive/controller/vsperf/utils
cp -r libs/proto testcontrol/interactive/controller/vsperf/proto
cp -r libs/utils testcontrol/interactive/controller/vsperf/utils

#copy libs/utils into deployment and testcontrol auto containers at appropriate location.
cp -r libs/utils deployment/auto/controller/vsperf/utils
cp -r libs/utils testcontrol/auto/controller/vsperf/utils
