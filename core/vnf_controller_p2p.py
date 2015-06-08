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
"""VNF Controller for the P2P scenario
"""

import logging

from core.vnf_controller import IVnfController

class VnfControllerP2P(IVnfController):
    """VNF controller for the P2P scenario.

    Does nothing as there is no VNF in P2P

    Attributes:
        _vnf_class: A class object representing the VNF to be used.
        _deployment_scenario: A string describing the scenario to set-up in the
            constructor.
        _vnfs: A list of vnfs controlled by the controller.
    """

    #TODO: Decide on contextmanager or __enter/exit__ strategy <MH 2015-05-01>
    def __init__(self, vnf_class):
        """Sets up the VNF infrastructure for the P2P deployment scenario.

        :param vnf_class: The VNF class to be used, this is mostly ignored.
        """
        self._logger = logging.getLogger(__name__)
        self._vnf_class = vnf_class
        self._deployment_scenario = "P2P"
        self._logger.debug('__init__ with ' + str(self._vnf_class))

    def get_vnfs(self):
        """Returns an empty list of vnfs.
        """
        self._logger.debug('get_vnfs with ' + str(self._vnf_class))
        return []

    def start(self):
        """Starts nothing.
        """
        self._logger.debug('start with ' + str(self._vnf_class))

    def stop(self):
        """Stops nothing.
        """
        self._logger.debug('stop with ' + str(self._vnf_class))
