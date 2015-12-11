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

"""VSwitch controller for Physical to Physical deployment
"""

import logging
import netaddr

from core.vswitch_controller import IVswitchController
from conf import settings

_FLOW_TEMPLATE = {
    'idle_timeout': '0'
}

_PROTO_TCP = 6
_PROTO_UDP = 17

class VswitchControllerP2P(IVswitchController):
    """VSwitch controller for P2P deployment scenario.

    Attributes:
        _vswitch_class: The vSwitch class to be used.
        _vswitch: The vSwitch object controlled by this controller
        _deployment_scenario: A string describing the scenario to set-up in the
            constructor.
    """
    def __init__(self, vswitch_class, traffic):
        """Initializes up the prerequisites for the P2P deployment scenario.

        :vswitch_class: the vSwitch class to be used.
        """
        self._logger = logging.getLogger(__name__)
        self._vswitch_class = vswitch_class
        self._vswitch = vswitch_class()
        self._deployment_scenario = "P2P"
        self._logger.debug('Creation using ' + str(self._vswitch_class))
        self._traffic = traffic.copy()

    def setup(self):
        """Sets up the switch for p2p.
        """
        self._logger.debug('Setup using ' + str(self._vswitch_class))

        try:
            self._vswitch.start()

            bridge = settings.getValue('VSWITCH_BRIDGE_NAME')
            self._vswitch.add_switch(bridge)

            (_, _) = self._vswitch.add_phy_port(bridge)
            (_, _) = self._vswitch.add_phy_port(bridge)

            self._vswitch.del_flow(bridge)

            # table#0 - flows designed to force 5 & 13 tuple matches go here
            flow = {'table':'0', 'priority':'1', 'actions': ['goto_table:1']}
            self._vswitch.add_flow(bridge, flow)

            # table#1 - flows to route packets between ports goes here. The
            # chosen port is communicated to subsequent tables by setting the
            # metadata value to the egress port number

            # configure flows according to the TC definition
            flow_template = _FLOW_TEMPLATE.copy()
            if self._traffic['flow_type'] == 'IP':
                flow_template.update({'dl_type':'0x0800', 'nw_src':self._traffic['l3']['srcip'],
                                      'nw_dst':self._traffic['l3']['dstip']})

            flow = flow_template.copy()
            flow.update({'table':'1', 'priority':'1', 'in_port':'1',
                         'actions': ['write_actions(output:2)', 'write_metadata:2',
                                     'goto_table:2']})
            self.process_flow_template(bridge, flow)
            flow = flow_template.copy()
            flow.update({'table':'1', 'priority':'1', 'in_port':'2',
                         'actions': ['write_actions(output:1)', 'write_metadata:1',
                                     'goto_table:2']})
            self.process_flow_template(bridge, flow)

            # Frame modification table. Frame modification flow rules are
            # isolated in this table so that they can be turned on or off
            # without affecting the routing or tuple-matching flow rules.
            flow = {'table':'2', 'priority':'1', 'actions': ['goto_table:3']}
            self._vswitch.add_flow(bridge, flow)

            # Egress table
            # (TODO) Billy O'Mahony - the drop action here actually required in
            # order to egress the packet. This is the subject of a thread on
            # ovs-discuss 2015-06-30.
            flow = {'table':'3', 'priority':'1', 'actions': ['drop']}
            self._vswitch.add_flow(bridge, flow)
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

    def process_flow_template(self, bridge, flow_template):
        """Method adds flows into the vswitch based on given flow template
           and configuration of multistream feature.
        """
        if ('pre_installed_flows' in self._traffic and
                self._traffic['pre_installed_flows'].lower() == 'yes' and
                'multistream' in self._traffic and self._traffic['multistream'] > 0 and
                'stream_type' in self._traffic):
            # multistream feature is enabled and flows should be inserted into OVS
            # so generate flows based on template and multistream configuration
            if self._traffic['stream_type'] == 'L2':
                # iterate through destimation MAC address
                dst_mac_value = netaddr.EUI(self._traffic['l2']['dstmac']).value
                for i in range(int(self._traffic['multistream'])):
                    tmp_mac = netaddr.EUI(dst_mac_value + i)
                    tmp_mac.dialect = netaddr.mac_unix_expanded
                    flow_template.update({'dl_dst':tmp_mac})
                    # optimize flow insertion by usage of cache
                    self._vswitch.add_flow(bridge, flow_template, cache='on')
            elif self._traffic['stream_type'] == 'L3':
                # iterate through destimation IP address
                dst_ip_value = netaddr.IPAddress(self._traffic['l3']['dstip']).value
                for i in range(int(self._traffic['multistream'])):
                    tmp_ip = netaddr.IPAddress(dst_ip_value + i)
                    flow_template.update({'dl_type':'0x800', 'nw_dst':tmp_ip})
                    # optimize flow insertion by usage of cache
                    self._vswitch.add_flow(bridge, flow_template, cache='on')
            elif self._traffic['stream_type'] == 'L4':
                # read transport protocol from configuration and iterate through its destination port
                proto = _PROTO_TCP if self._traffic['l3']['proto'].lower() == 'tcp' else _PROTO_UDP
                for i in range(int(self._traffic['multistream'])):
                    flow_template.update({'dl_type':'0x800', 'nw_proto':proto, 'tp_dst':i})
                    # optimize flow insertion by usage of cache
                    self._vswitch.add_flow(bridge, flow_template, cache='on')
            else:
                self._logger.error('Stream type is set to uknown value %s', self._traffic['stream_type'])
            # insert cached flows into the OVS
            self._vswitch.add_flow(bridge, [], cache='flush')
        else:
            self._vswitch.add_flow(bridge, flow_template)
