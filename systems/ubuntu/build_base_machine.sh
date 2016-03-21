#!/bin/bash
#
# Build a base machine for Ubuntu style distro
#
# Copyright 2015 OPNFV
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# Contributors:
#   Aihua Li, Huawei Technologies.

# Synchronize package index files
apt-get -y update

# Make and Compilers
apt-get -y install make
apt-get -y install automake
apt-get -y install gcc
apt-get -y install gcc++
apt-get -y install libssl1.0.0
apt-get -y install libxml2
apt-get -y install zlib1g-dev
apt-get -y install scapy

# Linux Kernel Source
apt-get -y install linux-source
apt-get -y install pkg-config

# Install package dependecies
apt-get -y install libncurses5-dev
apt-get -y install curl
apt-get -y install libcurl4-openssl-dev
apt-get -y install autoconf libtool
apt-get -y install libpcap-dev
apt-get -y install libglib2.0
apt-get -y install libfuse-dev

# Some useful tools you may optionally install
#apt-get -y install ctags
#apt-get -y install wireshark

# packages related to VM

# a few manual fix up on a ubuntu
cd /lib/x86_64-linux-gnu
ln -sf libssl.so.1.0.0 libssl.so
ln -sf libcrypto.so.1.0.0 libcrypto.so

cd /usr/lib/x86_64-linux-gnu
ln -sf libxml2.so.2 libxml2.so



