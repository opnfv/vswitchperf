#!/usr/bin/env python

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
import sys
from stat import S_ISDIR
import time
import paramiko
from xtesting.core import testcase
import ssh

TIMER = float()



DUT_IP = os.getenv('DUT_IP_ADDRESS')
DUT_USER = os.getenv('DUT_USERNAME')
DUT_PWD = os.getenv('DUT_PASSWORD')
RES_PATH= os.getenv('RES_PATH')

VSPERF_TEST = os.getenv('VSPERF_TESTS')
VSPERF_CONF = os.getenv('VSPERF_CONFFILE')
VSPERF_TRAFFICGEN_MODE = str(os.getenv('VSPERF_TRAFFICGEN_MODE'))

DUT_CLIENT = None
TGEN_CLIENT = None

RECV_BYTES = 4096

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
    if VSPERF_CONF:
        localpath = VSPERF_CONF
    else:
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
    print(check_test_config_cmd_1)
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

def get_result():
    """
    Get Latest results from DUT
    """
    stdout_data = []
    stderr_data = []
    client = paramiko.Transport((DUT_IP, 22))
    client.connect(username=DUT_USER, password=DUT_PWD)
    session = client.open_channel(kind='session')
    directory_to_download = ''
    session.exec_command('ls /tmp | grep results')
    if not directory_to_download:
        while True:
            if session.recv_ready():
                stdout_data.append(session.recv(RECV_BYTES))
            if session.recv_stderr_ready():
                stderr_data.append(session.recv_stderr(RECV_BYTES))
            if session.exit_status_ready():
                break
        if stdout_data:
            line = stdout_data[0]
            filenames = line.decode("utf-8").rstrip("\n").split("\n")
            filenames = sorted(filenames)
            latest = filenames[-1]
            directory_to_download = os.path.join('/tmp', latest)
    stdout_data = []
    stderr_data = []
    if directory_to_download:
        destination = os.path.join(RES_PATH,
                               os.path.basename(os.path.normpath(
                                   directory_to_download)))
        os.makedirs(destination)
        print(directory_to_download)
        # Begin the actual downlaod
        sftp = paramiko.SFTPClient.from_transport(client)
        def sftp_walk(remotepath):
            path=remotepath
            files=[]
            folders=[]
            for fle in sftp.listdir_attr(remotepath):
                if S_ISDIR(fle.st_mode):
                    folders.append(fle.filename)
                else:
                    files.append(fle.filename)
            if files:
                yield path, files
        # Filewise download happens here
        for path,files  in sftp_walk(directory_to_download):
            for fil in files:
                remote = os.path.join(path,fil)
                local = os.path.join(destination, fil)
                print(local)
                sftp.get(remote, local)
    # Ready to work with downloaded data, close the session and client.
    session.close()
    client.close()

class VsperfBm(testcase.TestCase):
    """
    VSPERF-Xtesting Baremetal Control Class
    """
    def run(self, **kwargs):
        global RES_PATH
        try:
            self.start_time = time.time()
            self.result=100
            os.makedirs(self.res_dir, exist_ok=True)
            RES_PATH = self.res_dir
            if DUT_IP:
                host_connect()
            if not DUT_CLIENT:
                print('Failed to connect to DUT ...............[Critical]')
                self.result = 0
            else:
                upload_test_config_file()
                run_vsperf_test()
                get_result()
            self.stop_time = time.time()
        except Exception:  # pylint: disable=broad-except
            print("Unexpected error:", sys.exc_info()[0])
            self.result = 0
            self.stop_time = time.time()
