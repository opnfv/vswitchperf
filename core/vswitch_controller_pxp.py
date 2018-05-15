# Copyright 2016-2018 Intel Corporation., Tieto
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
import netaddr

from core.vswitch_controller import IVswitchController
from conf import settings

class VswitchControllerPXP(IVswitchController):
    """VSwitch controller for PXP deployment scenario.
    """
    def __init__(self, deployment, vswitch_class, traffic):
        """See IVswitchController for general description
        """
        super().__init__(deployment, vswitch_class, traffic)
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

        self._bidir = True if self._traffic['bidir'] == 'True' else False
        self._bridge = settings.getValue('VSWITCH_BRIDGE_NAME')

    def setup(self):
        """ Sets up the switch for PXP
        """
        self._logger.debug('Setup using %s', str(self._vswitch_class))

        try:
            self._vswitch.start()

            self._vswitch.add_switch(self._bridge)

            # create physical ports
            (phy1, _) = self._vswitch.add_phy_port(self._bridge)
            (phy2, _) = self._vswitch.add_phy_port(self._bridge)

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
                    (vport, _) = self._vswitch.add_vport(self._bridge)
                    vm_ports[vmindex].append(vport)

            # configure connections according to the TC definition
            if self._pxp_topology == 'serial':
                # NOTE: all traffic from VMs is sent to other ports directly
                # without applying traffic options to avoid issues with MAC swapping
                # and upper layer mods performed inside guests

                # insert connections for phy ports first
                # from 1st PHY to 1st vport of 1st VM
                self._vswitch.add_connection(self._bridge, phy1, vm_ports[0][0], self._traffic)
                self._vswitch.add_connection(self._bridge, vm_ports[0][0], phy1)
                # from last vport of last VM to 2nd phy
                self._vswitch.add_connection(self._bridge, vm_ports[self._pxp_vm_count-1][-1], phy2)
                self._vswitch.add_connection(self._bridge, phy2, vm_ports[self._pxp_vm_count-1][-1], self._traffic)

                # add serial connections among VMs and VM NICs pairs if needed
                # in case of multiple NICs pairs per VM, the pairs are chained
                # first, before connection to the next VM is created
                for vmindex in range(self._pxp_vm_count):
                    # connect VMs NICs pairs in case of 4 and more NICs per VM
                    connections = [(vm_ports[vmindex][2*(x+1)-1],
                                    vm_ports[vmindex][2*(x+1)])
                                   for x in range(int(len(vm_ports[vmindex])/2)-1)]
                    for connection in connections:
                        self._vswitch.add_connection(self._bridge, connection[0], connection[1])
                        self._vswitch.add_connection(self._bridge, connection[1], connection[0])
                    # connect last NICs to the next VM if there is any
                    if self._pxp_vm_count > vmindex + 1:
                        self._vswitch.add_connection(self._bridge, vm_ports[vmindex][-1], vm_ports[vmindex+1][0])
                        self._vswitch.add_connection(self._bridge, vm_ports[vmindex+1][0], vm_ports[vmindex][-1])
            else:
                mac_value = netaddr.EUI(self._traffic['l2']['dstmac']).value
                ip_value = netaddr.IPAddress(self._traffic['l3']['dstip']).value
                port_value = self._traffic['l4']['dstport']
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
                        # override traffic options to ensure, that traffic is
                        # dispatched among VMs connected in parallel
                        options = {'multistream':1,
                                   'stream_type':self._traffic['stream_type'],
                                   'pre_installed_flows':'Yes'}
                        # update connection based on trafficgen settings
                        if self._traffic['stream_type'] == 'L2':
                            tmp_mac = netaddr.EUI(mac_value + stream)
                            tmp_mac.dialect = netaddr.mac_unix_expanded
                            options.update({'l2':{'dstmac':tmp_mac}})
                        elif self._traffic['stream_type'] == 'L3':
                            tmp_ip = netaddr.IPAddress(ip_value + stream)
                            options.update({'l3':{'dstip':tmp_ip}})
                        elif self._traffic['stream_type'] == 'L4':
                            options.update({'l3':{'proto':self._traffic['l3']['proto']}})
                            options.update({'l4':{'dstport':(port_value + stream) % 65536}})
                        else:
                            raise RuntimeError('Unknown stream_type {}'.format(self._traffic['stream_type']))

                        # insert connection to dispatch traffic from physical ports
                        # to VMs based on stream type; all traffic from VMs is
                        # sent to physical ports to avoid issues with MAC swapping
                        # and upper layer mods performed inside guests
                        self._vswitch.add_connection(self._bridge, phy1, port_pair[0], options)
                        self._vswitch.add_connection(self._bridge, port_pair[1], phy2)
                        self._vswitch.add_connection(self._bridge, phy2, port_pair[1], options)
                        self._vswitch.add_connection(self._bridge, port_pair[0], phy1)

                        # every NIC pair needs its own unique traffic stream
                        stream += 1

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
