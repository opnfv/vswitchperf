#!/bin/bash
#
# Prepare Python environment for vsperf execution on RHEL 7.3 systems.
#
# Copyright 2016-2017 OPNFV, Intel Corporation, Red Hat Inc.
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

scl enable rh-python34 "
virtualenv "$VSPERFENV_DIR" --python /opt/rh/rh-python34/root/usr/bin/python3
source "$VSPERFENV_DIR"/bin/activate
pip install -r ../requirements.txt
pip install pylint
"