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
yum -y update

# this sould be installed if running from parent
yum -y install redhat-lsb

# Make and Compilers
yum -y install make
yum -y install automake
yum -y install gcc
yum -y install libxml2

# tools
yum -y install curl
yum -y install autoconf libtool

yum -y install libpcap-devel
yum -y install libnet

# install gvim
yum -y install vim-X11

