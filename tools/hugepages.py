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


def is_hugepage_available():
    """Check if hugepages are configured/available on the system.
    """
    hugepage_size_re = re.compile(r'^Hugepagesize:\s+(?P<size_hp>\d+)\s+kB',
                                  re.IGNORECASE)

    # read in meminfo
    with open('/proc/meminfo') as mem_file:
        mem_info = mem_file.readlines()

    # see if the hugepage size is the recommended value
    for line in mem_info:
        match_size = hugepage_size_re.match(line)
        if match_size:
            if match_size.group('size_hp') != '1048576':
                _LOGGER.warn(
                    '%s%s%s kB',
                    'Hugepages not configured for recommend 1GB size. ',
                    'Currently set at ', match_size.group('size_hp'))

    # make sure we have at least 1 hugepage configured.
    with open('/proc/sys/vm/nr_hugepages', 'r') as fh:
        num_huge = fh.read().rstrip('\n')
        if not int(num_huge):
            _LOGGER.error('No configured hugepages. Hugepages configured: %s',
                          num_huge)
            return False
        else:
            _LOGGER.info('Found \'%s\' configured hugepage(s).', num_huge)
        return True


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
    """Ensure hugepages are mounted. Raises RuntimeError if no configured
    hugepages are available.
    """
    if not is_hugepage_available():
        raise RuntimeError('No Hugepages available.')

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


