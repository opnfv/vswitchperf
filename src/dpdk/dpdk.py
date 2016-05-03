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

"""Automation of system configuration for DPDK use.

Parts of this based on ``tools/dpdk_nic_bind.py`` script from Intel(R)
DPDK.
"""

from sys import platform as _platform

import os
import subprocess
import logging

from tools import tasks
from conf import settings
from tools.module_manager import ModuleManager

_LOGGER = logging.getLogger(__name__)
RTE_PCI_TOOL = os.path.join(
    settings.getValue('RTE_SDK_USER'), 'tools', 'dpdk_nic_bind.py')

_DPDK_MODULE_MANAGER = ModuleManager()

# declare global NIC variables only as their content might not be known yet
_NICS = []
_NICS_PCI = []

#
# system management
#

def init():
    """Setup system for DPDK.
    """
    global _NICS
    global _NICS_PCI
    _NICS = settings.getValue('NICS')
    _NICS_PCI = list(nic['pci'] for nic in _NICS)
    if not _is_linux():
        _LOGGER.error('Not running on a compatible Linux version. Exiting...')
        return
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
    _vhost_user_cleanup()

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
# module management
#

def _insert_modules():
    """Ensure required modules are inserted on system.
    """

    _DPDK_MODULE_MANAGER.insert_modules(settings.getValue('SYS_MODULES'))

    mod_path_prefix = settings.getValue('OVS_DIR')
    _DPDK_MODULE_MANAGER.insert_module_group(settings.getValue('OVS_MODULES'),
                                             mod_path_prefix)
    if 'vfio-pci' not in settings.getValue('DPDK_MODULES'):
        mod_path_prefix = os.path.join(settings.getValue('RTE_SDK'),
                                       settings.getValue('RTE_TARGET'))
        _DPDK_MODULE_MANAGER.insert_module_group(settings.getValue('DPDK_MODULES'),
                                                 mod_path_prefix)
    else:
        _DPDK_MODULE_MANAGER.insert_modules(settings.getValue('DPDK_MODULES'))

def _remove_modules():
    """Ensure required modules are removed from system.
    """
    _DPDK_MODULE_MANAGER.remove_modules()

#
# vhost specific modules management
#

def insert_vhost_modules():
    """Inserts VHOST related kernel modules
    """
    mod_path_prefix = os.path.join(settings.getValue('RTE_SDK'),
                                   'lib',
                                   'librte_vhost')
    _DPDK_MODULE_MANAGER.insert_module_group(settings.getValue('VHOST_MODULE'), mod_path_prefix)


def remove_vhost_modules():
    """Removes all VHOST related kernel modules
    """
    # all modules are removed automatically by _remove_modules() method
    pass


#
# 'vhost-net' module cleanup
#

def _remove_vhost_net():
    """Remove vhost-net driver and file.
    """
    _DPDK_MODULE_MANAGER.remove_module('vhost-net')
    try:
        tasks.run_task(['sudo', 'rm', '-f', '/dev/vhost-net'], _LOGGER,
                       'Removing \'/dev/vhost-net\' directory...', True)
    except subprocess.CalledProcessError:
        _LOGGER.error('Unable to remove directory \'/dev/vhost-net\'.')

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
#
# NIC management
#


def _bind_nics():
    """Bind NICs using the Intel DPDK ``dpdk_nic_bind.py`` tool.
    """
    try:
        _driver = 'igb_uio'
        if 'vfio-pci' in settings.getValue('DPDK_MODULES'):
            _driver = 'vfio-pci'
            tasks.run_task(['sudo', 'chmod', 'a+x', '/dev/vfio'],
                           _LOGGER, 'Setting VFIO permissions .. a+x',
                           True)
            tasks.run_task(['sudo', 'chmod', '-R', '666', '/dev/vfio/'],
                           _LOGGER, 'Setting VFIO permissions .. 0666',
                           True)

        tasks.run_task(['sudo', RTE_PCI_TOOL, '--bind=' + _driver] +
                       _NICS_PCI, _LOGGER,
                       'Binding NICs %s...' % _NICS_PCI,
                       True)
    except subprocess.CalledProcessError:
        _LOGGER.error('Unable to bind NICs %s', str(_NICS_PCI))

def _unbind_nics():
    """Unbind NICs using the Intel DPDK ``dpdk_nic_bind.py`` tool.
    """
    try:
        tasks.run_task(['sudo', RTE_PCI_TOOL, '--unbind'] +
                       _NICS_PCI, _LOGGER,
                       'Unbinding NICs %s...' % str(_NICS_PCI),
                       True)
    except subprocess.CalledProcessError:
        _LOGGER.error('Unable to unbind NICs %s', str(_NICS_PCI))
    # Rebind NICs to their original drivers
    # using the Intel DPDK ``dpdk_nic_bind.py`` tool.
    for nic in _NICS:
        try:
            if nic['driver']:
                tasks.run_task(['sudo', RTE_PCI_TOOL, '--bind',
                                nic['driver'], nic['pci']],
                               _LOGGER, 'Binding NIC %s to %s...' %
                               (nic['pci'], nic['driver']),
                               True)
        except subprocess.CalledProcessError:
            _LOGGER.error('Unable to bind NIC %s to driver %s',
                          nic['pci'], nic['driver'])

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
