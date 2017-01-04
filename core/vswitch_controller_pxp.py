# Copyright 2016 Intel Corporation.
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

"""VSwitch controller for multi VM scenarios with serial or parallel connection
"""

import logging
import netaddr

from core.vswitch_controller import IVswitchController
from vswitches.utils import add_ports_to_flow
from conf import settings

_FLOW_TEMPLATE = {
    'idle_timeout': '0'
}

_PROTO_TCP = 6
_PROTO_UDP = 17

class VswitchControllerPXP(IVswitchController):
    """VSwitch controller for PXP deployment scenario.
    """
    def __init__(self, deployment, vswitch_class, traffic):
        """Initializes up the prerequisites for the PXP deployment scenario.

        :vswitch_class: the vSwitch class to be used.
        :deployment: the deployment scenario to configure
        :traffic: dictionary with detailed traffic definition
        """
        self._logger = logging.getLogger(__name__)
        self._vswitch_class = vswitch_class
        self._vswitch = vswitch_class()
        self._pxp_topology = 'parallel' if deployment.startswith('pvpv') else 'serial'
        if deployment == 'pvp':
            self._pxp_vm_count = 1
        elif deployment.startswith('pvvp') or deployment.startswith('pvpv'):
            if len(deployment) > 4:
                self._pxp_vm_count = int(deployment[4:])
            else:
                self._pxp_vm_count = 2
        else:
            raise RuntimeError('Unknown number of VMs involved in {} deployment.'.format(deployment))

        self._deployment_scenario = deployment

        self._traffic = traffic.copy()
        self._bidir = True if self._traffic['bidir'] == 'True' else False
        self._logger.debug('Creation using ' + str(self._vswitch_class))
        self._bridge = settings.getValue('VSWITCH_BRIDGE_NAME')

    def setup(self):
        """ Sets up the switch for PXP
        """
        self._logger.debug('Setup using ' + str(self._vswitch_class))

        try:
            self._vswitch.start()

            self._vswitch.add_switch(self._bridge)

            # create physical ports
            (_, phy1_number) = self._vswitch.add_phy_port(self._bridge)
            (_, phy2_number) = self._vswitch.add_phy_port(self._bridge)

            # create VM ports
            # initialize vport array to requested number of VMs
            guest_nics = settings.getValue('GUEST_NICS_NR')
            vm_ports = [[] for _ in range(self._pxp_vm_count)]
            # create as many VM ports as requested by configuration, but configure
            # only even number of NICs or just one
            for vmindex in range(self._pxp_vm_count):
                # just for case, enforce even number of NICs or 1
                nics_nr = int(guest_nics[vmindex] / 2) * 2 if guest_nics[vmindex] > 1 else 1
                self._logger.debug('Create %s vports for %s. VM with index %s',
                                   nics_nr, vmindex + 1, vmindex)
                for _ in range(nics_nr):
                    (_, vport) = self._vswitch.add_vport(self._bridge)
                    vm_ports[vmindex].append(vport)

            self._vswitch.del_flow(self._bridge)

            # configure flows according to the TC definition
            if self._pxp_topology == 'serial':
                flow = _FLOW_TEMPLATE.copy()
                if self._traffic['flow_type'] == 'IP':
                    flow.update({'dl_type':'0x0800',
                                 'nw_src':self._traffic['l3']['srcip'],
                                 'nw_dst':self._traffic['l3']['dstip']})

                # insert flows for phy ports first
                # from 1st PHY to 1st vport of 1st VM
                self._add_flow(flow,
                               phy1_number,
                               vm_ports[0][0],
                               self._bidir)
                # from last vport of last VM to 2nd phy
                self._add_flow(flow,
                               vm_ports[self._pxp_vm_count-1][-1],
                               phy2_number,
                               self._bidir)

                # add serial connections among VMs and VM NICs pairs if needed
                # in case of multiple NICs pairs per VM, the pairs are chained
                # first, before flow to the next VM is created
                for vmindex in range(self._pxp_vm_count):
                    # connect VMs NICs pairs in case of 4 and more NICs per VM
                    connections = [(vm_ports[vmindex][2*(x+1)-1],
                                    vm_ports[vmindex][2*(x+1)])
                                   for x in range(int(len(vm_ports[vmindex])/2)-1)]
                    for connection in connections:
                        self._add_flow(flow,
                                       connection[0],
                                       connection[1],
                                       self._bidir)
                    # connect last NICs to the next VM if there is any
                    if self._pxp_vm_count > vmindex + 1:
                        self._add_flow(flow,
                                       vm_ports[vmindex][-1],
                                       vm_ports[vmindex+1][0],
                                       self._bidir)
            else:
                proto = _PROTO_TCP if self._traffic['l3']['proto'].lower() == 'tcp' else _PROTO_UDP
                dst_mac_value = netaddr.EUI(self._traffic['l2']['dstmac']).value
                dst_ip_value = netaddr.IPAddress(self._traffic['l3']['dstip']).value
                # initialize stream index; every NIC pair of every VM uses unique stream
                stream = 0
                for vmindex in range(self._pxp_vm_count):
                    # iterate through all VMs NIC pairs...
                    if len(vm_ports[vmindex]) > 1:
                        port_pairs = [(vm_ports[vmindex][2*x],
                                       vm_ports[vmindex][2*x+1]) for x in range(int(len(vm_ports[vmindex])/2))]
                    else:
                        # ...or connect VM with just one NIC to both phy ports
                        port_pairs = [(vm_ports[vmindex][0], vm_ports[vmindex][0])]

                    for port_pair in port_pairs:
                        flow_p = _FLOW_TEMPLATE.copy()
                        flow_v = _FLOW_TEMPLATE.copy()

                        # update flow based on trafficgen settings
                        if self._traffic['stream_type'] == 'L2':
                            tmp_mac = netaddr.EUI(dst_mac_value + stream)
                            tmp_mac.dialect = netaddr.mac_unix_expanded
                            flow_p.update({'dl_dst':tmp_mac})
                        elif self._traffic['stream_type'] == 'L3':
                            tmp_ip = netaddr.IPAddress(dst_ip_value + stream)
                            flow_p.update({'dl_type':'0x0800', 'nw_dst':tmp_ip})
                        elif self._traffic['stream_type'] == 'L4':
                            flow_p.update({'dl_type':'0x0800', 'nw_proto':proto, 'tp_dst':stream})
                        else:
                            raise RuntimeError('Unknown stream_type {}'.format(self._traffic['stream_type']))

                        # insert flow to dispatch traffic from physical ports
                        # to VMs based on stream type; all traffic from VMs is
                        # sent to physical ports to avoid issues with MAC swapping
                        # and upper layer mods performed inside guests
                        self._add_flow(flow_p, phy1_number, port_pair[0])
                        self._add_flow(flow_v, port_pair[1], phy2_number)
                        if self._bidir:
                            self._add_flow(flow_p, phy2_number, port_pair[1])
                            self._add_flow(flow_v, port_pair[0], phy1_number)

                        # every NIC pair needs its own unique traffic stream
                        stream += 1

        except:
            self._vswitch.stop()
            raise

    def stop(self):
        """Tears down the switch created in setup().
        """
        self._logger.debug('Stop using ' + str(self._vswitch_class))
        self._vswitch.stop()

    def _add_flow(self, flow, port1, port2, reverse_flow=False):
        """ Helper method to insert flow into the vSwitch
        """
        self._vswitch.add_flow(self._bridge,
                               add_ports_to_flow(flow,
                                                 port1,
                                                 port2))
        if reverse_flow:
            self._vswitch.add_flow(self._bridge,
                                   add_ports_to_flow(flow,
                                                     port2,
                                                     port1))

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
        return self._vswitch.get_ports(self._bridge)

    def dump_vswitch_flows(self):
        """See IVswitchController for description
        """
        self._vswitch.dump_flows(self._bridge)
