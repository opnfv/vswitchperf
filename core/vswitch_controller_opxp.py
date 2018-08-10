
# Copyright 2017 Intel Corporation.
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
import logging
import netaddr
from netaddr import EUI, IPNetwork, mac_unix
from core.vswitch_controller import IVswitchController
from vswitches.utils import add_ports_to_flow
from conf import settings as S
from tools import tasks

_FLOW_TEMPLATE = {
    'idle_timeout': '0'
}


class VswitchControllerOPXP(IVswitchController):
    """VSwitch controller for OPXP deployment scenario.

    Attributes:
        _vswitch_class: The vSwitch class to be used.
        _vswitch: The vSwitch object controlled by this controller
        _deployment_scenario: A string describing the scenario to set-up in the
            constructor.
    """
    def __init__(self, deployment, vswitch_class, traffic,
                 tunnel_operation=None):
        """Initializes up the prerequisites for the OPXP deployment scenario.

        :vswitch_class: the vSwitch class to be used.
        """
        self._logger = logging.getLogger(__name__)
        self._vswitch_class = vswitch_class
        self._vswitch = vswitch_class()
        self._deployment_scenario = deployment

        if deployment == 'opvp':
            self._pxp_vm_count = 1
        elif deployment.startswith('opvp'):
            if len(deployment) > 4:
                self._pxp_vm_count = int(deployment[4:])
        else:
            raise RuntimeError(
                'Unknown number of VMs involved in {} deployment.'
                .format(deployment))

        self._traffic = traffic.copy()
        self._tunnel_operation = tunnel_operation
        self._logger.debug('Creation using %s', str(self._vswitch_class))

    def setup(self):
        """ Sets up the switch for overlay PVP (tunnel encap or decap)
        """
        self._logger.debug('Setting up %s', str(self._tunnel_operation))

        if self._tunnel_operation == "encapsulation":
            self._setup_encap()
        elif self._tunnel_operation == "decapsulation":
            self._setup_decap()
        else:
            self._setup_decap_encap()

    def _setup_encap(self):
        """ Sets up the switch for overlay PXP encapsulation test

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
            (_, phy3_number) = self._vswitch.add_phy_port(bridge)
            (_, vport) = self._vswitch.add_vport(bridge_ext)
            (_, vport1) = self._vswitch.add_vport(bridge)

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
            self._vswitch.del_flow(bridge_ext)
            flow1 = add_ports_to_flow(_FLOW_TEMPLATE, phy1_number, phy2_number)
            flow2 = add_ports_to_flow(_FLOW_TEMPLATE, vport1, phy3_number)
            flow3 = add_ports_to_flow(_FLOW_TEMPLATE, 'LOCAL', vport)
            flow4 = add_ports_to_flow(_FLOW_TEMPLATE, vport, vport1)
            self._vswitch.add_flow(bridge, flow1)
            self._vswitch.add_flow(bridge, flow2)
            self._vswitch.add_flow(bridge_ext, flow3)
            self._vswitch.add_flow(bridge_ext, flow4)

        except:
            self._vswitch.stop()
            raise

    def _setup_decap(self):
        """ Sets up the switch for overlay PXP decapsulation test
        """
        self._logger.debug('Setup using %s', str(self._vswitch_class))

        try:
            self._vswitch.start()
            bridge = S.getValue('TUNNEL_INTEGRATION_BRIDGE')
            bridge_ext = S.getValue('TUNNEL_EXTERNAL_BRIDGE')
            bridge_ext_ip = S.getValue('TUNNEL_EXTERNAL_BRIDGE_IP')
            tgen_ip1 = S.getValue('TRAFFICGEN_PORT1_IP')
            tgen_ip2 = S.getValue('TRAFFICGEN_PORT2_IP')
            self._vswitch.add_switch(bridge,
                                     params=[
                                      "other_config:hwaddr=00:00:64:00:00:02"])

            tasks.run_task(['sudo', 'ip', 'addr', 'add',
                            S.getValue('VTEP_IP1'), 'dev', bridge],
                           self._logger, 'Assign ' +
                           S.getValue('VTEP_IP1') + ' to ' + bridge, False)
            tasks.run_task(['sudo', 'ip', 'link', 'set', 'dev', bridge, 'up'],
                           self._logger, 'Bring up ' + bridge, False)

            tunnel_type = self._traffic['tunnel_type']

            (_, phy1_number) = self._vswitch.add_phy_port(bridge)
            self._vswitch.add_switch(bridge_ext,
                                     params=[
                                      "other_config:hwaddr=00:00:64:00:00:01"])
            if tunnel_type == "vxlan":
                vxlan_vni = 'options:key=' + S.getValue('VXLAN_VNI')
                (_, phy2_number) = self._vswitch.add_tunnel_port(bridge,
                                                                 tgen_ip1,
                                                                 tunnel_type,
                                                                 params=[
                                                                    vxlan_vni])
            else:
                (_, phy2_number) = self._vswitch.add_tunnel_port(bridge,
                                                                 tgen_ip1,
                                                                 tunnel_type)
            (_, phy3_number) = self._vswitch.add_phy_port(bridge_ext)
            (_, vport) = self._vswitch.add_vport(bridge)
            (_, vport1) = self._vswitch.add_vport(bridge)

            tasks.run_task(['sudo', 'ip', 'addr', 'add',
                            bridge_ext_ip,
                            'dev', bridge_ext],
                           self._logger, 'Assign ' +
                           bridge_ext_ip +
                           ' to ' + bridge_ext)

            tasks.run_task(['sudo', 'ip', 'link', 'set', 'dev', bridge_ext,
                            'up'],
                           self._logger,
                           'Set ' + bridge_ext + ' status to up')

            self._vswitch.add_route(bridge,
                                    S.getValue('VTEP_IP2_SUBNET'),
                                    bridge_ext)

            self._vswitch.add_route(bridge,
                                    '0.0.0.1/24',
                                    bridge)
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
            self._vswitch.del_flow(bridge)
            flow1 = add_ports_to_flow(_FLOW_TEMPLATE, vport,
                                      phy1_number)
            flow2 = add_ports_to_flow(_FLOW_TEMPLATE, phy2_number,
                                      vport1)
            flow5 = add_ports_to_flow(_FLOW_TEMPLATE, vport1,
                                      vport)
            flow3 = add_ports_to_flow(_FLOW_TEMPLATE, phy3_number,
                                      'LOCAL')
            flow4 = add_ports_to_flow(_FLOW_TEMPLATE, 'LOCAL',
                                      phy3_number)
            self._vswitch.add_flow(bridge, flow1)
            self._vswitch.add_flow(bridge, flow2)
            self._vswitch.add_flow(bridge, flow5)

            self._vswitch.add_flow(bridge_ext, flow3)
            self._vswitch.add_flow(bridge_ext, flow4)
        except:
            self._vswitch.stop()
            raise

    def _setup_decap_encap(self):

        self._logger.debug('Setup using %s', str(self._vswitch_class))
        try:
            bridge = S.getValue('TUNNEL_INTEGRATION_BRIDGE')
            bridge_ext = S.getValue('TUNNEL_EXTERNAL_BRIDGE')
            br_ext_mac = S.getValue('TUNNEL_MODIFY_BRIDGE_MAC1')
            bridge_mac = S.getValue('TUNNEL_MODIFY_BRIDGE_MAC2')
            br_ext_ip = S.getValue('TUNNEL_MODIFY_BRIDGE_IP1')
            bridge_ip = S.getValue('TUNNEL_MODIFY_BRIDGE_IP2')
            tunnel_type = S.getValue('TUNNEL_TYPE')
            self._vswitch.start()
            self._vswitch.add_switch(bridge,
                                     params=[
                                      "other_config:hwaddr=00:00:20:00:00:01"])
            self._vswitch.add_switch(bridge_ext,
                                     params=[
                                      "other_config:hwaddr=00:00:10:00:00:01"])

            tasks.run_task(['sudo', 'iptables', '-F'],
                           self._logger, 'Clean ip tables',
                           False)
            tasks.run_task(['sudo', 'ip', 'addr', 'add',
                            br_ext_ip, 'dev', bridge_ext],
                           self._logger, 'Assign ' +
                           br_ext_ip + ' to ' + bridge_ext,
                           False)
            tasks.run_task(['sudo', 'ip', 'link', 'set', 'dev',
                            bridge_ext, 'up'],
                           self._logger, 'Bring up ' + bridge_ext, False)

            tasks.run_task(['sudo', 'ip', 'addr', 'add',
                            bridge_ip, 'dev', bridge],
                           self._logger, 'Assign ' +
                           bridge_ip + ' to ' + bridge,
                           False)
            tasks.run_task(['sudo', 'ip', 'link', 'set', 'dev', bridge, 'up'],
                           self._logger, 'Bring up ' + bridge, False)

            self._vswitch.add_route(bridge, br_ext_ip, bridge_ext)

            self._vswitch.add_route(bridge, bridge_ip, bridge)

            self._vswitch.set_tunnel_arp('10.0.0.1', br_ext_mac,
                                         bridge)
            self._vswitch.set_tunnel_arp('20.0.0.1', bridge_mac,
                                         bridge)
            self._vswitch.set_tunnel_arp('10.0.0.2', '00:00:10:00:00:02',
                                         bridge_ext)
            self._vswitch.set_tunnel_arp('20.0.0.2', '00:00:20:00:00:02',
                                         bridge)

            # Lets add the ports to bridges
            (_, phy1_number) = self._vswitch.add_phy_port(bridge_ext)
            vxlan_vni = 'options:key=' + S.getValue('VXLAN_VNI')
            (_, phy3_number) = self._vswitch.add_tunnel_port(bridge,
                                                             '10.0.0.2',
                                                             "vxlan",
                                                             params=[vxlan_vni]
                                                             )
            vm_ports = [[] for _ in range(self._pxp_vm_count)]
            for vmindex in range(self._pxp_vm_count):
                nics_nr = 1
                for _ in range(nics_nr):
                    (_, vport) = self._vswitch.add_vport(bridge)
                    vm_ports[vmindex].append(vport)
            # Set up flows for the switches
            self._vswitch.del_flow(bridge_ext)
            self._vswitch.del_flow(bridge)

            flow = add_ports_to_flow(_FLOW_TEMPLATE, phy1_number, 'LOCAL')
            self._vswitch.add_flow(bridge_ext, flow)

            flow = add_ports_to_flow(_FLOW_TEMPLATE, 'LOCAL', phy1_number)
            self._vswitch.add_flow(bridge_ext, flow)
            dst_ip_value = netaddr.IPAddress(
                                            self._traffic['l4']
                                            ['inner_dstip']).value
            stream = 0
            mod_flow_template = _FLOW_TEMPLATE.copy()
            for vmindex in range(self._pxp_vm_count):
                if self._traffic['stream_type'] == 'L3':
                    tmp_ip = netaddr.IPAddress(dst_ip_value + stream)
                    mod_flow_template.update({'ip': '', 'nw_dst': tmp_ip})
                x = vm_ports[vmindex][0]
                flow = add_ports_to_flow(mod_flow_template, phy3_number, x)
                self._vswitch.add_flow(bridge, flow)
                flow = add_ports_to_flow(_FLOW_TEMPLATE, x, phy3_number)
                self._vswitch.add_flow(bridge, flow)

                stream += 1
        except:
            self._vswitch.stop()
            raise

    def stop(self):
        """Tears down the switch created in setup().
        """
        self._logger.debug('Stop using %s', str(self._vswitch_class))
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
        self._logger.debug('get_ports_info for bridges: %s, %s',
                           S.getValue('TUNNEL_INTEGRATION_BRIDGE'),
                           S.getValue('TUNNEL_EXTERNAL_BRIDGE'))
        return self._vswitch.get_ports(
            S.getValue('TUNNEL_INTEGRATION_BRIDGE')) +\
            self._vswitch.get_ports(S.getValue('TUNNEL_EXTERNAL_BRIDGE'))

    def dump_vswitch_flows(self):
        """See IVswitchController for description
        """
        self._vswitch.dump_flows(S.getValue('TUNNEL_INTEGRATION_BRIDGE'))
        self._vswitch.dump_flows(S.getValue('TUNNEL_EXTERNAL_BRIDGE'))

    def dump_vswitch_connections(self):
        """See IVswitchController for description
        """
        self._vswitch.dump_connections(S.getValue('TUNNEL_INTEGRATION_BRIDGE'))
        self._vswitch.dump_connections(S.getValue('TUNNEL_EXTERNAL_BRIDGE'))
