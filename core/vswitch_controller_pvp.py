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

"""VSwitch controller for Physical to VM to Physical deployment
"""

import logging

from core.vswitch_controller import IVswitchController

class VswitchControllerPVP(IVswitchController):
    """VSwitch controller for PVP deployment scenario.

    Attributes:
        _vswitch_class: The vSwitch class to be used.
        _vswitch: The vSwitch object controlled by this controller
        _deployment_scenario: A string describing the scenario to set-up in the
            constructor.
    """
    def __init__(self, vswitch_class):
        """Initializes up the prerequisites for the PVP deployment scenario.

        :vswitch_class: the vSwitch class to be used.
        """
        self._logger = logging.getLogger(__name__)
        self._vswitch_class = vswitch_class
        self._vswitch = vswitch_class()
        self._deployment_scenario = "PVP"
        self._logger.debug('Creation using ' + str(self._vswitch_class))

    def setup(self):
        """
        Sets up the switch for the particular deployment scenario passed in to
        the constructor.
        """
        # TODO call IVSwitch methods to configure VSwitch for PVP scenario.
        self._logger.debug('Setup using ' + str(self._vswitch_class))

    def stop(self):
        """
        Tears down the switch created in setup().
        """
        # TODO call IVSwitch methods to stop VSwitch for PVP scenario.
        self._logger.debug('Stop using ' + str(self._vswitch_class))

    def get_vswitch(self):
        """See IVswitchController for description
        """
        return self._vswitch

    def get_ports_info(self):
        """See IVswitchController for description
        """
        self._logger.debug('get_ports_info  using ' + str(self._vswitch_class))
        return []



