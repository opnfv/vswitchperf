#!/bin/bash
#
# Top level scripts to build basic setup for the host
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
#   Abdul Halim, Intel Corporation.
#   Martin Klozik, Intel Corporation.

ROOT_UID=0
SUDO=""

export VSPERFENV_DIR="$HOME/vsperfenv"

# function to emit error message before quitting
function die() {
    echo $1
    exit 1
}

# Detect OS name and version from systemd based os-release file
. /etc/os-release

# Get OS name (the First word from $NAME in /etc/os-release)
OS_NAME=`echo "$ID"`

# check if root
if [ "$UID" -ne "$ROOT_UID" ]
then
    # installation must be run via sudo
    SUDO="sudo -E"
fi

# If there is version specific dir available then set distro_dir to that
if [ -d "$OS_NAME/$VERSION_ID" ]; then
    distro_dir="$OS_NAME/$VERSION_ID"
else
    # Fallback - Default distro_dir = OS name
    distro_dir="$OS_NAME"
fi

# build base system using OS specific scripts
if [ -d "$distro_dir" ] && [ -e "$distro_dir/build_base_machine.sh" ]; then
    $SUDO $distro_dir/build_base_machine.sh || die "$distro_dir/build_base_machine.sh failed"
else
    die "$distro_dir is not yet supported"
fi

if [ -d "$distro_dir" ] && [ -e "$distro_dir/prepare_python_env.sh" ] ; then
    $distro_dir/prepare_python_env.sh || die "prepare_python_env.sh failed"
else
    die "$distro_dir is not yet supported"
fi

if [ ! -d /lib/modules/`uname -r`/build ] ; then
    die "Kernel devel is not available for active kernel. It can be caused by recent kernel update. Please reboot and run $0 again."
fi

# download and compile DPDK, OVS and QEMU
if [ -f ../src/Makefile ] ; then
    cd ../src
    make || die "Make failed"
    cd -
else
    die "Make failed; No Makefile"
fi
