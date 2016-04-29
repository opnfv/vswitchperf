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
Interface for VNF.
"""

import time
from tools import tasks

class IVnf(tasks.Process):

    """
    Interface for VNF.
    """

    _number_vnfs = 0

    def __init__(self):
        """
        Initialization method.

        Purpose of this method is to initialize all
        common Vnf data, no services should be started by
        this call (use ``start`` method instead).
        """
        self._number = IVnf._number_vnfs
        IVnf._number_vnfs = IVnf._number_vnfs + 1
        self._log_prefix = 'vnf_%d_cmd : ' % self._number

    def start(self):
        """
        Starts VNF instance.

        This is a blocking function
        """
        super(IVnf, self).start()

    def stop(self):
        """
        Stops VNF instance.
        """
        if self.is_running():
            self._logger.info('Killing VNF...')

            # force termination of VNF and wait for it to terminate; It will avoid
            # sporadic reboot of host. (caused by hugepages or DPDK ports)
            super(IVnf, self).kill(signal='-9', sleep=10)

    def execute(self, cmd, delay=0):
        """
        execute ``cmd`` with given ``delay``.

        This method makes asynchronous call to guest system
        and waits given ``delay`` before returning. Can be
        used with ``wait`` method to create synchronous call.

        :param cmd: Command to execute on guest system.
        :param delay: Delay (in seconds) to wait after sending
                      command before returning. Please note that
                      this value can be floating point which
                      allows to pass milliseconds.

        :returns: None.
        """
        self._logger.debug('%s%s', self._log_prefix, cmd)
        self._child.sendline(cmd)
        time.sleep(delay)

    def wait(self, prompt='', timeout=30):
        """
        wait for ``prompt`` on guest system for given ``timeout``.

        This method ends based on two conditions:
        * ``prompt`` has been detected
        * ``timeout`` has been reached.

        :param prompt: method end condition. If ``prompt``
                             won't be detected during given timeout,
                             method will return False.
        :param timeout: Time to wait for prompt (in seconds).
                        Please note that this value can be floating
                        point which allows to pass milliseconds.

        :returns: True if result_cmd has been detected before
                  timeout has been reached, False otherwise.
        """
        self._child.expect(prompt, timeout=timeout)

    def execute_and_wait(self, cmd, timeout=30, prompt=''):
        """
        execute ``cmd`` with given ``timeout``.

        This method makes synchronous call to guest system
        and waits till ``cmd`` execution is finished
        (based on ``prompt value) or ''timeout'' has
        been reached.

        :param cmd: Command to execute on guest system.
        :param timeout: Timeout till the end of execution is not
                        detected.
        :param prompt: method end condition. If ``prompt``
                             won't be detected during given timeout,
                             method will return False. If no argument
                             or None value will be passed, default
                             ``prompt`` passed in __init__
                             method will be used.

        :returns: True if end of execution has been detected
                  before timeout has been reached, False otherwise.
        """
        self.execute(cmd)
        self.wait(prompt=prompt, timeout=timeout)

    def validate_start(self, dummy_result):
        """ Validate call of VNF start()
        """
        if self._child and self._child.isalive():
            return True
        else:
            return False

    def validate_stop(self, result):
        """ Validate call of fVNF stop()
        """
        return not self.validate_start(result)

    @staticmethod
    def reset_vnf_counter():
        """
        Reset internal VNF counters

        This method is static
        """
        IVnf._number_vnfs = 0

