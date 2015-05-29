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

"""VSPERF VSwitch implementation using DPDK and vhost ports
"""

from conf import settings
from vswitches.vswitch import IVSwitch
from src.ovs import VSwitchd, OFBridge
from src.dpdk import dpdk

VSWITCHD_CONST_ARGS = ['--', '--log-file']

class OvsDpdkVhost(IVSwitch):
    """VSwitch implementation using DPDK and vhost ports

    Generic OVS wrapper functionality in src.ovs is maximally used. This
    class wraps DPDK system configuration along with DPDK specific OVS
    parameters

    The method docstrings document only considerations specific to this
    implementation. For generic information of the nature of the methods,
    see the interface.
    """
    def __init__(self):
        vswitchd_args = ['--dpdk']
        vswitchd_args += settings.getValue('VSWITCHD_DPDK_ARGS')
        vswitchd_args += VSWITCHD_CONST_ARGS

        self._vswitchd = VSwitchd(vswitchd_args=vswitchd_args)
        self._bridges = {}

    def start(self):
        """See IVswitch for general description

        Activates DPDK kernel modules, ovsdb and vswitchd.
        """
        dpdk.init()
        self._vswitchd.start()

    def stop(self):
        """See IVswitch for general description

        Kills ovsdb and vswitchd and removes DPDK kernel modules.
        """
        self._vswitchd.kill()
        dpdk.cleanup()

    def add_switch(self, switch_name):
        """See IVswitch for general description
        """
        bridge = OFBridge(switch_name)
        bridge.create()
        bridge.set_db_attribute('Open_vSwitch', '.',
                                'other_config:max-idle', '60000')
        bridge.set_db_attribute('Bridge', bridge.br_name,
                                'datapath_type', 'netdev')
        self._bridges[switch_name] = bridge

    def del_switch(self, switch_name):
        """See IVswitch for general description
        """
        bridge = self._bridges[switch_name]
        self._bridges.pop(switch_name)
        bridge.destroy()

    def add_phy_port(self, switch_name):
        """See IVswitch for general description

        Creates a port of type dpdk.
        The new port is named dpdk<n> where n is an integer starting from 0.
        """
        bridge = self._bridges[switch_name]
        dpdk_count = self._get_port_count(bridge, 'type=dpdk')
        port_name = 'dpdk' + str(dpdk_count)
        params = ['--', 'set', 'Interface', port_name, 'type=dpdk']
        of_port = bridge.add_port(port_name, params)

        return (port_name, of_port)

    def add_vport(self, switch_name):
        """See IVswitch for general description

        Creates a port of type dpdkvhost
        The new port is named dpdkvhost<n> where n is an integer starting
        from 0
        """
        bridge = self._bridges[switch_name]
        vhost_count = self._get_port_count(bridge, 'type=dpdkvhost')
        port_name = 'dpdkvhost' + str(vhost_count)
        params = ['--', 'set', 'Interface', port_name, 'type=dpdkvhost']
        of_port = bridge.add_port(port_name, params)

        return (port_name, of_port)

    def get_ports(self, switch_name):
        """See IVswitch for general description
        """
        bridge = self._bridges[switch_name]
        ports = list(bridge.get_ports().items())
        return [(name, of_port) for (name, (of_port, _)) in ports]

    def del_port(self, switch_name, port_name):
        """See IVswitch for general description
        """
        bridge = self._bridges[switch_name]
        bridge.del_port(port_name)

    def add_flow(self, switch_name, flow):
        """See IVswitch for general description
        """
        bridge = self._bridges[switch_name]
        bridge.add_flow(flow)

    def del_flow(self, switch_name, flow=None):
        """See IVswitch for general description
        """
        flow = flow or {}
        bridge = self._bridges[switch_name]
        bridge.del_flow(flow)

    @staticmethod
    def _get_port_count(bridge, param):
        """Returns the number of ports having a certain parameter

        :param bridge: The src.ovs.ofctl.OFBridge on which to operate
        :param param: The parameter to search for
        :returns: Count of matches
        """
        port_params = [c for (_, (_, c)) in list(bridge.get_ports().items())]
        param_hits = [i for i in port_params if param in i]
        return len(param_hits)
