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

"""Generic interface VSPERF uses for controlling a vSwitch
"""
import logging

class IVSwitch(object):
    """Interface class that is implemented by vSwitch-specific classes

    Other methods are called only between start() and stop()
    """
    def __init__(self):
        """Initialization of vswitch class
        """
        self._timeout = 30
        self._switches = {}
        self._logger = logging.getLogger(__name__)
        self._cmd = []
        self._vswitch_args = []
        self._stamp = None

    def get_version(self):
        """Return version of vSwitch and DPDK (if used by vSwitch)
           This method should be implemented in case, that version
           of vswitch or DPDK can be read only during vSwitch runtime.
           Otherwise it can be implemented inside tools/systeminfo.py.
        """
        raise NotImplementedError()

    def start(self):
        """Start the vSwitch

        If vSwitch is split to multiple processes, has kernel modules etc.,
        this is expected to set them all up in correct sequence
        """
        raise NotImplementedError()

    def restart(self):
        """Retart the vSwitch

        Restart of vSwitch is required for failover testcases.
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

    def add_connection(self, switch_name, port1, port2, traffic=None):
        """Creates connection between given ports.

        :param switch_name: switch on which to operate
        :param port1: port to be used in connection
        :param port2: port to be used in connection

        :raises: RuntimeError
        """
        raise NotImplementedError()

    def del_connection(self, switch_name, port1=None, port2=None):
        """Remove connection between two interfaces.

        :param switch_name: switch on which to operate
        :param port1: port to be used in connection
        :param port2: port to be used in connection

        :raises: RuntimeError
        """
        raise NotImplementedError()

    def dump_connections(self, switch_name):
        """Dump connections between interfaces.

        :param switch_name: switch on which to operate

        :raises: RuntimeError
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
