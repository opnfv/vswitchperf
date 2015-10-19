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
""" VNF Controller interface
"""

import logging
from vnfs.vnf.vnf import IVnf

class VnfController(object):
    """VNF controller class

    Used to set-up and control VNFs for specified scenario

    Attributes:
        _vnf_class: A class object representing the VNF to be used.
        _deployment_scenario: A string describing the scenario to set-up in the
            constructor.
        _vnfs: A list of vnfs controlled by the controller.
    """

    def __init__(self, deployment_scenario, vnf_class):
        """Sets up the VNF infrastructure for the PVP deployment scenario.

        :param vnf_class: The VNF class to be used.
        """
        # reset VNF ID counter for each testcase
        IVnf.reset_vnf_counter()

        # setup controller with requested number of VNFs
        self._logger = logging.getLogger(__name__)
        self._vnf_class = vnf_class
        self._deployment_scenario = deployment_scenario.upper()
        if self._deployment_scenario == 'P2P':
            self._vnfs = []
        elif self._deployment_scenario == 'PVP':
            self._vnfs = [vnf_class()]
        elif self._deployment_scenario == 'PVVP':
            self._vnfs = [vnf_class(), vnf_class()]
        elif self._deployment_scenario == 'OP2P':
            self._vnfs = []
        self._logger.debug('__init__ ' + str(len(self._vnfs)) +
                           ' VNF[s] with ' + ' '.join(map(str, self._vnfs)))

    def get_vnfs(self):
        """Returns a list of vnfs controlled by this controller.
        """
        self._logger.debug('get_vnfs ' + str(len(self._vnfs)) +
                           ' VNF[s] with ' + ' '.join(map(str, self._vnfs)))
        return self._vnfs

    def start(self):
        """Boots all VNFs set-up by __init__.

        This is a blocking function.
        """
        self._logger.debug('start ' + str(len(self._vnfs)) +
                           ' VNF[s] with ' + ' '.join(map(str, self._vnfs)))
        for vnf in self._vnfs:
            vnf.start()

    def stop(self):
        """Stops all VNFs set-up by __init__.

        This is a blocking function.
        """
        self._logger.debug('stop ' + str(len(self._vnfs)) +
                           ' VNF[s] with ' + ' '.join(map(str, self._vnfs)))
        for vnf in self._vnfs:
            vnf.stop()

    def __enter__(self):
        self.start()

    def __exit__(self, type_, value, traceback):
        self.stop()
