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

_OVS_VAR_DIR = settings.getValue('OVS_VAR_DIR')
_OVS_ETC_DIR = settings.getValue('OVS_ETC_DIR')

_LOG_FILE_VSWITCHD = os.path.join(
    settings.getValue('LOG_DIR'), settings.getValue('LOG_FILE_VSWITCHD'))

class VSwitchd(tasks.Process):
    """Class wrapper for controlling an OVS instance.

    Wraps a pair of ``ovs-vswitchd`` and ``ovsdb-server`` processes.
    """
    _ovsdb_pid = None
    _logfile = _LOG_FILE_VSWITCHD
    _ovsdb_pidfile_path = os.path.join(settings.getValue('LOG_DIR'), "ovsdb_pidfile.pid")
    _proc_name = 'ovs-vswitchd'

    def __init__(self, timeout=30, vswitchd_args=None, expected_cmd=None):
        """Initialise the wrapper with a specific start timeout and extra
        parameters.

        :param timeout: Timeout to wait for application to start.
        :param vswitchd_args: Command line parameters for vswitchd.

        :returns: None
        """
        self._logger = logging.getLogger(__name__)
        self._timeout = timeout
        self._expect = expected_cmd
        vswitchd_args = vswitchd_args or []
        ovs_vswitchd_bin = os.path.join(
            settings.getValue('OVS_DIR'), 'vswitchd', 'ovs-vswitchd')
        self._cmd = ['sudo', '-E', ovs_vswitchd_bin] + vswitchd_args

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
            logging.error("Exception during VSwitch start.")
            self._kill_ovsdb()
            raise exc

    def kill(self, signal='-15', sleep=2):
        """Kill ``ovs-vswitchd`` instance if it is alive.

        :returns: None
        """
        self._logger.info('Killing ovs-vswitchd...')

        self._kill_ovsdb()

        super(VSwitchd, self).kill(signal, sleep)

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
        ovsdb_tool_bin = os.path.join(
            settings.getValue('OVS_DIR'), 'ovsdb', 'ovsdb-tool')
        tasks.run_task(['sudo', ovsdb_tool_bin, 'create',
                        os.path.join(_OVS_ETC_DIR, 'conf.db'),
                        os.path.join(settings.getValue('OVS_DIR'), 'vswitchd',
                                     'vswitch.ovsschema')],
                       self._logger,
                       'Creating ovsdb configuration database...')

        ovsdb_server_bin = os.path.join(
            settings.getValue('OVS_DIR'), 'ovsdb', 'ovsdb-server')

        tasks.run_background_task(
            ['sudo', ovsdb_server_bin,
             '--remote=punix:%s' % os.path.join(_OVS_VAR_DIR, 'db.sock'),
             '--remote=db:Open_vSwitch,Open_vSwitch,manager_options',
             '--pidfile=' + self._ovsdb_pidfile_path, '--overwrite-pidfile'],
            self._logger,
            'Starting ovsdb-server...')

    def _kill_ovsdb(self):
        """Kill ``ovsdb-server`` instance.

        :returns: None
        """
        with open(self._ovsdb_pidfile_path, "r") as pidfile:
            ovsdb_pid = pidfile.read().strip()

        self._logger.info("Killing ovsdb with pid: " + ovsdb_pid)

        if ovsdb_pid:
            tasks.run_task(['sudo', 'kill', '-15', str(ovsdb_pid)],
                           self._logger, 'Killing ovsdb-server...')

    @staticmethod
    def get_db_sock_path():
        """Method returns location of db.sock file

        :returns: path to db.sock file.
        """
        return os.path.join(_OVS_VAR_DIR, 'db.sock')
