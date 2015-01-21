#!/bin/bash
#
# Top level scripts to build basic setup for the host
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
#   ...

# function to emit error message before quitting
function die() {
    echo $1
    exit 1
}

# determine this machine's distro-version

distro=`lsb_release -i  | cut -f 2`
release=`lsb_release -r  | cut -f 2`
distro_dir=$distro-$release

if [ -d "$distro_dir" ] && [ -e $distro_dir/build_base_machine.sh ]; then
   $distro_dir/build_base_machine.sh
else
   die "$distro_dir is not yet supported"
fi
