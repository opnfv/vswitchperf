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


class IVnf(object):

    """
    Interface for VNF.
    """

    def __init__(self, memory, cpus,
                 monitor_path, shared_path_host,
                 shared_path_guest, guest_prompt):
        """
        Initialization method.

        Purpose of this method is to initialize all
        common Vnf data, no services should be started by
        this call (use ``start`` method instead).

        :param memory:   Virtual RAM size in megabytes.
        :param cpus:     Number of Processors.
        :param monitor_path: Configure monitor to given path.
        :param shared_path_host: HOST path to shared location.
        :param shared_path_guest: GUEST path to shared location.
        :param guest_prompt: preconfigured command prompt which is used
                           in execute_and_wait & wait methods
                           to detect if particular call is finished.
        """
        raise NotImplementedError()

    def start(self):
        """
        Starts VNF instance.
        """
        raise NotImplementedError()

    def stop(self):
        """
        Stops VNF instance.
        """
        raise NotImplementedError()

    def execute(self, command, delay=30):
        """
        execute ``command`` with given ``delay``.

        This method makes asynchronous call to guest system
        and waits given ``delay`` before returning. Can be
        used with ``wait`` method to create synchronous call.

        :param command: Command to execute on guest system.
        :param delay: Delay (in seconds) to wait after sending
                      command before returning. Please note that
                      this value can be floating point which
                      allows to pass milliseconds.

        :returns: None.
        """
        raise NotImplementedError()

    def wait(self, guest_prompt, timeout=30):
        """
        wait for ``guest_prompt`` on guest system for given ``timeout``.

        This method ends based on two conditions:
        * ``guest_prompt`` has been detected
        * ``timeout`` has been reached.

        :param guest_prompt: method end condition. If ``guest_prompt``
                             won't be detected during given timeout,
                             method will return False.
        :param timeout: Time to wait for prompt (in seconds).
                        Please note that this value can be floating
                        point which allows to pass milliseconds.

        :returns: True if result_cmd has been detected before
                  timeout has been reached, False otherwise.
        """
        raise NotImplementedError()

    def execute_and_wait(self, command, timeout=30, guest_prompt=None):
        """
        execute ``command`` with given ``timeout``.

        This method makes synchronous call to guest system
        and waits till ``command`` execution is finished
        (based on ``guest_prompt value) or ''timeout'' has
        been reached.

        :param command: Command to execute on guest system.
        :param timeout: Timeout till the end of execution is not
                        detected.
        :param guest_prompt: method end condition. If ``guest_prompt``
                             won't be detected during given timeout,
                             method will return False. If no argument
                             or None value will be passed, default
                             ``guest_prompt`` passed in __init__
                             method will be used.

        :returns: True if end of execution has been detected
                  before timeout has been reached, False otherwise.
        """
        raise NotImplementedError()
