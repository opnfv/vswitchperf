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

"""Automation of system configuration for DPDK use.

Parts of this based on ``tools/dpdk_nic_bind.py`` script from Intel(R)
DPDK.
"""

from sys import platform as _platform

import os
import re
import subprocess
import logging
import locale

from tools import tasks
from conf import settings
from tools.module_manager import ModuleManager

_LOGGER = logging.getLogger(__name__)
RTE_PCI_TOOL = os.path.join(
    settings.getValue('RTE_SDK'), 'tools', 'dpdk_nic_bind.py')

_DPDK_MODULE_MANAGER = ModuleManager()

#
# system management
#


def init():
    """Setup system for DPDK.
    """
    if not _is_linux():
        _LOGGER.error('Not running on a compatible Linux version. Exiting...')
        return

    _mount_hugepages()
    _insert_modules()
    _remove_vhost_net()
    _bind_nics()


def cleanup():
    """Setup system for DPDK.
    """
    if not _is_linux():
        _LOGGER.error('Not running on a compatible Linux version. Exiting...')
        return

    _unbind_nics()
    _remove_modules()
    _umount_hugepages()
    _vhost_user_cleanup()


#
# vhost specific modules management
#


def insert_vhost_modules():
    """Inserts VHOST related kernel modules
    """
    mod_path_prefix = os.path.join(settings.getValue('RTE_SDK'),
                                   'lib',
                                   'librte_vhost')
    _insert_module_group('VHOST_MODULE', mod_path_prefix)


def remove_vhost_modules():
    """Removes all VHOST related kernel modules
    """
    _remove_module_group('VHOST_MODULE')

#
# basic compatibility test
#


def _is_linux():
    """Check if running on Linux.

    Many of the functions in this file rely on features commonly found
    only on Linux (i.e. ``/proc`` is not present on FreeBSD). Hence, this
    check is important to ensure someone doesn't run this on an incompatible
    OS or distro.
    """
    return _platform.startswith('linux') and os.path.isdir('/proc')

#
# hugepage management
#


def _is_hugepage_available():
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
        if not num_huge:
            _LOGGER.info('No free hugepages.')
        else:
            _LOGGER.info('Found \'%s\' free hugepage(s).', num_huge)
        return True

    return False


def _is_hugepage_mounted():
    """Check if hugepages are mounted.
    """
    output = subprocess.check_output(['mount'], shell=True)
    my_encoding = locale.getdefaultlocale()[1]
    for line in output.decode(my_encoding).split('\n'):
        if 'hugetlbfs' in line:
            return True

    return False


def _mount_hugepages():
    """Ensure hugepages are mounted.
    """
    if not _is_hugepage_available():
        return

    if _is_hugepage_mounted():
        return

    if not os.path.exists(settings.getValue('HUGEPAGE_DIR')):
        os.makedirs(settings.getValue('HUGEPAGE_DIR'))
    try:
        tasks.run_task(['sudo', 'mount', '-t', 'hugetlbfs', 'nodev',
                        settings.getValue('HUGEPAGE_DIR')],
                       _LOGGER, 'Mounting hugepages...', True)
    except subprocess.CalledProcessError:
        _LOGGER.error('Unable to mount hugepages.')


def _umount_hugepages():
    """Ensure hugepages are unmounted.
    """
    if not _is_hugepage_mounted():
        return

    try:
        tasks.run_task(['sudo', 'umount', settings.getValue('HUGEPAGE_DIR')],
                       _LOGGER, 'Unmounting hugepages...', True)
    except subprocess.CalledProcessError:
        _LOGGER.error('Unable to umount hugepages.')

#
# module management
#


def _is_module_inserted(module):
    """Check if a module is inserted on system.
    """
    with open('/proc/modules') as mod_file:
        loaded_mods = mod_file.readlines()

    # first check if module is loaded
    for line in loaded_mods:
        if line.startswith(module):
            return True
    return False


def _insert_modules():
    """Ensure required modules are inserted on system.
    """

    _DPDK_MODULE_MANAGER.insert_modules(settings.getValue('SYS_MODULES'))

    mod_path_prefix = settings.getValue('OVS_DIR')
    _insert_module_group('OVS_MODULES', mod_path_prefix)
    mod_path_prefix = os.path.join(settings.getValue('RTE_SDK'),
                                   settings.getValue('RTE_TARGET'))
    _insert_module_group('DPDK_MODULES', mod_path_prefix)


def _insert_module_group(module_group, group_path_prefix):
    """Ensure all modules in a group are inserted into the system.

    :param module_group: A name of configuration item containing a list
    of module names
    """
    for module in settings.getValue(module_group):
        # first check if module is loaded
        if _is_module_inserted(module[1]):
            continue

        try:
            mod_path = os.path.join(group_path_prefix, module[0],
                                    '%s.ko' % module[1])
            tasks.run_task(['sudo', 'insmod', mod_path], _LOGGER,
                           'Inserting module \'%s\'...' % module[1], True)
        except subprocess.CalledProcessError:
            _LOGGER.error('Unable to insert module \'%s\'.', module[1])
            raise  # fail catastrophically


def _remove_modules():
    """Ensure required modules are removed from system.
    """
    _remove_module_group('OVS_MODULES')
    _remove_module_group('DPDK_MODULES')

    _DPDK_MODULE_MANAGER.remove_modules()

def _remove_module_group(module_group):
    """Ensure all modules in a group are removed from the system.

    :param module_group: A name of configuration item containing a list
    of module names
    """
    for module in settings.getValue(module_group):
        # first check if module is loaded
        if not _is_module_inserted(module[1]):
            continue

        try:
            tasks.run_task(['sudo', 'rmmod', module[1]], _LOGGER,
                           'Removing module \'%s\'...' % module[1], True)
        except subprocess.CalledProcessError:
            _LOGGER.error('Unable to remove module \'%s\'.', module[1])
            continue


#
# 'vhost-net' module management
#

def _remove_vhost_net():
    """Remove vhost-net driver and file.
    """
    if _is_module_inserted('vhost_net'):
        try:
            tasks.run_task(['sudo', 'rmmod', 'vhost_net'], _LOGGER,
                           'Removing \'/dev/vhost-net\' directory...', True)
        except subprocess.CalledProcessError:
            _LOGGER.error('Unable to remove module \'vhost_net\'.')

    try:
        tasks.run_task(['sudo', 'rm', '-f', '/dev/vhost-net'], _LOGGER,
                       'Removing \'/dev/vhost-net\' directory...', True)
    except subprocess.CalledProcessError:
        _LOGGER.error('Unable to remove directory \'/dev/vhost-net\'.')

#
# NIC management
#


def _bind_nics():
    """Bind NICs using the Intel DPDK ``dpdk_nic_bind.py`` tool.
    """
    try:
        tasks.run_task(['sudo', RTE_PCI_TOOL, '--bind', 'igb_uio'] +
                       settings.getValue('WHITELIST_NICS'), _LOGGER,
                       'Binding NICs %s...' %
                       settings.getValue('WHITELIST_NICS'),
                       True)
    except subprocess.CalledProcessError:
        _LOGGER.error('Unable to bind NICs %s',
                      str(settings.getValue('WHITELIST_NICS')))

def _unbind_nics_get_driver():
    """Check what driver the NICs should be bound to
       after unbinding them from DPDK.
    """
    _driver_list = []
    _output = subprocess.check_output([RTE_PCI_TOOL, '--status'])
    _my_encoding = locale.getdefaultlocale()[1]
    for line in _output.decode(_my_encoding).split('\n'):
        for nic in settings.getValue('WHITELIST_NICS'):
            if nic in line:
                _driver_list.append((line.split("unused=", 1)[1]))
    return _driver_list

def _unbind_nics():
    """Unbind NICs using the Intel DPDK ``dpdk_nic_bind.py`` tool.
    """
    nic_drivers = _unbind_nics_get_driver()
    try:
        tasks.run_task(['sudo', RTE_PCI_TOOL, '--unbind'] +
                       settings.getValue('WHITELIST_NICS'), _LOGGER,
                       'Unbinding NICs %s...' %
                       str(settings.getValue('WHITELIST_NICS')),
                       True)
    except subprocess.CalledProcessError:
        _LOGGER.error('Unable to unbind NICs %s',
                      str(settings.getValue('WHITELIST_NICS')))
    # Rebind NICs to their original drivers
    # using the Intel DPDK ``dpdk_nic_bind.py`` tool.
    for i, nic in enumerate(settings.getValue('WHITELIST_NICS')):
        try:
            if nic_drivers[i] != '':
                tasks.run_task(['sudo', RTE_PCI_TOOL, '--bind',
                                nic_drivers[i], nic],
                               _LOGGER, 'Binding NIC %s...' %
                               nic,
                               True)
        except subprocess.CalledProcessError:
            _LOGGER.error('Unable to bind NICs %s to drivers %s',
                          str(settings.getValue('WHITELIST_NICS')),
                          nic_drivers)



#
# Vhost-user cleanup
#

def _vhost_user_cleanup():
    """Remove files created by vhost-user tests.
    """
    for sock in settings.getValue('VHOST_USER_SOCKS'):
        if os.path.exists(sock):
            try:
                tasks.run_task(['sudo', 'rm', sock],
                               _LOGGER,
                               'Deleting vhost-user socket \'%s\'...' %
                               sock,
                               True)

            except subprocess.CalledProcessError:
                _LOGGER.error('Unable to delete vhost-user socket \'%s\'.',
                              sock)
                continue


class Dpdk(object):
    """A context manager for the system init/cleanup.
    """
    def __enter__(self):
        _LOGGER.info('Setting up DPDK')
        init()
        return self

    def __exit__(self, type_, value, traceback):
        _LOGGER.info('Cleaning up DPDK')
        cleanup()
