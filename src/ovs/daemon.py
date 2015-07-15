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

"""Class wrapper for controlling an OVS instance.

Wraps a pair of ``ovs-vswitchd`` and ``ovsdb-server`` processes.
"""

import os
import logging
import pexpect

from conf import settings
from tools import tasks

_OVS_VSWITCHD_BIN = os.path.join(
    settings.getValue('OVS_DIR'), 'vswitchd', 'ovs-vswitchd')
_OVSDB_TOOL_BIN = os.path.join(
    settings.getValue('OVS_DIR'), 'ovsdb', 'ovsdb-tool')
_OVSDB_SERVER_BIN = os.path.join(
    settings.getValue('OVS_DIR'), 'ovsdb', 'ovsdb-server')

_OVS_VAR_DIR = '/usr/local/var/run/openvswitch/'
_OVS_ETC_DIR = '/usr/local/etc/openvswitch/'

_LOG_FILE_VSWITCHD = os.path.join(
    settings.getValue('LOG_DIR'), settings.getValue('LOG_FILE_VSWITCHD'))

class VSwitchd(tasks.Process):
    """Class wrapper for controlling an OVS instance.

    Wraps a pair of ``ovs-vswitchd`` and ``ovsdb-server`` processes.
    """
    _ovsdb_pid = None
    _logfile = _LOG_FILE_VSWITCHD


    _expect = r'EAL: Master l*core \d+ is ready'
    _proc_name = 'ovs-vswitchd'

    def __init__(self, timeout=60, vswitchd_args=None):
        """Initialise the wrapper with a specific start timeout and extra
        parameters.

        :param timeout: Timeout to wait for application to start.
        :param vswitchd_args: Command line parameters for vswitchd.

        :returns: None
        """
        self._logger = logging.getLogger(__name__)
        self._timeout = timeout
        vswitchd_args = vswitchd_args or []

        self._cmd = ['sudo', '-E', _OVS_VSWITCHD_BIN] + vswitchd_args

    # startup/shutdown

    def start(self):
        """ Start ``ovsdb-server`` and ``ovs-vswitchd`` instance.

        :returns: None
        :raises: pexpect.EOF, pexpect.TIMEOUT
        """
        self._reset_ovsdb()
        self._start_ovsdb()  # this has to be started first

        try:
            super(VSwitchd, self).start()
            self.relinquish()
        except (pexpect.EOF, pexpect.TIMEOUT) as exc:
            self._kill_ovsdb()
            raise exc

    def kill(self):
        """Kill ``ovs-vswitchd`` instance if it is alive.

        :returns: None
        """
        self._logger.info('Killing ovs-vswitchd...')

        self._kill_ovsdb()

        super(VSwitchd, self).kill()

    # helper functions

    def _reset_ovsdb(self):
        """Reset system for 'ovsdb'.

        :returns: None
        """
        self._logger.info('Resetting system after last run...')

        tasks.run_task(['sudo', 'rm', '-rf', _OVS_VAR_DIR], self._logger)
        tasks.run_task(['sudo', 'mkdir', '-p', _OVS_VAR_DIR], self._logger)
        tasks.run_task(['sudo', 'rm', '-rf', _OVS_ETC_DIR], self._logger)
        tasks.run_task(['sudo', 'mkdir', '-p', _OVS_ETC_DIR], self._logger)

        tasks.run_task(['sudo', 'rm', '-f',
                        os.path.join(_OVS_ETC_DIR, 'conf.db')],
                       self._logger)

        self._logger.info('System reset after last run.')

    def _start_ovsdb(self):
        """Start ``ovsdb-server`` instance.

        :returns: None
        """
        tasks.run_task(['sudo', _OVSDB_TOOL_BIN, 'create',
                        os.path.join(_OVS_ETC_DIR, 'conf.db'),
                        os.path.join(settings.getValue('OVS_DIR'), 'vswitchd',
                                     'vswitch.ovsschema')],
                       self._logger,
                       'Creating ovsdb configuration database...')

        self._ovsdb_pid = tasks.run_background_task(
            ['sudo', _OVSDB_SERVER_BIN,
             '--remote=punix:%s' % os.path.join(_OVS_VAR_DIR, 'db.sock'),
             '--remote=db:Open_vSwitch,Open_vSwitch,manager_options'],
            self._logger,
            'Starting ovsdb-server...')

    def _kill_ovsdb(self):
        """Kill ``ovsdb-server`` instance.

        :returns: None
        """
        if self._ovsdb_pid:
            tasks.run_task(['sudo', 'kill', '-15', str(self._ovsdb_pid)],
                           self._logger, 'Killing ovsdb-server...')
