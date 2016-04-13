#!/bin/bash
#
# Build a base machine for CentOS distro
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
#   Martin Klozik, Intel Corporation.

# Synchronize package index files
yum -y update

# Install required packages
yum -y install $(echo "

# Make, Compilers and devel
make
gcc
gcc-c++
libxml2
glibc
kernel-devel

# tools
wget
git
scl-utils
vim
curl
autoconf
libtool
automake
pciutils
cifs-utils
sysstat

# libs
libpcap-devel
libnet
fuse
fuse-libs
fuse-devel
zlib
zlib-devel
glib2-devel
pixman-devel
socat

# install gvim
vim-X11

# install epel release required for git-review
epel-release
" | grep -v ^#)

# install SCL for python33
wget https://www.softwarecollections.org/en/scls/rhscl/python33/epel-7-x86_64/download/rhscl-python33-epel-7-x86_64.noarch.rpm
rpm -i rhscl-python33-epel-7-x86_64.noarch.rpm

# install python33 packages and git-review tool
yum -y install $(echo "
python33
python33-python-tkinter
git-review
" | grep -v ^#)
