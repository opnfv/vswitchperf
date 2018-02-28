# Copyright 2015-2017 Intel Corporation.
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

Parts of this based on ``tools/dpdk*bind.py`` script from Intel(R)
DPDK.
"""

from sys import platform as _platform

import os
import subprocess
import logging
import glob

from conf import settings as S
from tools import tasks
from tools.module_manager import ModuleManager

_LOGGER = logging.getLogger(__name__)

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
    # pylint: disable=global-statement
    global _NICS
    global _NICS_PCI
    _NICS = S.getValue('NICS')
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

    _DPDK_MODULE_MANAGER.insert_modules(S.getValue('TOOLS')['dpdk_modules'])

def _remove_modules():
    """Ensure required modules are removed from system.
    """
    _DPDK_MODULE_MANAGER.remove_modules()

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
    for sock in glob.glob(os.path.join(S.getValue('TOOLS')['ovs_var_tmp'],
                                       S.getValue('VHOST_USER_SOCKS'))):
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
    """Bind NICs using the bind tool specified in the configuration.
    """
    if not _NICS_PCI:
        _LOGGER.info('NICs are not configured - nothing to bind')
        return
    try:
        _driver = 'igb_uio'
        if 'vfio-pci' in S.getValue('TOOLS')['dpdk_modules']:
            _driver = 'vfio-pci'
            tasks.run_task(['sudo', 'chmod', 'a+x', '/dev/vfio'],
                           _LOGGER, 'Setting VFIO permissions .. a+x',
                           True)
            tasks.run_task(['sudo', 'chmod', '-R', '666', '/dev/vfio/'],
                           _LOGGER, 'Setting VFIO permissions .. 0666',
                           True)
        if 'driverctl' in S.getValue('TOOLS')['bind-tool'].lower():
            for nic in _NICS_PCI:
                tasks.run_task(['sudo', S.getValue('TOOLS')['bind-tool'], '-v',
                                'set-override'] + [nic] + [_driver], _LOGGER,
                               'Binding NIC %s...' % nic, True)
        else:
            tasks.run_task(['sudo', S.getValue('TOOLS')['bind-tool'],
                            '--bind=' + _driver] +
                           _NICS_PCI, _LOGGER,
                           'Binding NICs %s...' % _NICS_PCI,
                           True)
    except subprocess.CalledProcessError:
        _LOGGER.error('Unable to bind NICs %s', str(_NICS_PCI))


def _unbind_nics():
    """Unbind NICs using the bind tool specified in the configuration.
    """
    if not _NICS_PCI:
        _LOGGER.info('NICs are not configured - nothing to unbind')
        return
    try:
        if 'driverctl' in S.getValue('TOOLS')['bind-tool'].lower():
            for nic in _NICS_PCI:
                tasks.run_task(['sudo', S.getValue('TOOLS')['bind-tool'], '-v',
                                'unset-override'] + [nic], _LOGGER,
                               'Binding NIC %s...' % nic, True)
        else:
            tasks.run_task(['sudo', S.getValue('TOOLS')['bind-tool'],
                            '--unbind'] +
                           _NICS_PCI, _LOGGER,
                           'Unbinding NICs %s...' % str(_NICS_PCI),
                           True)
    except subprocess.CalledProcessError:
        _LOGGER.error('Unable to unbind NICs %s', str(_NICS_PCI))
    # Rebind NICs to their original drivers
    # using the Intel DPDK ``dpdk*bind.py`` tool.
    for nic in _NICS:
        try:
            if nic['driver']:
                if 'driverctl' in S.getValue('TOOLS')['bind-tool'].lower():
                    # driverctl restores the driver automatically on unset
                    break
                else:
                    tasks.run_task(['sudo', S.getValue('TOOLS')['bind-tool'],
                                    '--bind',
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
