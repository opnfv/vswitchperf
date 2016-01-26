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

"""VSwitch controller for Physical to Tunnel Endpoint to Physical deployment
"""

import logging

from core.vswitch_controller import IVswitchController
from vswitches.utils import add_ports_to_flow
from conf import settings
from tools import tasks

_FLOW_TEMPLATE = {
    'idle_timeout': '0'
}

class VswitchControllerOP2P(IVswitchController):
    """VSwitch controller for OP2P deployment scenario.

    Attributes:
        _vswitch_class: The vSwitch class to be used.
        _vswitch: The vSwitch object controlled by this controller
        _deployment_scenario: A string describing the scenario to set-up in the
            constructor.
    """
    def __init__(self, vswitch_class, traffic, tunnel_operation=None):
        """Initializes up the prerequisites for the OP2P deployment scenario.

        :vswitch_class: the vSwitch class to be used.
        """
        self._logger = logging.getLogger(__name__)
        self._vswitch_class = vswitch_class
        self._vswitch = vswitch_class()
        self._deployment_scenario = "OP2P"
        self._traffic = traffic.copy()
        self._tunnel_operation = tunnel_operation
        self._logger.debug('Creation using ' + str(self._vswitch_class))

    def setup(self):
        """ Sets up the switch for overlay P2P (tunnel encap or decap)
        """
        self._logger.debug('Setting up ' + str(self._tunnel_operation))
        if self._tunnel_operation == "encapsulation":
            self._setup_encap()
        else:
            self._setup_decap()

    def _setup_encap(self):
        """ Sets up the switch for overlay P2P encapsulation test

        Create 2 bridges br0 (integration bridge) and br-ext and a VXLAN port
        for encapsulation.
        """
        self._logger.debug('Setup using ' + str(self._vswitch_class))

        try:
            self._vswitch.start()
            bridge = settings.getValue('TUNNEL_INTEGRATION_BRIDGE')
            bridge_ext = settings.getValue('TUNNEL_EXTERNAL_BRIDGE')
            bridge_ext_ip = settings.getValue('TUNNEL_EXTERNAL_BRIDGE_IP')
            tg_port2_mac = settings.getValue('TRAFFICGEN_PORT2_MAC')
            vtep_ip2 = settings.getValue('VTEP_IP2')
            self._vswitch.add_switch(bridge)

            tasks.run_task(['sudo', 'ifconfig', bridge,
                            settings.getValue('VTEP_IP1')],
                           self._logger, 'Assign ' +
                           settings.getValue('VTEP_IP1') + ' to ' + bridge,
                           False)

            tunnel_type = self._traffic['tunnel_type']

            self._vswitch.add_switch(bridge_ext)
            (_, phy1_number) = self._vswitch.add_phy_port(bridge)
            (_, phy2_number) = self._vswitch.add_tunnel_port(bridge,
                                                             vtep_ip2,
                                                             tunnel_type)
            self._vswitch.add_phy_port(bridge_ext)

            tasks.run_task(['sudo', 'ip', 'addr', 'add',
                            bridge_ext_ip,
                            'dev', bridge_ext], self._logger, 'Assign ' +
                           bridge_ext_ip + ' to ' + bridge_ext)

            tasks.run_task(['sudo', 'ip', 'link', 'set', 'dev', bridge_ext,
                            'up'], self._logger,
                           'Set ' + bridge_ext + 'status to up')

            self._vswitch.add_route(bridge,
                                    settings.getValue('VTEP_IP2_SUBNET'),
                                    bridge_ext)

            if settings.getValue('VSWITCH').endswith('Vanilla'):
                tasks.run_task(['sudo', 'arp', '-s', vtep_ip2, tg_port2_mac],
                               self._logger,
                               'Set ' + bridge_ext + ' status to up')
            else:
                self._vswitch.set_tunnel_arp(vtep_ip2,
                                             tg_port2_mac,
                                             bridge_ext)

            # Test is unidirectional for now
            self._vswitch.del_flow(bridge)
            flow1 = add_ports_to_flow(_FLOW_TEMPLATE, phy1_number,
                                      phy2_number)
            self._vswitch.add_flow(bridge, flow1)

        except:
            self._vswitch.stop()
            raise

    def _setup_decap(self):
        """ Sets up the switch for overlay P2P decapsulation test
        """
        self._logger.debug('Setup using ' + str(self._vswitch_class))

        try:
            self._vswitch.start()
            bridge = settings.getValue('TUNNEL_INTEGRATION_BRIDGE')
            bridge_ext = settings.getValue('TUNNEL_EXTERNAL_BRIDGE')
            bridge_ext_ip = settings.getValue('TUNNEL_EXTERNAL_BRIDGE_IP')
            tgen_ip1 = settings.getValue('TRAFFICGEN_PORT1_IP')
            self._vswitch.add_switch(bridge)

            tasks.run_task(['sudo', 'ifconfig', bridge,
                            settings.getValue('VTEP_IP1')],
                           self._logger, 'Assign ' +
                           settings.getValue('VTEP_IP1') + ' to ' + bridge, False)

            tunnel_type = self._traffic['tunnel_type']

            self._vswitch.add_switch(bridge_ext)
            self._vswitch.add_phy_port(bridge)
            (_, phy2_number) = self._vswitch.add_phy_port(bridge_ext)
            vxlan_vni = 'options:key=' + settings.getValue('VXLAN_VNI')
            (_, phy3_number) = self._vswitch.add_tunnel_port(bridge_ext,
                                                             tgen_ip1,
                                                             tunnel_type,
                                                             params=[vxlan_vni])

            tasks.run_task(['sudo', 'ip', 'addr', 'add',
                            bridge_ext_ip,
                            'dev', bridge_ext],
                           self._logger, 'Assign ' +
                           bridge_ext_ip
                           + ' to ' + bridge_ext)

            tasks.run_task(['sudo', 'ip', 'link', 'set', 'dev', bridge_ext,
                            'up'],
                           self._logger,
                           'Set ' + bridge_ext + ' status to up')

            self._vswitch.set_tunnel_arp(tgen_ip1,
                                         settings.getValue('TRAFFICGEN_PORT1_MAC'),
                                         bridge)
            self._vswitch.set_tunnel_arp(bridge_ext_ip.split('/')[0],
                                         settings.getValue('DUT_NIC1_MAC'),
                                         bridge_ext)

            # Test is unidirectional for now
            self._vswitch.del_flow(bridge_ext)
            flow1 = add_ports_to_flow(_FLOW_TEMPLATE, phy3_number,
                                      phy2_number)
            self._vswitch.add_flow(bridge_ext, flow1)

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

    def dump_vswitch_flows(self):
        """See IVswitchController for description
        """
        self._vswitch.dump_flows(settings.getValue('VSWITCH_BRIDGE_NAME'))
