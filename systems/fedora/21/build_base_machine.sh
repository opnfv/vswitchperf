#!/bin/bash
#
# Build a base machine for Fedora distro
#
# Copyright 2015 OPNFV, Intel Corporation.
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
#   Abdul Halim, Intel Corporation.

yum -y install $(echo "
# Make and Compilers
make
automake
gcc
gcc-c++
libxml2
glibc
glib2-devel
kernel-devel
fuse-libs
fuse
fuse-devel
kernel-modules-extra
pixman-devel
openssl-devel

# tools
curl
autoconf
libtool
libpcap-devel
libnet
vim
wget
git
pciutils
cifs-utils
socat

# install python packages
python3
python3-virtualenv
python3-setuptools
python3-pip
python3-dbus
python3-devel
python3-tkinter
systemd-python3
python3-libs
libreport-python3
abrt-python3
abrt-addon-python3

# install git-review tool
git-review
" | grep -v ^#) || exit 1

# Create hugepage dirs
mkdir -p /dev/hugepages
