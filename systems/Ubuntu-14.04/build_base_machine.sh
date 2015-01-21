#!/bin/bash
#
# Top level scripts to build basic setup for the host 
#
# Copyright (C) 2015 OPNFV 
#
# Copying and distribution of this file, with or without modification,
# are permitted in any medium without royalty provided the copyright
# notice and this notice are preserved.  This file is offered as-is,
# without warranty of any kind.
#
# Contributors:
# 	Aihua Li, Huawei Technologies. 
#   ...

# Enable sshd
/etc/init.d/sshd start

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



