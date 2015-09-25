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
from vswitches.utils import add_ports_to_flow
from conf import settings

_FLOW_TEMPLATE = {
    'idle_timeout': '0'
}

class VswitchControllerPVVP(IVswitchController):
    """VSwitch controller for PVVP deployment scenario.

    Attributes:
        _vswitch_class: The vSwitch class to be used.
        _vswitch: The vSwitch object controlled by this controller
        _deployment_scenario: A string describing the scenario to set-up in the
            constructor.
    """
    def __init__(self, vswitch_class, bidir=False):
        """Initializes up the prerequisites for the PVVP deployment scenario.

        :vswitch_class: the vSwitch class to be used.
        """
        self._logger = logging.getLogger(__name__)
        self._vswitch_class = vswitch_class
        self._vswitch = vswitch_class()
        self._deployment_scenario = "PVVP"
        self._bidir = bidir
        self._logger.debug('Creation using ' + str(self._vswitch_class))

    def setup(self):
        """ Sets up the switch for PVVP
        """
        self._logger.debug('Setup using ' + str(self._vswitch_class))

        try:
            self._vswitch.start()

            bridge = settings.getValue('VSWITCH_BRIDGE_NAME')
            self._vswitch.add_switch(bridge)

            (_, phy1_number) = self._vswitch.add_phy_port(bridge)
            (_, phy2_number) = self._vswitch.add_phy_port(bridge)
            (_, vport1_number) = self._vswitch.add_vport(bridge)
            (_, vport2_number) = self._vswitch.add_vport(bridge)
            (_, vport3_number) = self._vswitch.add_vport(bridge)
            (_, vport4_number) = self._vswitch.add_vport(bridge)

            self._vswitch.del_flow(bridge)
            flow1 = add_ports_to_flow(_FLOW_TEMPLATE, phy1_number,
                                      vport1_number)
            flow2 = add_ports_to_flow(_FLOW_TEMPLATE, vport2_number,
                                      vport3_number)
            flow3 = add_ports_to_flow(_FLOW_TEMPLATE, vport4_number,
                                      phy2_number)
            self._vswitch.add_flow(bridge, flow1)
            self._vswitch.add_flow(bridge, flow2)
            self._vswitch.add_flow(bridge, flow3)

            if self._bidir:
                flow4 = add_ports_to_flow(_FLOW_TEMPLATE, phy2_number,
                                          vport4_number)
                flow5 = add_ports_to_flow(_FLOW_TEMPLATE, vport3_number,
                                          vport2_number)
                flow6 = add_ports_to_flow(_FLOW_TEMPLATE, vport1_number,
                                          phy1_number)
                self._vswitch.add_flow(bridge, flow4)
                self._vswitch.add_flow(bridge, flow5)
                self._vswitch.add_flow(bridge, flow6)

        except:
            self._vswitch.stop()
            raise

    def stop(self):
        """Tears down the switch created in setup().
        """
        self._logger.debug('Stop using ' + str(self._vswitch_class))
        self._vswitch.stop()

    def __enter__(self):
        self.setup()

    def __exit__(self, type_, value, traceback):
        self.stop()

    def get_vswitch(self):
        """See IVswitchController for description
        """
        return self._vswitch

    def get_ports_info(self):
        """See IVswitchController for description
        """
        self._logger.debug('get_ports_info  using ' + str(self._vswitch_class))
        return self._vswitch.get_ports(settings.getValue('VSWITCH_BRIDGE_NAME'))
