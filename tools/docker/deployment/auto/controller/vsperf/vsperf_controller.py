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
VSPERF_deploy_auto
"""

# Fetching Environment Variable for controller, You can configure or
# modifies list.env file for setting your environment variable.
# pylint: disable=W0603

import os

from utils import ssh

_ONE_DAY_IN_SECONDS = 60 * 60 * 24

DUT_IP = os.getenv('DUT_IP_ADDRESS')
DUT_USER = os.getenv('DUT_USERNAME')
DUT_PWD = os.getenv('DUT_PASSWORD')

TGEN_IP = os.getenv('TGEN_IP_ADDRESS')
TGEN_USER = os.getenv('TGEN_USERNAME')
TGEN_PWD = os.getenv('TGEN_PASSWORD')
TGEN_PARAM = os.getenv('TGEN_PARAMS')

HPMAX = int(os.getenv('HUGEPAGE_MAX'))
HPREQUESTED = int(os.getenv('HUGEPAGE_REQUESTED'))

SANITY = str(os.getenv('SANITY_CHECK'))

DUT_CLIENT = None
TGEN_CLIENT = None


def host_connect():
    """
    Handle host connectivity to DUT
    """
    global DUT_CLIENT
    DUT_CLIENT = ssh.SSH(host=DUT_IP, user=DUT_USER, password=DUT_PWD)
    print("DUT-Host Successfully Connected .........................................[OK] \n ")

def tgen_connect():
    """
    Handle Tgen Connection to Trex
    """
    global TGEN_CLIENT
    TGEN_CLIENT = ssh.SSH(host=TGEN_IP, user=TGEN_USER, password=TGEN_PWD)
    print("Traffic Generator Successfully Connected ...............................[OK] \n ")


def vsperf_install():
    """
    Perform actual installation
    """
    vsperf_check_command = "source ~/vsperfenv/bin/activate ; "
    vsperf_check_command += "cd vswitchperf* && ./vsperf --help"
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
                print(
                    "VSPERF is Already Installed on DUT-Host..........................."\
                    ".......[OK]\n")
            else:
                download_cmd = "git clone https://gerrit.opnfv.org/gerrit/vswitchperf"
                DUT_CLIENT.run(download_cmd)
                install_cmd = "cd vswitchperf/systems ; "
                install_cmd += "echo '{}' | sudo -S ./build_base_machine.sh ".\
                                format(DUT_PWD)
                #install_cmd += "./build_base_machine.sh"
                DUT_CLIENT.run(install_cmd)
                print(
                    "Vsperf Installed on DUT-Host ....................................[OK]\n")


def tgen_install():
    """
    #Install T-rex traffic gen on TGen
    """
    kill_cmd = "pkill -f ./t-rex"
    TGEN_CLIENT.send_command(kill_cmd)
    tgen_start_check = "cd trex_2.37/scripts && ./t-rex-64 -f cap2/dns.yaml -d 100 -m 1 --nc"
    tgen_start_cmd_result = int(TGEN_CLIENT.execute(tgen_start_check)[0])
    if tgen_start_cmd_result == 0:
        print(
            "Traffic Generator has T-rex Installed....................................[OK]\n")
    else:
        download_cmd = "git clone https://github.com/cisco-system-traffic-generator/trex-core"
        TGEN_CLIENT.run(download_cmd)
        install_cmd = "cd trex-core/linux_dpdk ; ./b configure ; ./b build"
        TGEN_CLIENT.run(install_cmd)
        # before you setup your trex_cfg.yml make sure to do sanity check NIC
        # PICs and extablished route between your DUT and Test Device.
        print(
            "Traffic Generetor Host has now T-rex Installed...........................[OK]\n")

def upload_tgen_config_file():
    """
    #Upload Tgen Config File on T-rex
    """
    #localpath = '/home/shaileshchauhan/Desktop/Container_2/controller/vsperf/trex_cfg.yml'
    #remotepath = '~/trex_cfg1.yaml'
    localpath = '/usr/src/app/vsperf/trex_cfg.yaml'
    remotepath = '~/trex_cfg.yaml'
    check_trex_config_cmd = "echo {} | sudo -S find /etc -maxdepth 1 -name '{}'".format(
        TGEN_PWD, remotepath[2:])
    check_test_result = str(TGEN_CLIENT.execute(check_trex_config_cmd)[1])
    if remotepath[2:] in check_test_result:
        DUT_CLIENT.run("rm -f /etc/{}".format(remotepath[2:]))
    TGEN_CLIENT.put_file(localpath, remotepath)
    TGEN_CLIENT.run(
        "echo {} | sudo -S mv ~/{} /etc/".format(TGEN_PWD, remotepath[2:]), pty=True)
    print(
        "T-rex Configuration File Uploaded on TGen-Host...........................[OK]\n")


def install_collectd():
    """
    installation of the collectd
    """
    check_collectd_config_cmd = "find /opt -maxdepth 1 -name 'collectd'"
    check_test_result = str(DUT_CLIENT.execute(check_collectd_config_cmd)[1])
    if "collectd" in check_test_result:
        print(
            'Collectd Installed Successfully on DUT-Host..............................[OK]\n')
    else:
        #DUT_CLIENT.run("echo {} | sudo -S rm -r -f /opt/collectd".format(DUT_PWD))
        #DUT_CLIENT.run("echo {} | sudo -S rm -r -f ~/collectd".format(DUT_PWD))
        download_cmd = "git clone https://github.com/collectd/collectd.git"
        DUT_CLIENT.run(download_cmd)
        build_cmd = "cd collectd ; "
        build_cmd += "./build.sh"
        DUT_CLIENT.run(build_cmd)
        config_cmd = "cd collectd ; ./configure --enable-syslog --enable-logfile "
        config_cmd += "--enable-hugepages --enable-debug ; "
        DUT_CLIENT.run(config_cmd)
        install_cmd = "cd collectd ; make ; "
        install_cmd += "echo '{}' | sudo -S make install".format(DUT_PWD)
        DUT_CLIENT.run(install_cmd, pty=True)
        print(
            'Collectd Installed Successfully on DUT-Host.............................[OK]\n ')


def collectd_upload_config():
    """
    Upload Configuration file of Collectd on DUT
    """
    #localpath = '/home/shaileshchauhan/Desktop/Container_2/controller/vsperf/collectd.conf'
    #remotepath = '~/collectd1.conf'
    localpath = '/usr/src/app/vsperf/collectd.conf'
    remotepath = '~/collectd.conf'
    collectd_config_cmd = "echo {} | sudo -S find /opt/collectd/etc -maxdepth 1 -name '{}'".\
                           format(DUT_PWD, remotepath[2:])
    check_test_result = str(DUT_CLIENT.execute(collectd_config_cmd)[1])
    if remotepath[2:] in check_test_result:
        DUT_CLIENT.run(
            "echo {} | sudo -S rm -f /opt/collectd/etc/{}".format(DUT_PWD, remotepath[2:]))
    DUT_CLIENT.put_file(localpath, remotepath)
    DUT_CLIENT.run("echo {} | sudo -S mv ~/{} /opt/collectd/etc/".\
                  format(DUT_PWD, remotepath[2:]), pty=True)
    print(
        "Collectd Configuration File Uploaded on DUT-Host.........................[OK]\n ")

def start_tgen():
    """
    It will start the Traffic generetor
    """
    #Might be possible that t-rex already running
    kill_cmd = "pkill -f ./t-rex"
    TGEN_CLIENT.send_command(kill_cmd)
    run_cmd = "cd trex_2.37/scripts && "
    run_cmd += "screen ./t-rex-64 "
    run_cmd += TGEN_PARAM
    TGEN_CLIENT.send_command(run_cmd)
    print(
        "T-Rex Successfully running...............................................[OK]\n")


def dut_hugepage_config():
    """
    Configure the DUT system hugepage parameter from client
    """
    hugepage_cmd = "echo '{}' | sudo -S mkdir -p /mnt/huge ; ".format(
        DUT_PWD)
    hugepage_cmd += "echo '{}' | sudo -S mount -t hugetlbfs nodev /mnt/huge".format(
        DUT_PWD)
    DUT_CLIENT.run(hugepage_cmd, pty=True)
    hp_nr_cmd = "cat /sys/devices/system/node/node0/hugepages/hugepages-2048kB/nr_hugepages"
    hp_free_cmd = "cat /sys/devices/system/node/node0/hugepages/hugepages-2048kB/free_hugepages"
    hp_nr = int(DUT_CLIENT.execute(hp_nr_cmd)[1])
    hp_free = int(DUT_CLIENT.execute(hp_free_cmd)[1])
    if hp_free <= HPREQUESTED:
        hp_nr_new = hp_nr + (HPREQUESTED - hp_free)
        if hp_nr_new > HPMAX:
            hp_nr_new = HPMAX

    nr_hugepage_cmd = "echo '{}' | sudo -S bash -c \"echo 'vm.nr_hugepages={}' >> ".\
                       format(DUT_PWD, hp_nr_new)
    nr_hugepage_cmd += "/etc/sysctl.conf\""
    DUT_CLIENT.run(nr_hugepage_cmd, pty=True)

    dict_cmd = "cat /sys/devices/system/node/node1/hugepages/hugepages-2048kB/nr_hugepages"
    dict_check = int(DUT_CLIENT.execute(dict_cmd)[0])
    if dict_check == 0:
        node1_hugepage_cmd = "echo '{}' | sudo -s bash -c \"echo 0 > ".format(DUT_PWD)
        node1_hugepage_cmd += "/sys/devices/system/node/node1/hugepages"
        node1_hugepage_cmd += "/hugepages-2048kB/nr_hugepages\""
        DUT_CLIENT.run(node1_hugepage_cmd, pty=True)
    print("DUT-Host system configured with {} No of Hugepages.....................[OK] \n ".\
          format(hp_nr_new))


def check_dependecies():
    """
    Check and Install required packages on DUT
    """
    packages = ['python34-tkinter', 'sysstat', 'bc']
    for pkg in packages:
        # pkg_check_cmd = "dpkg -s {}".format(pkg) for ubuntu
        pkg_check_cmd = "rpm -q {}".format(pkg)
        pkg_cmd_response = DUT_CLIENT.execute(pkg_check_cmd)[0]
        if pkg_cmd_response == 1:
            install_pkg_cmd = "echo '{}' | sudo -S apt-get install -y {}".format(
                DUT_PWD, pkg)
            DUT_CLIENT.run(install_pkg_cmd, pty=True)
    print(
        "Python3-tk, sysstat and bc Packages are now Installed....................[OK] \n ")


def sanity_nic_check():
    """
    Check either NIC PCI ids are Correctly placed or not
    """
    trex_conf_path = "cat /etc/trex_cfg.yaml | grep interfaces"
    trex_conf_read = TGEN_CLIENT.execute(trex_conf_path)[1]
    nic_pid_ids_list = [trex_conf_read.split("\"")[1], trex_conf_read.split("\"")[3]]
    trex_nic_pic_id_cmd = "lspci | egrep -i --color 'network|ethernet'"
    trex_nic_pic_id = str(TGEN_CLIENT.execute(trex_nic_pic_id_cmd)[1]).split('\n')
    acheck = 0
    for k in trex_nic_pic_id:
        for j in nic_pid_ids_list:
            if j in k:
                acheck += 1
            else:
                pass
    if acheck == 2:
        print("Both the NIC PCI Ids are Correctly"\
            " configured on TGen-Host...............[OK]\n")
    else:
        print("You configured NIC PCI Ids Wrong in "\
            "TGen-Host............................[OK]\n")


def sanity_collectd_check():
    """
    Check and verify collectd is able to run and start properly
    """
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
            print(
                "Collectd is working Fine ................................................[OK] \n ")
        else:
            print(
                "Collectd Fail to Start, Install correctly before running Test....[Failed]\n ")
    else:
        print(
            "Collectd is not installed yet........................................[Failed]\n")

def sanity_vsperf_check():
    """
    We have to make sure that VSPERF install correctly
    """
    vsperf_check_cmd = "source ~/vsperfenv/bin/activate ; cd vswitchperf* && ./vsperf --help"
    vsperf_check_cmd_result = str(DUT_CLIENT.execute(vsperf_check_cmd)[1])
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
                print(
                    "VSPERF Installed Correctly and Working fine.........................."\
                    "....[OK]\n")
            else:
                print(
                    "VSPERF Does Not Installed Correctly , INSTALL IT AGAIN........[Critical]\n")
        else:
            print(
                "VSPERF Does Not Installed Correctly , INSTALL IT AGAIN............[Critical]\n")
            break


def sanity_tgen_conn_dut_check():
    """
    We should confirm the DUT connectivity with the Tgen and Traffic Generator is working or not
    """
    tgen_connectivity_check_cmd = "ping {} -c 1".format(TGEN_IP)
    tgen_connectivity_check_result = int(
        DUT_CLIENT.execute(tgen_connectivity_check_cmd)[0])
    if tgen_connectivity_check_result == 0:
        print(
            "DUT-Host is successfully reachable to Traffic Generator Host.............[OK]\n")
    else:
        print(
            "DUT-host is unsuccessful to reach the Traffic Generator Host..............[Failed]")
        print(
            "Make sure to establish connection before running Test...............[Critical]\n")


def sanity_tgen_check():
    """
    It will check Trex properly running or not
    """
    tgen_start_cmd_check = "cd trex_2.37/scripts &&"
    tgen_start_cmd_check += " ./t-rex-64 -f cap2/dns.yaml -d 100 -m 1 --nc"
    tgen_start_cmd_result = int(TGEN_CLIENT.execute(tgen_start_cmd_check)[0])
    if tgen_start_cmd_result == 0:
        print(
            "TGen-Host successfully running........................................[OK]\n")
    else:
        print("TGen-Host is unable to start t-rex ..................[Failed]")
        print("Make sure you install t-rex correctly ...............[Critical]\n")


def dut_vsperf_test_availability():
    """
    Before running test we have to make sure there is no other test running
    """
    vsperf_ava_cmd = "ps -ef | grep -v grep | grep ./vsperf | awk '{print $2}'"
    vsperf_ava_result = len(
        (DUT_CLIENT.execute(vsperf_ava_cmd)[1]).split("\n"))
    if vsperf_ava_result == 1:
        print("DUT-Host is available for performing VSPERF Test\n\
            You can perform Test!")
    else:
        print("DUT-Host is busy right now, Wait for some time\n\
            Always Check availability before Running Test!\n")


host_connect()
tgen_connect()
vsperf_install()
tgen_install()
upload_tgen_config_file()
install_collectd()
collectd_upload_config()
dut_hugepage_config()
check_dependecies()
sanity_nic_check()
start_tgen()
dut_vsperf_test_availability()

print("\n\nIF you are getting any Failed or Critical message!!!\n" \
      "Please follow this steps:\n"
      "1. Make necessory changes before running VSPERF TEST\n"\
      "2. Re-Run the auto deployment container")

if 'yes' in SANITY.lower():
    sanity_collectd_check()
    sanity_vsperf_check()
    sanity_tgen_conn_dut_check()
