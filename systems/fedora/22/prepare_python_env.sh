#!/bin/bash
#
# Prepare Python environment for vsperf execution on Fedora 22 systems.
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

if [ -d "$VSPERFENV_DIR" ] ; then
    echo "Directory $VSPERFENV_DIR already exists. Skipping python virtualenv creation."
    exit
fi

# enable virtual environment in a subshell, so QEMU build can use python 2.7

(virtualenv-3.4 "$VSPERFENV_DIR"
source "$VSPERFENV_DIR"/bin/activate
pip install -r ../requirements.txt
pip install pylint)