# Copyright 2020 Spirent Communications
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
""" pod Controller interface
"""

import logging
import pexpect
from conf import settings
from pods.pod.pod import IPod

class PodController(object):
    """POD controller class

    Used to set-up and control PODs for specified scenario

    Attributes:
        _pod_class: A class object representing the POD.
        _deployment: A string describing the scenario to set-up in the
            constructor.
        _pods: A list of pods controlled by the controller.
    """

    def __init__(self, deployment, pod_class):
        """Sets up the POD infrastructure based on deployment scenario

        :param pod_class: The POD class to be used.
        """
        # reset POD ID counter for each testcase
        IPod.reset_pod_counter()

        # setup controller with requested number of pods
        self._logger = logging.getLogger(__name__)
        self._pod_class = pod_class
        self._deployment = deployment.lower()
        self._pods = []
        if self._deployment == 'pvp':
            pod_number = 1

        if pod_number:
            self._pods = [pod_class() for _ in range(vm_number)]

            self._logger.debug('__init__ ' + str(len(self._pods)) +
                               ' POD[s] with ' + ' '.join(map(str, self._pods)))

    def get_pods(self):
        """Returns a list of pods controlled by this controller.
        """
        self._logger.debug('get_pods ' + str(len(self._pods)) +
                           ' pod[s] with ' + ' '.join(map(str, self._pods)))
        return self._pods

    def get_pods_number(self):
        """Returns a number of pods controlled by this controller.
        """
        self._logger.debug('get_pods_number %s pod[s]', str(len(self._pods)))
        return len(self._pods)

    def start(self):
        """Boots all pods set-up by __init__.

        This is a blocking function.
        """
        self._logger.debug('start ' + str(len(self._pods)) +
                           ' pod[s] with ' + ' '.join(map(str, self._pods)))
        try:
            for pod in self._pods:
                pod.create()
        except pexpect.TIMEOUT:
            self.stop()
            raise

    def stop(self):
        """Stops all pods set-up by __init__.

        This is a blocking function.
        """
        self._logger.debug('stop ' + str(len(self._pods)) +
                           ' pod[s] with ' + ' '.join(map(str, self._pods)))
        for pod in self._pods:
            pod.terminate()

    def __enter__(self):
        self.start()

    def __exit__(self, type_, value, traceback):
        self.stop()
