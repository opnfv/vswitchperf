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
sshpass

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
numactl
numactl-devel
libpng-devel
freetype-devel

# install gvim
vim-X11

# install epel release required for git-review
epel-release
" | grep -v ^#)

# install SCL for python34
sudo yum -y install centos-release-scl-rh

# install python34 packages and git-review tool
yum -y install $(echo "
rh-python36
rh-python36-python-tkinter
git-review
" | grep -v ^#)
# prevent ovs vanilla from building from source due to kernel incompatibilities
sed -i s/'SUBBUILDS = src_vanilla'/'#SUBBUILDS = src_vanilla'/ ../src/Makefile
