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

from tools import tasks
from conf import settings

_LOGGER = logging.getLogger(__name__)

#
# hugepage management
#

def allocate_hugepages():
    """Allocate hugepages on the fly
    """

    nr_hugepages = 'vm.nr_hugepages=' + settings.getValue('NR_HUGEPAGES')
    try:
        tasks.run_task(['sudo', 'sysctl', nr_hugepages],
                       _LOGGER, 'Trying to allocate hugepages..', True)
    except subprocess.CalledProcessError:
        _LOGGER.error('Unable to allocate hugepages.')


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
            allocate_hugepages()
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


