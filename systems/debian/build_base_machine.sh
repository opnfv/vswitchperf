#!/bin/bash
#
# Build a base machine for Debian style distro
#
# Copyright 2020 OPNFV
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
#   Sridhar K. N. Rao Spirent Communications

# This is meant to be used only for Containerized VSPERF.

# Synchronize package index files
apt-get -y update
apt-get -y install curl
apt-get -y install git
apt-get -y install wget
apt-get -y install python3-venv

# Make and Compilers
apt-get -y install make
apt-get -y install automake
apt-get -y install gcc
apt-get -y install g++
apt-get -y install libssl1.1
apt-get -y install libxml2
apt-get -y install zlib1g-dev
apt-get -y install scapy
