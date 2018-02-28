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

"""VSwitch controller for Physical to VxLAN Tunnel Endpoint to Physical
   deployment with mod operation.
"""

import logging
from netaddr import EUI, IPNetwork, mac_unix

from core.vswitch_controller import IVswitchController
from vswitches.utils import add_ports_to_flow
from conf import settings
from tools import tasks

_FLOW_TEMPLATE = {
    'idle_timeout': '0'
}

class VswitchControllerPtunP(IVswitchController):
    """VSwitch controller for VxLAN ptunp deployment scenario.
    The deployment scenario is to test VxLAN tunneling feature without using an
    overlay ingress traffic. The VxLAN encap and decap performed in the virtual
    switch in each direction.

    Attributes:
        _vswitch_class: The vSwitch class to be used.
        _vswitch: The vSwitch object controlled by this controller
        _deployment_scenario: A string describing the scenario to set-up in the
            constructor.
    """
    def __init__(self, vswitch_class, traffic):
        """Initializes up the prerequisites for the ptunp deployment scenario.

        :vswitch_class: the vSwitch class to be used.
        """
        self._logger = logging.getLogger(__name__)
        self._vswitch_class = vswitch_class
        self._vswitch = vswitch_class()
        self._deployment_scenario = "ptunp"
        self._traffic = traffic.copy()
        self.bridge_phy1 = settings.getValue('TUNNEL_EXTERNAL_BRIDGE1')
        self.bridge_phy2 = settings.getValue('TUNNEL_EXTERNAL_BRIDGE2')
        self.bridge_mod1 = settings.getValue('TUNNEL_MODIFY_BRIDGE1')
        self.bridge_mod2 = settings.getValue('TUNNEL_MODIFY_BRIDGE2')
        self.br_mod_mac1 = settings.getValue('TUNNEL_MODIFY_BRIDGE_MAC1')
        self.br_mod_mac2 = settings.getValue('TUNNEL_MODIFY_BRIDGE_MAC2')
        self.br_mod_ip1 = settings.getValue('TUNNEL_MODIFY_BRIDGE_IP1')
        self.br_mod_ip2 = settings.getValue('TUNNEL_MODIFY_BRIDGE_IP2')
        self.tunnel_type = settings.getValue('TUNNEL_TYPE')
        self._logger.debug('Creation using %s', str(self._vswitch_class))

    def setup(self):
        """ Sets up the switch for VxLAN overlay PTUNP (tunnel encap or decap)
        """
        self._logger.debug('Setting up phy-tun-phy tunneling scenario')
        if self.tunnel_type == 'vxlan':
            self._setup_vxlan_encap_decap()
        else:
            self._logger.error("Only VxLAN is supported for now")
            raise NotImplementedError

    def _setup_vxlan_encap_decap(self):
        """ Sets up switches for VxLAN overlay P-TUN-P test.

            Create 2 bridges br-phy1 and br-phy2 (The bridge to connect
            physical ports. Two more bridges br-mod1 and br-mod2 to mangle
            and redirect the packets from one tunnel port to other.
        """
        self._logger.debug('Setup using %s', str(self._vswitch_class))
        try:
            self._vswitch.start()
            self._vswitch.add_switch(self.bridge_phy1)
            self._vswitch.add_switch(self.bridge_phy2)
            self._vswitch.add_switch(self.bridge_mod1,
                                     params=["other_config:hwaddr=" +
                                             self.br_mod_mac1
                                            ])
            self._vswitch.add_switch(self.bridge_mod2,
                                     params=["other_config:hwaddr=" +
                                             self.br_mod_mac2
                                            ])

            tasks.run_task(['sudo', 'iptables', '-F'],
                           self._logger, 'Clean ip tables',
                           False)
            tasks.run_task(['sudo', 'ip', 'addr', 'add',
                            self.br_mod_ip1, 'dev', self.bridge_mod1],
                           self._logger, 'Assign ' +
                           self.br_mod_ip1 + ' to ' + self.bridge_mod1,
                           False)
            tasks.run_task(['sudo', 'ip', 'link', 'set', 'dev', self.bridge_mod1, 'up'],
                           self._logger, 'Bring up ' + self.bridge_mod1, False)

            tasks.run_task(['sudo', 'ip', 'addr', 'add',
                            self.br_mod_ip2, 'dev', self.bridge_mod2],
                           self._logger, 'Assign ' +
                           self.br_mod_ip2 + ' to ' + self.bridge_mod2,
                           False)
            tasks.run_task(['sudo', 'ip', 'link', 'set', 'dev', self.bridge_mod2, 'up'],
                           self._logger, 'Bring up ' + self.bridge_mod2, False)

            tasks.run_task(['sudo', 'ip', 'link', 'set', 'dev', self.bridge_phy1, 'up'],
                           self._logger, 'Bring up ' + self.bridge_phy1, False)
            tasks.run_task(['sudo', 'ip', 'link', 'set', 'dev', self.bridge_phy2, 'up'],
                           self._logger, 'Bring up ' + self.bridge_phy2, False)
            self._vswitch.add_route(self.bridge_phy1, self.br_mod_ip1, self.bridge_mod1)
            self._vswitch.add_route(self.bridge_phy2, self.br_mod_ip2, self.bridge_mod2)

            # Create tunnel ip and mac from the bridge ips
            vxlan_local_ip1 = str(IPNetwork(self.br_mod_ip1).ip)
            vxlan_local_ip2 = str(IPNetwork(self.br_mod_ip2).ip)
            vxlan_rem_ip1 = str(IPNetwork(self.br_mod_ip1).ip + 1)
            vxlan_rem_ip2 = str(IPNetwork(self.br_mod_ip2).ip + 1)
            vxlan_rem_mac1 = EUI(int(EUI(self.br_mod_mac1)) + 1)
            vxlan_rem_mac1.dialect = mac_unix
            vxlan_rem_mac2 = EUI(int(EUI(self.br_mod_mac2)) + 1)
            vxlan_rem_mac2.dialect = mac_unix
            self._vswitch.set_tunnel_arp(vxlan_local_ip1, self.br_mod_mac1,
                                         self.bridge_phy1)
            self._vswitch.set_tunnel_arp(vxlan_local_ip2, self.br_mod_mac2,
                                         self.bridge_phy2)
            self._vswitch.set_tunnel_arp(vxlan_rem_ip1, str(vxlan_rem_mac1),
                                         self.bridge_mod1)
            self._vswitch.set_tunnel_arp(vxlan_rem_ip2, str(vxlan_rem_mac2),
                                         self.bridge_mod2)

            # Lets add the ports to bridges
            (_, phy1_number) = self._vswitch.add_phy_port(self.bridge_phy1)
            (_, phy2_number) = self._vswitch.add_phy_port(self.bridge_phy2)
            vxlan_vni = 'options:key=' + settings.getValue('VXLAN_VNI')
            (_, phy3_number) = self._vswitch.add_tunnel_port(self.bridge_phy1,
                                                             vxlan_rem_ip1,
                                                             "vxlan",
                                                             params=[vxlan_vni])
            (_, phy4_number) = self._vswitch.add_tunnel_port(self.bridge_phy2,
                                                             vxlan_rem_ip2,
                                                             "vxlan",
                                                             params=[vxlan_vni])
            [(_, phy5_number), (_, phy6_number)] = \
                     self._vswitch.add_veth_pair_port(self.bridge_mod1, self.bridge_mod2)

            # Set up flows for the switches
            self._vswitch.del_flow(self.bridge_phy1)
            self._vswitch.del_flow(self.bridge_phy2)
            self._vswitch.del_flow(self.bridge_mod1)
            self._vswitch.del_flow(self.bridge_mod2)
            flow = add_ports_to_flow(_FLOW_TEMPLATE, phy1_number,
                                     phy3_number)
            self._vswitch.add_flow(self.bridge_phy1, flow)
            flow = add_ports_to_flow(_FLOW_TEMPLATE, phy3_number,
                                     phy1_number)
            self._vswitch.add_flow(self.bridge_phy1, flow)

            flow = add_ports_to_flow(_FLOW_TEMPLATE, phy2_number,
                                     phy4_number)
            self._vswitch.add_flow(self.bridge_phy2, flow)
            flow = add_ports_to_flow(_FLOW_TEMPLATE, phy4_number,
                                     phy2_number)
            self._vswitch.add_flow(self.bridge_phy2, flow)
            flow = add_ports_to_flow(_FLOW_TEMPLATE, phy5_number,
                                     'LOCAL')
            self._vswitch.add_flow(self.bridge_mod1, flow)
            mod_flow_template = _FLOW_TEMPLATE.copy()
            mod_flow_template.update({'ip':'',
                                      'actions':
                                      ['mod_dl_src:' + str(vxlan_rem_mac2),
                                       'mod_dl_dst:' + self.br_mod_mac2,
                                       'mod_nw_src:' + vxlan_rem_ip2,
                                       'mod_nw_dst:' + vxlan_local_ip2
                                      ]
                                     })
            flow = add_ports_to_flow(mod_flow_template, 'LOCAL', phy5_number)
            self._vswitch.add_flow(self.bridge_mod1, flow)
            flow = add_ports_to_flow(_FLOW_TEMPLATE, phy6_number,
                                     'LOCAL')
            self._vswitch.add_flow(self.bridge_mod2, flow)
            mod_flow_template = _FLOW_TEMPLATE.copy()
            mod_flow_template.update({'ip':'',
                                      'actions':
                                      ['mod_dl_src:' + str(vxlan_rem_mac1),
                                       'mod_dl_dst:' + self.br_mod_mac1,
                                       'mod_nw_src:' + vxlan_rem_ip1,
                                       'mod_nw_dst:' + vxlan_local_ip1]
                                     })
            flow = add_ports_to_flow(mod_flow_template, 'LOCAL', phy6_number)
            self._vswitch.add_flow(self.bridge_mod2, flow)

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
        self._logger.debug('get_ports_info using %s', str(self._vswitch_class))
        ports = self._vswitch.get_ports(self.bridge_phy1) +\
                self._vswitch.get_ports(self.bridge_mod1) +\
                self._vswitch.get_ports(self.bridge_phy2) +\
                self._vswitch.get_ports(self.bridge_mod2)
        return ports

    def dump_vswitch_flows(self):
        """See IVswitchController for description
        """
        self._logger.debug('dump_flows using %s', str(self._vswitch_class))
        self._vswitch.dump_flows(self.bridge_phy1)
        self._vswitch.dump_flows(self.bridge_mod1)
        self._vswitch.dump_flows(self.bridge_phy2)
        self._vswitch.dump_flows(self.bridge_mod2)
