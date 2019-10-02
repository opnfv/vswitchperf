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

# Build .proto to create python library
cd libs/proto && python3 -m grpc_tools.protoc -I./ --python_out=. --grpc_python_out=. vsperf.proto
sed -i 's/import vsperf_pb2 as vsperf__pb2/from . import vsperf_pb2 as vsperf__pb2/g' vsperf_pb2_grpc.py
cd ../..

#copy libs/proto and libs/utils in deployment and testcontrol container at appropriate location.
cp -r libs/proto deployment/interactive/controller/vsperf/proto
cp -r libs/utils deployment/interactive/controller/vsperf/utils
cp -r libs/proto testcontrol/interactive/controller/vsperf/proto
cp -r libs/utils testcontrol/interactive/controller/vsperf/utils

#copy libs/utils into deployment and testcontrol auto container at appropriate location.
cp -r libs/utils deployment/auto/controller/vsperf/utils
cp -r libs/utils testcontrol/auto/controller/vsperf/utils

#copy libs/proto into client
cp -r libs/proto client/proto
