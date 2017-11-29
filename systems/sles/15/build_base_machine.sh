#!/bin/bash
#
# Build a base machine for SLES15 systems
#
# Copyright (c) 2017 SUSE LLC.
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
#   Jose Lausuch, SUSE LINUX GmbH

zypper -q -n update
zypper -q -n in -y $(echo "
# compiler, tools and dependencies
make
automake
gcc
gcc-c++
glibc
glibc-devel
fuse
fuse-devel
glib2-devel
zlib-devel
ncurses-devel
kernel-default
kernel-default-devel
pkg-config
findutils-locate
curl
automake
autoconf
vim
wget
git
pciutils
cifs-utils
socat
sysstat
java-1_8_0-openjdk
git-review
mlocate

# python
python3
python-pip
python3-pip
python3-setuptools
python3-devel
python3-tk
python3-virtualenv

# libraries
libnuma1
libnuma-devel
libpixman-1-0
libpixman-1-0-devel
libtool
libpcap-devel
libnet9
libncurses5
libcurl4
libcurl-devel
libxml2
libfuse2
libopenssl1_0_0
libopenssl-devel
libpython3_4m1_0

" | grep -v ^#)

updatedb

# fix for the Ixia TclClient
ln -sf $(locate libc.so.6) /lib/libc.so.6

# virtual environment for python
pip3 install virtualenv

# hugepages setup
mkdir -p /dev/hugepages

# fix for non-utf8 characters in file
cp /etc/services /etc/services.bak
iconv -o /etc/services -f utf-8 -t utf-8 -c /etc/services.bak
