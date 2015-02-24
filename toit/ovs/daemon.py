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

"""
Automation of ``ovs-vswitchd``.

Part of 'toit' - The OVS Integration Testsuite.
"""

import os
import logging
import pexpect

from toit import utils
from toit.conf import settings

OVS_VSWITCHD_BIN = os.path.join(
    getattr(settings, 'OVS_DIR'), 'vswitchd', 'ovs-vswitchd')
OVSDB_TOOL_BIN = os.path.join(
    getattr(settings, 'OVS_DIR'), 'ovsdb', 'ovsdb-tool')
OVSDB_SERVER_BIN = os.path.join(
    getattr(settings, 'OVS_DIR'), 'ovsdb', 'ovsdb-server')
VSWITCHD_PID = os.path.join(
    getattr(settings, 'LOG_DIR'), 'vswitchd.pid')

OVS_VAR_DIR = '/usr/local/var/run/openvswitch/'
OVS_ETC_DIR = '/usr/local/etc/openvswitch/'

LOG_FILE_VSWITCHD = os.path.join(
    getattr(settings, 'LOG_DIR'), getattr(settings, 'LOG_FILE_VSWITCHD'))


class VSwitchd(utils.Process):
    """
    Wrapper to control instances of ``ovs-vswitchd``.
    """
    _ovsdb_pid = None
    _logfile = LOG_FILE_VSWITCHD

    # the pid file argument *must* have an equals sign. If not, you get a
    # warning like so:
    #  xxx reconnect|INFO|/tmp/vswitchd.pid: waiting 8 seconds before reconnect
    _cmd = ['sudo', '-E', OVS_VSWITCHD_BIN, '--dpdk', '-c', '0x2', '-n', '4',
            '--socket-mem 1024,0', '--', '--pidfile=%s' % VSWITCHD_PID,
            '--log-file']
    _expect = r'EAL: Master core \d+ is ready'
    _proc_name = 'ovs-vswitchd'

    def __init__(self, timeout=30):
        """
        Initialise the wrapper with a specific start timeout.

        :param timeout: Timeout to wait for application to start.

        :returns: None
        """
        self._logger = logging.getLogger(__name__)
        self._timeout = timeout

    # startup/shutdown

    def start(self):
        """
        Start ``ovs-vswitchd`` instance.
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
        """
        Kill ``ovs-vswitchd`` instance if it is alive.
        """
        self._logger.info('Killing ovs-vswitchd...')

        self._kill_ovsdb()

        super(VSwitchd, self).kill()

    # helper functions

    def _reset_ovsdb(self):
        """
        Reset system for 'ovsdb'.
        """
        self._logger.info('Resetting system after last run...')

        utils.run_task(['sudo', 'rm', '-rf', OVS_VAR_DIR], self._logger)
        utils.run_task(['sudo', 'mkdir', '-p', OVS_VAR_DIR], self._logger)
        utils.run_task(['sudo', 'rm', '-rf', OVS_ETC_DIR], self._logger)
        utils.run_task(['sudo', 'mkdir', '-p', OVS_ETC_DIR], self._logger)

        utils.run_task(['sudo', 'rm', '-f',
                        os.path.join(OVS_ETC_DIR, 'conf.db')],
                       self._logger)

        self._logger.info('System reset after last run.')

    def _start_ovsdb(self):
        """
        Start ``ovsdb-server`` instance.
        """
        utils.run_task(['sudo', OVSDB_TOOL_BIN, 'create',
                        os.path.join(OVS_ETC_DIR, 'conf.db'),
                        os.path.join(getattr(settings, 'OVS_DIR'), 'vswitchd',
                                     'vswitch.ovsschema')],
                       self._logger,
                       'Creating ovsdb configuration database...')

        self._ovsdb_pid = utils.run_background_task(
            ['sudo', OVSDB_SERVER_BIN,
             '--remote=punix:%s' % os.path.join(OVS_VAR_DIR, 'db.sock'),
             '--remote=db:Open_vSwitch,Open_vSwitch,manager_options'],
            self._logger,
            'Starting ovsdb-server...')

    def _kill_ovsdb(self):
        """
        Kill ``ovsdb-server`` instance.
        """
        if self._ovsdb_pid:
            utils.run_task(['sudo', 'kill', '-2', str(self._ovsdb_pid)],
                           self._logger, 'Killing ovsdb-server...')
