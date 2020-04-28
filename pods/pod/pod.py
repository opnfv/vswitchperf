# Copyright 2020 Spirent Communications, University Of Delhi.
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
Interface for POD
"""

#import time
#import pexpect
from tools import tasks

class IPod(tasks.Process):
    """
    Interface for POD

    Inheriting from Process helps in managing system process.
    execute a command, wait, kill, etc.
    """
    _number_pods = 0

    def __init__(self):
        """
        Initialization Method
        """
        self._number = IPod._number_pods
        self._logger.debug('Initializing %s. Pod with index %s',
                           self._number + 1, self._number)
        IPod._number_pods = IPod._number_pods + 1
        self._log_prefix = 'pod_%d_cmd : ' % self._number
        # raise NotImplementedError()

    def create(self):
        """
        Start the Pod
        """
        raise NotImplementedError()


    def terminate(self):
        """
        Stop the Pod
        """
        raise NotImplementedError()

    @staticmethod
    def reset_pod_counter():
        """
        Reset internal POD counter

        This method is static
        """
        IPod._number_pods = 0
