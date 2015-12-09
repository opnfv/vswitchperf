# Copyright 2015 Intel Corporation.
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

from conf import settings

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
    with open('/proc/cpuinfo') as file_:
        for line in file_:
            if not line.strip():
                continue
            if not line.rstrip('\n').startswith('model name'):
                continue

            return line.rstrip('\n').split(':')[1]

def get_nic():
    """Get NIC(s) information.

    :returns: Return NIC(s) information as a string
    """
    nics = []
    output = subprocess.check_output('lspci', shell=True)
    output = output.decode(locale.getdefaultlocale()[1])
    for line in output.split('\n'):
        for nic_pciid in settings.getValue('WHITELIST_NICS'):
            if line.startswith(nic_pciid):
                nics.append(''.join(line.split(':')[2:]).strip())
    return ', '.join(nics).strip()

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
    with open('/proc/meminfo') as file_:
        for line in file_:
            if not line.strip():
                continue
            if not line.rstrip('\n').startswith('MemTotal'):
                continue

            return line.rstrip('\n').split(':')[1].strip()

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
        pids = subprocess.check_output(['sudo', 'LC_ALL=' + settings.getValue('DEFAULT_CMD_LOCALE'), 'pidof']
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
