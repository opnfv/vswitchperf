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

#pylint: disable=global-statement
#pylint: disable=too-many-branches

import os
import time
import math
import ast
from utils import ssh

_ONE_DAY_IN_SECONDS = 60 * 60 * 24
TIMER = float()


DUT_IP = os.getenv('DUT_IP_ADDRESS')
DUT_USER = os.getenv('DUT_USERNAME')
DUT_PWD = os.getenv('DUT_PASSWORD')

TGEN_IP = os.getenv('TGEN_IP_ADDRESS')

VSPERF_TEST = os.getenv('VSPERF_TESTS')
VSPERF_CONF = os.getenv('VSPERF_CONFFILE')
VSPERF_TRAFFICGEN_MODE = str(os.getenv('VSPERF_TRAFFICGEN_MODE'))

CLEAN_UP = os.getenv('CLEAN_UP')

DUT_CLIENT = None
TGEN_CLIENT = None
SANITY_CHECK_DONE_LIST = list()


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
    localpath = '/usr/src/app/vsperf/vsperf.conf'
    remotepath = '~/vsperf.conf'
    check_test_config_cmd = "find ~/ -maxdepth 1 -name '{}'".format(
        remotepath[2:])
    check_test_result = str(DUT_CLIENT.execute(check_test_config_cmd)[1])
    if remotepath[2:] in check_test_result:
        DUT_CLIENT.run("rm -f {}".format(remotepath[2:]))
    DUT_CLIENT.put_file(localpath, remotepath)
    print(
        "Test Configuration File Uploaded on DUT-Host.............................[OK] \n ")


def start_beats():
    """
    Start fileBeats on DUT
    """
    run_cmd = "echo '{}' | sudo -S service filebeat start".format(DUT_PWD)
    #run_cmd = "sudo service filebeat start"
    DUT_CLIENT.run(run_cmd, pty=True)
    print(
        "Beats are started on DUT-Host............................................[OK] \n")

def run_vsperf_test():
    """
    Here we will perform the actual vsperf test
    """
    global TIMER
    # Sometimes hugepage store in /mnt/huge in order to free up the hugepage
    # removing this stored hugepage is necessory
    rmv_cmd = "cd /mnt/huge && echo {} | sudo -S rm -rf *".format(DUT_PWD)
    DUT_CLIENT.run(rmv_cmd, pty=True)
    cmd = "source ~/vsperfenv/bin/activate ; "
    #cmd = "scl enable python33 bash ; "
    cmd += "cd vswitchperf* && "
    cmd += "./vsperf "
    if VSPERF_CONF:
        cmd += "--conf-file ~/vsperf.conf "
        # cmd += self.conffile
    if "yes" in VSPERF_TRAFFICGEN_MODE.lower():
        cmd += "--mode trafficgen"
    vsperf_test_list = VSPERF_TEST.split(",")
    print(vsperf_test_list)
    for test in vsperf_test_list:
        atest = cmd
        atest += test
        DUT_CLIENT.run(atest, pty=True)
    print(
        "Test Successfully running................................................[OK]\n ")


def test_status():
    """
    Chechk for the test status after performing test
    """
    testtype_list = VSPERF_TEST.split(",")
    num_test = len(testtype_list)
    test_success = []
    test_failed = []
    testtype_list_len = len(testtype_list)
    for test in testtype_list:
        passed_minutes = 5
        latest_result_cmd = "find /tmp -mindepth 1 -type d -cmin -{} -printf '%f'".format(
            passed_minutes)
        test_result_dir = str(
            (DUT_CLIENT.execute(latest_result_cmd)[1]).split('find')[0])
        test_date_cmd = "date +%F"
        test_date = str(DUT_CLIENT.execute(test_date_cmd)[1]).replace("\n", "")
        if test_date in test_result_dir:
            testcase_check_cmd = "cd /tmp && cd `ls -t | grep results | head"
            testcase_check_cmd += " -{} | tail -1` && find . -maxdepth 1 -name '*{}*'".\
                                  format(testtype_list_len, test)
            testcase_check_output = str(
                DUT_CLIENT.execute(testcase_check_cmd)[1]).split('\n', 2)
            check = 0
            for i in testcase_check_output:
                if (".csv" in i) or (".md" in i) or (".rst" in i):
                    check += 1
            if check == 3:
                test_success.append(test)
            else:
                test_failed.append(test)
            testtype_list_len -= 1
    if num_test == len(test_success):
        print("All Test Successfully Completed on DUT-Host   Results... [OK]")
    elif not test_success:
        print("All Test Failed on DUT-Host \nResults... [Failed]")
    else:
        print(
            "Only {} Test failed    Results ... [Failed]\n"\
            "All other Test Successfully Completed on DUT-Host     Results... [OK] ".\
            format(test_failed))


def vsperf_remove():
    """
    Actual removal of the VSPERF
    """
    vsperf_rm_cmd = "echo '{}' | sudo -S rm -r ~/vswitchperf".format(DUT_PWD)
    DUT_CLIENT.run(vsperf_rm_cmd)
    vsperfenv_rm_cmd = "echo '{}' | sudo -S rm -r -f ~/vsperfenv".\
                        format(DUT_PWD)
    DUT_CLIENT.run(vsperfenv_rm_cmd)


def remove_uploaded_config():
    """
    Remove all the uploaded configuration files
    """
    vconfig_rm_cmd = "rm ~/vsperf.conf"
    DUT_CLIENT.run(vconfig_rm_cmd)
    cdconfig_rm_cmd = "echo '{}' | sudo -S rm /opt/collectd/etc/collectd.conf".\
                       format(DUT_PWD)
    DUT_CLIENT.run(cdconfig_rm_cmd)


def result_folders_remove():
    """
    Remove result folder on DUT
    """
    remove_cmd = "rm -r /tmp/*results*"
    DUT_CLIENT.run(remove_cmd)


def collectd_remove():
    """
    Remove collectd from DUT
    """
    collectd_dwn_rm_cmd = "echo '{}' | sudo -S rm -r -f ~/collectd".format(
        DUT_PWD)
    DUT_CLIENT.run(collectd_dwn_rm_cmd)
    collectd_rm_cmd = "echo '{}' | sudo -S rm -r -f /opt/collectd".format(
        DUT_PWD)
    DUT_CLIENT.run(collectd_rm_cmd)


def terminate_vaperf():
    """
    Terminate the VSPERF and kill processes
    """
    stress_kill_cmd = "echo '{}' | sudo -S pkill stress &> /dev/null".format(
        DUT_PWD)
    python3_kill_cmd = "echo '{}' | sudo -S pkill python3 &> /dev/null".format(
        DUT_PWD)
    qemu_kill_cmd = "echo '{}' | sudo -S killall -9 qemu-system-x86_64 &> /dev/null".format(
        DUT_PWD)
    DUT_CLIENT.run(stress_kill_cmd)
    DUT_CLIENT.run(python3_kill_cmd)
    DUT_CLIENT.run(qemu_kill_cmd)

    # sometimes qemu resists to terminate, so wait a bit and kill it again
    qemu_check_cmd = "pgrep qemu-system-x86_64"
    qemu_cmd_response = DUT_CLIENT.execute(qemu_check_cmd)[1]

    if qemu_cmd_response != '':
        time.sleep(5)
        DUT_CLIENT.run(qemu_kill_cmd)
        time.sleep(5)

    ovs_kill_cmd = "echo '{}' | sudo pkill ovs-vswitchd &> /dev/null".format(
        DUT_PWD)
    ovsdb_kill_cmd = "echo '{}' | sudo pkill ovsdb-server &> /dev/null".format(
        DUT_PWD)
    vppctl_kill_cmd = "echo '{}' | sudo pkill vppctl &> /dev/null".format(
        DUT_PWD)
    vpp_kill_cmd = "echo '{}' | sudo pkill vpp &> /dev/null".format(DUT_PWD)
    vpp_cmd = "echo '{}' | sudo pkill -9 vpp &> /dev/null".format(DUT_PWD)

    DUT_CLIENT.run(ovs_kill_cmd)
    time.sleep(1)
    DUT_CLIENT.run(ovsdb_kill_cmd)
    time.sleep(1)
    DUT_CLIENT.run(vppctl_kill_cmd)
    time.sleep(1)
    DUT_CLIENT.run(vpp_kill_cmd)
    time.sleep(1)
    DUT_CLIENT.run(vpp_cmd)
    time.sleep(1)

    print(
        "All the VSPERF related process terminated successfully..............[OK]")


def sanit_collectd_check():
    """
    Check and verify collectd is able to run and start properly
    """
    global SANITY_CHECK_DONE_LIST
    check_collectd_cmd = "find /opt -maxdepth 1 -name 'collectd'"
    check_test_result = str(DUT_CLIENT.execute(check_collectd_cmd)[1])
    if "collectd" in check_test_result:
        check_collectd_run_cmd = "echo {} | sudo -S service collectd start".format(
            DUT_PWD)
        DUT_CLIENT.run(check_collectd_run_cmd, pty=True)
        check_collectd_status_cmd = "ps aux | grep collectd"
        check_collectd_status = str(
            DUT_CLIENT.execute(check_collectd_status_cmd)[1])
        if "/sbin/collectd" in check_collectd_status:
            SANITY_CHECK_DONE_LIST.append(int(1))
            print(
                "Collectd is working Fine ................................................[OK] \n ")
        else:
            print(
                "Collectd Fail to Start, Install correctly before running Test....[Failed]\n ")
    else:
        print(
            "Collectd is not installed yet........................................[Failed]\n")


def sanity_vnf_path():
    """
    Check if VNF image available on the mention path in Test Config File
    """
    # fetch the VNF path we placed in vsperf.conf file
    global SANITY_CHECK_DONE_LIST
    vsperf_conf_path = open('/usr/src/app/vsperf/vsperf.conf')
    vsperf_conf_read = vsperf_conf_path.readlines()
    for i in vsperf_conf_read:
        if 'GUEST_IMAGE' in i:
            vnf_image_path = i.split("'")[1]
            vnf_path_check_cmd = "find {}".format(vnf_image_path)
            vnf_path_check_result = str(
                DUT_CLIENT.execute(vnf_path_check_cmd)[1])
            if vnf_image_path in vnf_path_check_result:
                SANITY_CHECK_DONE_LIST.append(int(2))
                print(
                    "Test Configratuion file has Correct VNF path information on DUT-Host.." \
                    "...[OK]\n ")
            else:
                print(
                    "Test Configuration file has wrongly placed VNF path information......" \
                    "....[FAILED]\n")

def sanity_vsperf_check():
    """
    We have to make sure that VSPERF install correctly
    """
    global SANITY_CHECK_DONE_LIST
    vsperf_check_command = "source ~/vsperfenv/bin/activate ; cd vswitchperf* && ./vsperf --help"
    vsperf_check_cmd_result = str(DUT_CLIENT.execute(vsperf_check_command)[1])
    vsperf_verify_list = [
        'usage',
        'positional arguments',
        'optional arguments',
        'test selection options',
        'test behavior options']
    for idx, i in enumerate(vsperf_verify_list, start=1):
        if str(i) in vsperf_check_cmd_result:
            if idx < 5:
                continue
            elif idx == 5:
                SANITY_CHECK_DONE_LIST.append(int(3))
                print("VSPERF Installed Correctly and Working fine......................." \
                    ".......[OK]\n")
            else:
                print(
                    "VSPERF Does Not Installed Correctly , INSTALL IT AGAIN.........[Critical]\n")
        else:
            print(
                "VSPERF Does Not Installed Correctly , INSTALL IT AGAIN..............[Critical]\n")
            break

def variable_from_test_config(aparameter):
    """This function can be use to read any configuration paramter from vsperf.conf"""
    read_cmd = 'cat ~/vsperf.conf | grep "{}"'.format(aparameter)
    read_cmd_output = str(DUT_CLIENT.execute(read_cmd)[1])
    print(read_cmd_output)
    if not read_cmd_output or '#' in read_cmd_output:
        return 0
    return read_cmd_output.split("=")[1].strip()

def cpumask2coreids(mask):
    """conver mask to coreids"""
    intmask = int(mask, 16)
    i = 1
    coreids = []
    while i < intmask:
        if i & intmask:
            coreids.append(str(math.frexp(i)[1]-1))
        i = i << 1
    return coreids

def cpu_allocation_check():
    """It will check the cpu allocation before run test"""
    global SANITY_CHECK_DONE_LIST
    read_setting_cmd = "source vsperfenv/bin/activate ; cd vswitchperf* && "
    read_setting_cmd += './vsperf --list-settings'
    default_vsperf_settings = ast.literal_eval(str(DUT_CLIENT.execute(read_setting_cmd)[1]))
    default_cpu_map = default_vsperf_settings["VSWITCH_VHOST_CPU_MAP"]
    default_vswitch_pmd_cpu_mask = str(default_vsperf_settings["VSWITCH_PMD_CPU_MASK"])
    default_vswitch_vhost_cpu_map = [str(x) for x in default_cpu_map]
    vswitch_pmd_cpu_mask = variable_from_test_config("VSWITCH_PMD_CPU_MASK")
    vswitch_cpu_map = (variable_from_test_config("VSWITCH_VHOST_CPU_MAP"))
    vswitch_vhost_cpu_map = 0
    if vswitch_cpu_map != 0:
        vswitch_vhost_cpu_map = [str(x) for x in  ast.literal_eval(vswitch_cpu_map)]

    if vswitch_pmd_cpu_mask == 0 and vswitch_vhost_cpu_map == 0:
        SANITY_CHECK_DONE_LIST.append(int(4))
        print("CPU allocation Check Done,"\
            "\nNo vswitch_pmd_cpu_mask or vswitch_vhost_cpu_map assign in test config file\n" \
            "Using Default Settings ..................................................[OK]\n")
    elif vswitch_pmd_cpu_mask != 0 and vswitch_vhost_cpu_map == 0:
        core_id = cpumask2coreids(vswitch_pmd_cpu_mask)
        print(core_id)
        if len(default_vswitch_vhost_cpu_map) >= len(core_id):
            if all(elem in default_vswitch_vhost_cpu_map  for elem in core_id):
                SANITY_CHECK_DONE_LIST.append(int(4))
                print("CPU allocation properly done on DUT-Host.................[OK]\n")
            else:
                print("CPU allocation not done properly on DUT-Host............[Failed]\n")
        else:
            print("CPU allocation not done properly on DUT-Host............[Failed]\n")
    elif vswitch_pmd_cpu_mask == 0 and vswitch_vhost_cpu_map != 0:
        core_id_1 = cpumask2coreids(default_vswitch_pmd_cpu_mask)
        print(core_id_1)
        if len(vswitch_vhost_cpu_map) >= len(core_id_1):
            if all(elem in vswitch_vhost_cpu_map  for elem in core_id_1):
                SANITY_CHECK_DONE_LIST.append(int(4))
                print("CPU allocation properly done on DUT-Host.................[OK]\n")
            else:
                print("CPU allocation not done properly on DUT-Host............[Failed]\n")
        else:
            print("CPU allocation not done properly on DUT-Host............[Failed]\n")
    else:
        core_id_2 = cpumask2coreids(vswitch_pmd_cpu_mask)
        print(core_id_2)
        if len(vswitch_vhost_cpu_map) >= len(core_id_2):
            if all(elem in vswitch_vhost_cpu_map  for elem in core_id_2):
                SANITY_CHECK_DONE_LIST.append(int(4))
                print("CPU allocation properly done on DUT-Host.................[OK]\n")
            else:
                print("CPU allocation not done properly on DUT-Host............[Failed]\n")
        else:
            print("CPU allocation not done properly on DUT-Host............[Failed]\n")



def sanity_dut_conn_tgen_check():
    """
    We should confirm the DUT connectivity with the Tgen and Traffic Generator is working or not
    """
    global SANITY_CHECK_DONE_LIST
    tgen_connectivity_check_cmd = "ping {} -c 1".format(TGEN_IP)
    tgen_connectivity_check_result = int(DUT_CLIENT.execute(tgen_connectivity_check_cmd)[0])
    if tgen_connectivity_check_result == 0:
        SANITY_CHECK_DONE_LIST.append(int(5))
        print(
            "DUT-Host is successfully reachable to Traffic Generator Host.............[OK]\n")
    else:
        print(
            "DUT-host is unsuccessful to reach the Traffic Generator Host.............[Failed]")
        print(
            "Make sure to establish connection before running Test...............[Critical]\n")


host_connect()
upload_test_config_file()
sanity_vnf_path()
cpu_allocation_check()
sanit_collectd_check()
sanity_vsperf_check()
sanity_dut_conn_tgen_check()
start_beats()

if len(SANITY_CHECK_DONE_LIST) != 5:
    print("Certain Sanity Checks Failed\n" \
          "You can make changes based on the outputs and run" \
          "the testcontrol auto container again")
else:
    run_vsperf_test()
    test_status()

if "yes" in CLEAN_UP.lower():
    vsperf_remove()
    remove_uploaded_config()
    result_folders_remove()
    collectd_remove()
    terminate_vaperf()
