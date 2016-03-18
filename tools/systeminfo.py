# Copyright 2015-2016 Intel Corporation.
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

"""Tools for access to OS details
"""

import os
import platform
import subprocess
import locale

from conf import settings as S

def match_line(file_name, pattern):
    """ loops through given file and returns first line matching given pattern

    :returns: string with the matching line without end of line or None
    """
    try:
        with open(file_name, encoding="latin-1") as file_:
            for line in file_:
                if not line.strip():
                    continue
                if not line.strip().startswith(pattern):
                    continue

                return line.strip().rstrip('\n')
        return None
    except OSError:
        return None

def get_os():
    """Get distro name.

    :returns: Return distro name as a string
    """
    return ' '.join(platform.dist())

def get_kernel():
    """Get kernel version.

    :returns: Return kernel version as a string
    """
    return platform.release()

def get_cpu():
    """Get CPU information.

    :returns: Return CPU information as a string
    """
    cpu = match_line('/proc/cpuinfo', 'model name')
    return cpu.split(':')[1] if cpu else cpu

def get_nic():
    """Get NIC(s) information.

    :returns: Return NIC(s) information as a list
    """
    nics = []
    output = subprocess.check_output('lspci', shell=True)
    output = output.decode(locale.getdefaultlocale()[1])
    for line in output.split('\n'):
        for nic in S.getValue('NICS'):
            # lspci shows PCI addresses without domain part, i.e. last 7 chars
            if line.startswith(nic['pci'][-7:]):
                nics.append(''.join(line.split(':')[2:]).strip())
    return nics

def get_platform():
    """Get platform information.

    Currently this is the motherboard vendor, name and socket
    count.

    :returns: Return platform information as a string
    """
    output = []

    with open('/sys/class/dmi/id/board_vendor', 'r') as file_:
        output.append(file_.readline().rstrip())

    with open('/sys/class/dmi/id/board_name', 'r') as file_:
        output.append(file_.readline().rstrip())

    num_nodes = len([name for name in os.listdir(
        '/sys/devices/system/node/') if name.startswith('node')])
    output.append(''.join(['[', str(num_nodes), ' sockets]']))

    return ' '.join(output).strip()

def get_cpu_cores():
    """Get number of CPU cores.

    :returns: Return number of CPU cores
    """
    cores = 0
    with open('/proc/cpuinfo') as file_:
        for line in file_:
            if line.rstrip('\n').startswith('processor'):
                cores += 1
            continue

    # this code must be executed by at leat one core...
    if cores < 1:
        cores = 1
    return cores

def get_memory():
    """Get memory information.

    :returns: amount of system memory as string together with unit
    """
    memory = match_line('/proc/meminfo', 'MemTotal')
    return memory.split(':')[1].strip() if memory else memory

def get_memory_bytes():
    """Get memory information in bytes

    :returns: amount of system memory
    """
    mem_list = get_memory().split(' ')
    mem = float(mem_list[0].strip())
    if mem_list.__len__() > 1:
        unit = mem_list[1].strip().lower()
        if unit == 'kb':
            mem *= 1024
        elif unit == 'mb':
            mem *= 1024 ** 2
        elif unit == 'gb':
            mem *= 1024 ** 3
        elif unit == 'tb':
            mem *= 1024 ** 4

    return int(mem)

def get_pids(proc_names_list):
    """ Get pid(s) of process(es) with given name(s)

    :returns: list with pid(s) of given processes or None if processes
        with given names are not running
    """

    try:
        pids = subprocess.check_output(['sudo', 'LC_ALL=' + S.getValue('DEFAULT_CMD_LOCALE'), 'pidof']
                                       + proc_names_list)
    except subprocess.CalledProcessError:
        # such process isn't running
        return None

    return list(map(str, map(int, pids.split())))

def get_pid(proc_name_str):
    """ Get pid(s) of process with given name

    :returns: list with pid(s) of given process or None if process
        with given name is not running
    """
    return get_pids([proc_name_str])

# This function uses long switch per purpose, so let us suppress pylint warning too-many-branches
# pylint: disable=R0912
def get_version(app_name):
    """ Get version of given application and its git tag

    :returns: dictionary {'name' : app_name, 'version' : app_version, 'git_tag' : app_git_tag) in case that
        version or git tag are not known or not applicaple, than None is returned for any unknown value

    """
    app_version_file = {
        'ovs' : os.path.join(S.getValue('OVS_DIR'), 'include/openvswitch/version.h'),
        'dpdk' : os.path.join(S.getValue('RTE_SDK'), 'lib/librte_eal/common/include/rte_version.h'),
        'qemu' : os.path.join(S.getValue('QEMU_DIR'), 'VERSION'),
        'l2fwd' : os.path.join(S.getValue('ROOT_DIR'), 'src/l2fwd/l2fwd.c'),
        'ixnet' : os.path.join(S.getValue('TRAFFICGEN_IXNET_LIB_PATH'), 'pkgIndex.tcl')
    }


    def get_git_tag(path):
        """ get tag of recent commit from repository located at 'path'

        :returns: git tag in form of string with commit hash or None if there
            isn't any git repository at given path
        """
        try:
            if os.path.isdir(path):
                return subprocess.check_output('cd {}; git rev-parse HEAD'.format(path), shell=True,
                                               stderr=subprocess.DEVNULL).decode().rstrip('\n')
            elif os.path.isfile(path):
                return subprocess.check_output('cd $(dirname {}); git log -1 --pretty="%H" {}'.format(path, path),
                                               shell=True, stderr=subprocess.DEVNULL).decode().rstrip('\n')
            else:
                return None
        except subprocess.CalledProcessError:
            return None


    app_version = None
    app_git_tag = None

    if app_name.lower().startswith('ovs'):
        app_version = match_line(app_version_file['ovs'], '#define OVS_PACKAGE_VERSION')
        if app_version:
            app_version = app_version.split('"')[1]
        app_git_tag = get_git_tag(S.getValue('OVS_DIR'))
    elif app_name.lower() in ['dpdk', 'testpmd']:
        tmp_ver = ['', '', '']
        found = False
        with open(app_version_file['dpdk']) as file_:
            for line in file_:
                if not line.strip():
                    continue
                if line.startswith('#define RTE_VER_MAJOR'):
                    found = True
                    tmp_ver[0] = line.rstrip('\n').split(' ')[2]
                if line.startswith('#define RTE_VER_MINOR'):
                    found = True
                    tmp_ver[1] = line.rstrip('\n').split(' ')[2]
                if line.startswith('#define RTE_VER_PATCH_LEVEL'):
                    found = True
                    tmp_ver[2] = line.rstrip('\n').split(' ')[2]

        if found:
            app_version = '.'.join(tmp_ver)
        app_git_tag = get_git_tag(S.getValue('RTE_SDK'))
    elif app_name.lower().startswith('qemu'):
        app_version = match_line(app_version_file['qemu'], '')
        app_git_tag = get_git_tag(S.getValue('QEMU_DIR'))
    elif app_name.lower() == 'ixnet':
        app_version = match_line(app_version_file['ixnet'], 'package provide IxTclNetwork')
        if app_version:
            app_version = app_version.split(' ')[3]
    elif app_name.lower() == 'dummy':
        # get git tag of file with Dummy implementation
        app_git_tag = get_git_tag(os.path.join(S.getValue('ROOT_DIR'), 'tools/pkt_gen/dummy/dummy.py'))
    elif app_name.lower() == 'vswitchperf':
        app_git_tag = get_git_tag(S.getValue('ROOT_DIR'))
    elif app_name.lower() == 'l2fwd':
        app_version = match_line(app_version_file[app_name], 'MODULE_VERSION')
        if app_version:
            app_version = app_version.split('"')[1]
        app_git_tag = get_git_tag(app_version_file[app_name])
    elif app_name.lower() in ['linux_bridge', 'buildin']:
        # without login into running VM, it is not possible to check bridge_utils version
        app_version = 'NA'
        app_git_tag = 'NA'

    return {'name' : app_name, 'version' : app_version, 'git_tag' : app_git_tag}
