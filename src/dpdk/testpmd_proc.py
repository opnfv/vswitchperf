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

"""Class wrapper for controlling a TestPMD instance.

Wraps ``testpmd`` process.
"""

import os
import logging
import time
import pexpect

from conf import settings
from tools import tasks

_TESTPMD_PROMPT = 'Done'

_TESTPMD_BIN = os.path.join(
    settings.getValue('RTE_SDK'), settings.getValue('RTE_TARGET'),
    'app', 'testpmd')

_LOG_FILE_VSWITCHD = os.path.join(
    settings.getValue('LOG_DIR'), settings.getValue('LOG_FILE_VSWITCHD'))

class TestPMDProcess(tasks.Process):
    """Class wrapper for controlling a TestPMD instance.

    Wraps ``testpmd`` process.
    """
    _logfile = _LOG_FILE_VSWITCHD
    _proc_name = 'testpmd'

    def __init__(self, timeout=30, testpmd_args=None, expected_cmd=None):
        """Initialise the wrapper with a specific start timeout and extra
        parameters.

        :param timeout: Timeout to wait for application to start.
        :param testpmd_args: Command line parameters for testpmd.

        :returns: None
        """
        self._logger = logging.getLogger(__name__)
        self._timeout = timeout
        self._expect = expected_cmd
        if not self._expect:
            self._expect = _TESTPMD_PROMPT
        testpmd_args = testpmd_args or []
        self._cmd = ['sudo', '-E', _TESTPMD_BIN] + testpmd_args

    # startup/shutdown

    def start(self):
        """ Start ``testpmd`` instance.

        :returns: None
        :raises: pexpect.EOF, pexpect.TIMEOUT
        """

        try:
            super(TestPMDProcess, self).start()
            self.relinquish()
        except (pexpect.EOF, pexpect.TIMEOUT) as exc:
            logging.error("TestPMD start failed.")
            raise exc

    def kill(self, signal='-15', sleep=2):
        """Kill ``testpmd`` instance if it is alive.

        :returns: None
        """
        self._logger.info('Killing testpmd...')

        super(TestPMDProcess, self).kill(signal, sleep)

    # helper functions

    def send(self, cmd, delay=0):
        """
        Send ``cmd`` with no wait.

        Useful for asynchronous commands.

        :param cmd: Command to send to guest.
        :param timeout: Delay to wait after sending command before returning.

        :returns: None
        """
        self._logger.debug(cmd)
        self._child.sendline(cmd)
        time.sleep(delay)

    def wait(self, msg=_TESTPMD_PROMPT, timeout=30):
        """
        Wait for ``msg``.

        :param msg: Message to wait for from guest.
        :param timeout: Time to wait for message.

        :returns: None
        """
        self._child.expect(msg, timeout=timeout)
