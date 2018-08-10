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

"""VSwitch controller for Physical to Tunnel Endpoint to Physical deployment
"""
from core.vswitch_controller import IVswitchController
from vswitches.utils import add_ports_to_flow
from conf import settings as S
from tools import tasks

class VswitchControllerOP2P(IVswitchController):
    """VSwitch controller for OP2P deployment scenario.
    """
    def __init__(self, deployment, vswitch_class, traffic, tunnel_operation=None):
        """See IVswitchController for general description
        """
        super().__init__(deployment, vswitch_class, traffic)
        self._tunnel_operation = tunnel_operation

    def setup(self):
        """ Sets up the switch for overlay P2P (tunnel encap or decap)
        """
        self._logger.debug('Setting up %s', str(self._tunnel_operation))
        if self._tunnel_operation == "encapsulation":
            self._setup_encap()
        else:
            if str(S.getValue('VSWITCH')).endswith('Vanilla'):
                self._setup_decap_vanilla()
            else:
                self._setup_decap()

    def _setup_encap(self):
        """ Sets up the switch for overlay P2P encapsulation test

        Create 2 bridges br0 (integration bridge) and br-ext and a VXLAN port
        for encapsulation.
        """
        self._logger.debug('Setup using %s', str(self._vswitch_class))

        try:
            self._vswitch.start()
            bridge = S.getValue('TUNNEL_INTEGRATION_BRIDGE')
            bridge_ext = S.getValue('TUNNEL_EXTERNAL_BRIDGE')
            bridge_ext_ip = S.getValue('TUNNEL_EXTERNAL_BRIDGE_IP')
            tg_port2_mac = S.getValue('TRAFFICGEN_PORT2_MAC')
            vtep_ip2 = S.getValue('VTEP_IP2')
            self._vswitch.add_switch(bridge)

            tasks.run_task(['sudo', 'ip', 'addr', 'add',
                            S.getValue('VTEP_IP1'), 'dev', bridge],
                           self._logger, 'Assign ' +
                           S.getValue('VTEP_IP1') + ' to ' + bridge,
                           False)
            tasks.run_task(['sudo', 'ip', 'link', 'set', 'dev', bridge, 'up'],
                           self._logger, 'Bring up ' + bridge, False)

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
                                    S.getValue('VTEP_IP2_SUBNET'),
                                    bridge_ext)

            if str(S.getValue('VSWITCH')).endswith('Vanilla'):
                tasks.run_task(['sudo', 'arp', '-s', vtep_ip2, tg_port2_mac],
                               self._logger,
                               'Set ' + bridge_ext + ' status to up')
            else:
                self._vswitch.set_tunnel_arp(vtep_ip2,
                                             tg_port2_mac,
                                             bridge_ext)

            # Test is unidirectional for now
            self._vswitch.del_flow(bridge)
            flow1 = add_ports_to_flow(S.getValue('OVS_FLOW_TEMPLATE'), phy1_number,
                                      phy2_number)
            self._vswitch.add_flow(bridge, flow1)
            # enable MAC learning mode at external bridge
            flow_ext = S.getValue('OVS_FLOW_TEMPLATE').copy()
            flow_ext.update({'actions': ['NORMAL']})
            self._vswitch.add_flow(bridge_ext, flow_ext)
        except:
            self._vswitch.stop()
            raise

    def _setup_decap(self):
        """ Sets up the switch for overlay P2P decapsulation test
        """
        self._logger.debug('Setup using %s', str(self._vswitch_class))

        try:
            self._vswitch.start()
            bridge = S.getValue('TUNNEL_INTEGRATION_BRIDGE')
            bridge_ext = S.getValue('TUNNEL_EXTERNAL_BRIDGE')
            bridge_ext_ip = S.getValue('TUNNEL_MODIFY_BRIDGE_IP1')
            tgen_ip1 = S.getValue('TRAFFICGEN_PORT1_IP')
            tgen_ip2 = S.getValue('TRAFFICGEN_PORT2_IP')
            self._vswitch.add_switch(bridge, params=["other_config:hwaddr=00:00:64:00:00:02"])

            tasks.run_task(['sudo', 'ip', 'addr', 'add',
                            '10.0.0.1', 'dev', bridge],
                           self._logger, 'Assign ' +
                           '10.0.0.1' + ' to ' + bridge, False)
            tasks.run_task(['sudo', 'ip', 'link', 'set', 'dev', bridge, 'up'],
                           self._logger, 'Bring up ' + bridge, False)

            tunnel_type = self._traffic['tunnel_type']

            (_, phy1_number) = self._vswitch.add_phy_port(bridge)
            self._vswitch.add_switch(bridge_ext, params=["other_config:hwaddr=00:00:64:00:00:01"])
            if tunnel_type == "vxlan":
                vxlan_vni = 'options:key=' + S.getValue('VXLAN_VNI')
                (_, phy2_number) = self._vswitch.add_tunnel_port(bridge,
                                                                 tgen_ip1,
                                                                 tunnel_type,
                                                                 params=[vxlan_vni])
            else:
                (_, phy2_number) = self._vswitch.add_tunnel_port(bridge,
                                                                 tgen_ip1,
                                                                 tunnel_type)
            (_, phy3_number) = self._vswitch.add_phy_port(bridge_ext)
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
                                         S.getValue('VXLAN_FRAME_L2')
                                         ["dstmac"],
                                         bridge_ext)

            self._vswitch.set_tunnel_arp(tgen_ip2,
                                         S.getValue('VXLAN_FRAME_L2')
                                         ["srcmac"],
                                         bridge)
            # Test is unidirectional for now
            self._vswitch.del_flow(bridge_ext)
            flow1 = add_ports_to_flow(S.getValue('OVS_FLOW_TEMPLATE'), phy3_number,
                                      'LOCAL')
            self._vswitch.add_flow(bridge_ext, flow1)
            flow2 = add_ports_to_flow(S.getValue('OVS_FLOW_TEMPLATE'), phy2_number,
                                      phy1_number)
            self._vswitch.add_flow(bridge, flow2)


        except:
            self._vswitch.stop()
            raise

    def _setup_decap_vanilla(self):
        """ Sets up the switch for overlay P2P decapsulation test
        """
        self._logger.debug('Setup decap vanilla %s', str(self._vswitch_class))

        try:
            self._vswitch.start()
            bridge = S.getValue('TUNNEL_INTEGRATION_BRIDGE')
            bridge_ext = S.getValue('TUNNEL_EXTERNAL_BRIDGE')
            bridge_ext_ip = S.getValue('TUNNEL_EXTERNAL_BRIDGE_IP')
            tgen_ip1 = S.getValue('TRAFFICGEN_PORT1_IP')
            self._vswitch.add_switch(bridge)

            tasks.run_task(['sudo', 'ip', 'addr', 'add',
                            S.getValue('TUNNEL_INT_BRIDGE_IP'), 'dev', bridge],
                           self._logger, 'Assign ' +
                           S.getValue('TUNNEL_INT_BRIDGE_IP') + ' to ' + bridge, False)
            tasks.run_task(['sudo', 'ip', 'link', 'set', 'dev', bridge, 'up'],
                           self._logger, 'Bring up ' + bridge, False)

            tunnel_type = self._traffic['tunnel_type']

            self._vswitch.add_switch(bridge_ext)
            self._vswitch.add_phy_port(bridge_ext)
            (_, phy2_number) = self._vswitch.add_phy_port(bridge)

            if tunnel_type == "vxlan":
                vxlan_vni = 'options:key=' + S.getValue('VXLAN_VNI')
                self._vswitch.add_tunnel_port(bridge, tgen_ip1, tunnel_type,
                                              params=[vxlan_vni])
            else:
                self._vswitch.add_tunnel_port(bridge, tgen_ip1, tunnel_type)

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

            tg_port2_mac = S.getValue('TRAFFICGEN_PORT2_MAC')
            vtep_ip2 = S.getValue('TRAFFICGEN_PORT2_IP')

            self._vswitch.set_tunnel_arp(vtep_ip2,
                                         tg_port2_mac,
                                         bridge_ext)

            self._vswitch.add_route(bridge,
                                    S.getValue('VTEP_IP2_SUBNET'),
                                    bridge)


            tasks.run_task(['sudo', 'arp', '-s', vtep_ip2, tg_port2_mac],
                           self._logger,
                           'Set ' + bridge_ext + ' status to up')


            # Test is unidirectional for now
            self._vswitch.del_flow(bridge_ext)

            flow1 = add_ports_to_flow(S.getValue('OVS_FLOW_TEMPLATE'), phy2_number, 'LOCAL')
            self._vswitch.add_flow(bridge_ext, flow1)

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
        self._logger.debug('get_ports_info for bridges: %s, %s',
                           S.getValue('TUNNEL_INTEGRATION_BRIDGE'),
                           S.getValue('TUNNEL_EXTERNAL_BRIDGE'))
        return self._vswitch.get_ports(
            S.getValue('TUNNEL_INTEGRATION_BRIDGE')) +\
                self._vswitch.get_ports(
                    S.getValue('TUNNEL_EXTERNAL_BRIDGE'))

    def dump_vswitch_connections(self):
        """See IVswitchController for description
        """
        self._vswitch.dump_connections(S.getValue('TUNNEL_INTEGRATION_BRIDGE'))
        self._vswitch.dump_connections(S.getValue('TUNNEL_EXTERNAL_BRIDGE'))
