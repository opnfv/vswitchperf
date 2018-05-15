# Copyright 2015-2018 Intel Corporation., Tieto
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

"""VSwitch controller for Physical to Physical deployment
"""
from core.vswitch_controller import IVswitchController
from conf import settings

class VswitchControllerP2P(IVswitchController):
    """VSwitch controller for P2P deployment scenario.

    Attributes:
        _vswitch_class: The vSwitch class to be used.
        _vswitch: The vSwitch object controlled by this controller
        _deployment_scenario: A string describing the scenario to set-up in the
            constructor.
    """
    def __init__(self, deployment, vswitch_class, traffic):
        """See IVswitchController for general description
        """
        super().__init__(deployment, vswitch_class, traffic)
        self._bridge = settings.getValue('VSWITCH_BRIDGE_NAME')

    def setup(self):
        """Sets up the switch for p2p.
        """
        self._logger.debug('Setup using %s', str(self._vswitch_class))

        try:
            self._vswitch.start()

            self._vswitch.add_switch(self._bridge)

            (port1, _) = self._vswitch.add_phy_port(self._bridge)
            (port2, _) = self._vswitch.add_phy_port(self._bridge)

            self._vswitch.add_connection(self._bridge, port1, port2, self._traffic)
            self._vswitch.add_connection(self._bridge, port2, port1, self._traffic)

        except:
            self._vswitch.stop()
            raise

    def stop(self):
        """Tears down the switch created in setup().
        """
        self._logger.debug('Stop using %s', str(self._vswitch_class))
        self._vswitch.stop()

    def get_ports_info(self):
        """See IVswitchController for description
        """
        self._logger.debug('get_ports_info  using %s', str(self._vswitch_class))
        return self._vswitch.get_ports(self._bridge)

    def dump_vswitch_connections(self):
        """See IVswitchController for description
        """
        self._vswitch.dump_connections(self._bridge)
