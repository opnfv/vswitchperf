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

"""Generic interface VSPERF uses for controlling a vSwitch
"""

class IVSwitch(object):
    """Interface class that is implemented by vSwitch-specific classes

    Other methods are called only between start() and stop()
    """
    def start(self):
        """Start the vSwitch

        If vSwitch is split to multiple processes, has kernel modules etc.,
        this is expected to set them all up in correct sequence
        """
        raise NotImplementedError()

    def stop(self):
        """Stop the vSwitch

        If vSwitch is split to multiple processes, has kernel modules etc.,
        this is expected to terminate and clean all of them in correct sequence
        """
        raise NotImplementedError()

    def add_switch(self, switch_name, params):
        """Create a new logical switch with no ports

        :param switch_name: The name of the new logical switch
        :param params: Optional parameters to configure switch

        :returns: None
        """
        raise NotImplementedError()

    def del_switch(self, switch_name):
        """Destroy the given logical switch

        :param switch_name: The name of the logical switch to be destroyed
        :returns: None
        """
        raise NotImplementedError()

    def add_phy_port(self, switch_name):
        """Create a new port to the logical switch that is attached to a
        physical port

        :param switch_name: The switch where the port is attached to
        :returns: (port name, OpenFlow port number)
        """
        raise NotImplementedError()

    def add_vport(self, switch_name):
        """Create a new port to the logical switch for VM connections

        :param switch_name: The switch where the port is attached to
        :returns: (port name, OpenFlow port number)
        """
        raise NotImplementedError()

    def add_tunnel_port(self, switch_name, remote_ip, tunnel_type, params=None):
        """Create a new port to the logical switch for tunneling

        :param switch_name: The switch where the port is attached to
        :returns: (port name, OpenFlow port number)
        """
        raise NotImplementedError()

    def get_ports(self, switch_name):
        """Return a list of tuples describing the ports of the logical switch

        :param switch_name: The switch whose ports to return
        :returns: [(port name, OpenFlow port number), ...]
        """
        raise NotImplementedError()

    def del_port(self, switch_name, port_name):
        """Delete the port from the logical switch

        The port can be either physical or virtual

        :param switch_name: The switch on which to operate
        :param port_name: The port to delete
        """
        raise NotImplementedError()

    def add_flow(self, switch_name, flow, cache='off'):
        """Add a flow rule to the logical switch

        :param switch_name: The switch on which to operate
        :param flow: Flow description as a dictionary
        :param cache: Optional. Specifies if flow should be inserted
            to the switch or cached to increase performance during manipulation
            with large number of flows.
            Values:
                'off'   - cache is off and flow is inserted directly to the switch
                'on'    - cache is on and flow is inserted into the cache
                'flush' - cache content will be inserted into the switch

        Example flow dictionary:
            flow = {
                'in_port': '1',
                'idle_timeout': '0',
                'actions': ['output:3']
            }
        """
        raise NotImplementedError()

    def del_flow(self, switch_name, flow=None):
        """Delete the flow rule from the logical switch

        :param switch_name: The switch on which to operate
        :param flow: Flow description as a dictionary

        For flow dictionary description, see add_flow
        For flow==None, all flows are deleted
        """
        raise NotImplementedError()

    def dump_flows(self, switch_name):
        """Dump flows from the logical switch

        :param switch_name: The switch on which to operate
        """
        raise NotImplementedError()

    def add_route(self, switch_name, network, destination):
        """Add a route for tunneling routing table

        :param switch_name: The switch on which to operate
        :param network: Target destination network
        :param destination: Gateway IP
        """
        raise NotImplementedError()

    def set_tunnel_arp(self, ip_addr, mac_addr, switch_name):
        """Add arp entry for tunneling

        :param ip_addr: IP of bridge
        :param mac_addr: MAC address of the bridge
        :param switch_name: Name of the bridge
        """
        raise NotImplementedError()
