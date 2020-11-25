# Copyright 2018-19 Spirent Communications.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
VSPERF-controller
"""

# Fetching Environment Variable for controller, You can configure or
# modifies list.env file for setting your environment variable.

#pylint: disable=global-statement,no-else-continue
#pylint: disable=too-many-branches

import os
import time
import math
import ast
import ssh
import sys

TIMER = float()


DUT_IP = os.getenv('DUT_IP_ADDRESS')
DUT_USER = os.getenv('DUT_USERNAME')
DUT_PWD = os.getenv('DUT_PASSWORD')

VSPERF_TEST = os.getenv('VSPERF_TESTS')
VSPERF_CONF = os.getenv('VSPERF_CONFFILE')
VSPERF_TRAFFICGEN_MODE = str(os.getenv('VSPERF_TRAFFICGEN_MODE'))

DUT_CLIENT = None
TGEN_CLIENT = None

def host_connect():
    """
    Handle host connectivity to DUT
    """
    global DUT_CLIENT
    DUT_CLIENT = ssh.SSH(host=DUT_IP, user=DUT_USER, password=DUT_PWD)
    print("DUT Successfully Connected ..............................................[OK] \n ")

def upload_test_config_file():
    """
    #Upload Test Config File on DUT
    """
    #localpath = '/usr/src/app/vsperf/vsperf.conf'
    localpath = 'vsperf.conf'
    if not os.path.exists(localpath):
        print("VSPERF Test config File does not exists.......................[Failed]")
        return
    remotepath = '~/vsperf.conf'
    check_test_config_cmd = "find ~/ -maxdepth 1 -name '{}'".format(
        remotepath[2:])
    check_test_result = str(DUT_CLIENT.execute(check_test_config_cmd)[1])
    if remotepath[2:] in check_test_result:
        DUT_CLIENT.run("rm -f {}".format(remotepath[2:]))
    DUT_CLIENT.put_file(localpath, remotepath)
    check_test_config_cmd_1= "find ~/ -maxdepth 1 -name '{}'".format(
        remotepath[2:])
    check_test_result_1= str(DUT_CLIENT.execute(check_test_config_cmd)[1])
    if remotepath[2:] in check_test_result_1:
        print(
        "Test Configuration File Uploaded on DUT-Host.............................[OK] \n ")
    else:
	print("VSPERF Test config file upload failed.....................................[Critical]")

def run_vsperf_test():
    """
    Here we will perform the actual vsperf test
    """
    global TIMER
    rmv_cmd = "cd /mnt/huge && echo {} | sudo -S rm -rf *".format(DUT_PWD)
    DUT_CLIENT.run(rmv_cmd, pty=True)
    cmd = "source ~/vsperfenv/bin/activate ; "
    #cmd = "scl enable python33 bash ; "
    cmd += "cd vswitchperf && "
    cmd += "./vsperf "
    if VSPERF_CONF:
        cmd += "--conf-file ~/vsperf.conf "
    if "yes" in VSPERF_TRAFFICGEN_MODE.lower():
        cmd += "--mode trafficgen"
    vsperf_test_list = VSPERF_TEST.split(",")
    print(vsperf_test_list)
    for test in vsperf_test_list:
        atest = cmd
        atest += test
        DUT_CLIENT.run(atest, pty=True)
    print(
        "Test Successfully Completed................................................[OK]\n ")


if DUT_IP:
    host_connect()
if not DUT_CLIENT:
    print('Failed to connect to DUT ...............[Critical]')
    sys.exit()
else:
    upload_test_config_file()
    run_vsperf_test()
