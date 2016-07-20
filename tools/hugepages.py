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

"""Automation of hugepages management
"""

import os
import re
import subprocess
import logging
import locale
import math

from tools import tasks
from conf import settings

_LOGGER = logging.getLogger(__name__)

#
# hugepage management
#

def get_hugepage_size():
    """Return the size of the configured hugepages
    """
    hugepage_size_re = re.compile(r'^Hugepagesize:\s+(?P<size_hp>\d+)\s+kB',
                                  re.IGNORECASE)
    with open('/proc/meminfo', 'r') as fh:
        data = fh.readlines()
        for line in data:
            match = hugepage_size_re.search(line)
            if match:
                _LOGGER.info('Hugepages size: %s', match.group('size_hp'))
                return int(match.group('size_hp'))
        else:
            _LOGGER.error('Could not parse for hugepage size')
            return 0



def allocate_hugepages():
    """Allocate hugepages on the fly
    """
    hp_size = get_hugepage_size()

    if hp_size > 0:
        nr_hp = int(math.ceil(settings.getValue('HP_RAM_ALLOCATION')/hp_size))
        _LOGGER.info('Will allocate %s hugepages.', nr_hp)

        nr_hugepages = 'vm.nr_hugepages=' + str(nr_hp)
        try:
            tasks.run_task(['sudo', 'sysctl', nr_hugepages],
                           _LOGGER, 'Trying to allocate hugepages..', True)
        except subprocess.CalledProcessError:
            _LOGGER.error('Unable to allocate hugepages.')
            return False
        return True

    else:
        _LOGGER.error('Division by 0 will be supported in next release')
        return False


def is_hugepage_available():
    """Check if hugepages are available on the system.
    """
    hugepage_re = re.compile(r'^HugePages_Free:\s+(?P<num_hp>\d+)$')

    # read in meminfo
    with open('/proc/meminfo') as mem_file:
        mem_info = mem_file.readlines()

    # first check if module is loaded
    for line in mem_info:
        result = hugepage_re.match(line)
        if not result:
            continue

        num_huge = result.group('num_hp')
        if num_huge == '0':
            _LOGGER.info('No free hugepages.')
            if not allocate_hugepages():
                return 
        else:
            _LOGGER.info('Found \'%s\' free hugepage(s).', num_huge)
        return True

    return False


def is_hugepage_mounted():
    """Check if hugepages are mounted.
    """
    output = subprocess.check_output(['mount'], shell=True)
    my_encoding = locale.getdefaultlocale()[1]
    for line in output.decode(my_encoding).split('\n'):
        if 'hugetlbfs' in line:
            return True

    return False


def mount_hugepages():
    """Ensure hugepages are mounted.
    """
    if not is_hugepage_available():
        return

    if is_hugepage_mounted():
        return

    if not os.path.exists(settings.getValue('HUGEPAGE_DIR')):
        tasks.run_task(['sudo', 'mkdir', settings.getValue('HUGEPAGE_DIR')], _LOGGER,
                       'Creating directory ' + settings.getValue('HUGEPAGE_DIR'), True)
    try:
        tasks.run_task(['sudo', 'mount', '-t', 'hugetlbfs', 'nodev',
                        settings.getValue('HUGEPAGE_DIR')],
                       _LOGGER, 'Mounting hugepages...', True)
    except subprocess.CalledProcessError:
        _LOGGER.error('Unable to mount hugepages.')


def umount_hugepages():
    """Ensure hugepages are unmounted.
    """
    if not is_hugepage_mounted():
        return

    try:
        tasks.run_task(['sudo', 'umount', settings.getValue('HUGEPAGE_DIR')],
                       _LOGGER, 'Unmounting hugepages...', True)
    except subprocess.CalledProcessError:
        _LOGGER.error('Unable to umount hugepages.')


