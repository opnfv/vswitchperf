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

"""VSPERF Open vSwitch base class
"""

import logging
import re
from conf import settings
from vswitches.vswitch import IVSwitch
from src.ovs import OFBridge, flow_key, flow_match

_VSWITCHD_CONST_ARGS = []

class IVSwitchOvs(IVSwitch):
    """Open vSwitch base class implementation

    The method docstrings document only considerations specific to this
    implementation. For generic information of the nature of the methods,
    see the interface.
    """

    def __init__(self):
        """See IVswitch for general description
        """
        self._vswitchd = None
        self._logger = logging.getLogger(__name__)
        self._bridges = {}
        self._vswitchd_args = _VSWITCHD_CONST_ARGS

    def start(self):
        """See IVswitch for general description
        """
        self._logger.info("Starting vswitchd...")
        self._vswitchd.start()
        self._logger.info("Vswitchd...Started.")

    def stop(self):
        """See IVswitch for general description
        """
        self._logger.info("Terminating vswitchd...")
        self._vswitchd.kill()
        self._logger.info("Vswitchd...Terminated.")

    def add_switch(self, switch_name, params=None):
        """See IVswitch for general description
        """
        bridge = OFBridge(switch_name)
        bridge.create(params)
        bridge.set_db_attribute('Open_vSwitch', '.',
                                'other_config:max-idle',
                                settings.getValue('VSWITCH_FLOW_TIMEOUT'))
        self._bridges[switch_name] = bridge

    def del_switch(self, switch_name):
        """See IVswitch for general description
        """
        bridge = self._bridges[switch_name]
        self._bridges.pop(switch_name)
        bridge.destroy()

    def add_phy_port(self, switch_name):
        """See IVswitch for general description
        """
        raise NotImplementedError

    def add_vport(self, switch_name):
        """See IVswitch for general description
        """
        raise NotImplementedError

    def add_tunnel_port(self, switch_name, remote_ip, tunnel_type='vxlan', params=None):
        """Creates tunneling port
        """
        bridge = self._bridges[switch_name]
        pcount = str(self._get_port_count('type=' + tunnel_type))
        port_name = tunnel_type + pcount
        local_params = ['--', 'set', 'Interface', port_name,
                        'type=' + tunnel_type,
                        'options:remote_ip=' + remote_ip]

        if params is not None:
            local_params = local_params + params

        of_port = bridge.add_port(port_name, local_params)
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

    def add_flow(self, switch_name, flow, cache='off'):
        """See IVswitch for general description
        """
        bridge = self._bridges[switch_name]
        bridge.add_flow(flow, cache=cache)

    def del_flow(self, switch_name, flow=None):
        """See IVswitch for general description
        """
        flow = flow or {}
        bridge = self._bridges[switch_name]
        bridge.del_flow(flow)

    def dump_flows(self, switch_name):
        """See IVswitch for general description
        """
        bridge = self._bridges[switch_name]
        bridge.dump_flows()

    def add_route(self, switch_name, network, destination):
        """See IVswitch for general description
        """
        bridge = self._bridges[switch_name]
        bridge.add_route(network, destination)

    def set_tunnel_arp(self, ip_addr, mac_addr, switch_name):
        """See IVswitch for general description
        """
        bridge = self._bridges[switch_name]
        bridge.set_tunnel_arp(ip_addr, mac_addr, switch_name)

    def _get_port_count(self, param):
        """Returns the number of ports having a certain parameter
        """
        cnt = 0
        for k in self._bridges:
            pparams = [c for (_, (_, c)) in list(self._bridges[k].get_ports().items())]
            phits = [i for i in pparams if param in i]
            cnt += len(phits)

        if cnt is None:
            cnt = 0
        return cnt

    def validate_add_switch(self, result, switch_name, params=None):
        """Validate - Create a new logical switch with no ports
        """
        bridge = self._bridges[switch_name]
        output = bridge.run_vsctl(['show'], check_error=True)
        assert not output[1]  # there shouldn't be any stderr, but in case
        assert re.search('Bridge ["\']?%s["\']?' % switch_name, output[0]) is not None
        return True

    def validate_del_switch(self, result, switch_name):
        """Validate removal of switch
        """
        bridge = OFBridge('tmp')
        output = bridge.run_vsctl(['show'], check_error=True)
        assert not output[1]  # there shouldn't be any stderr, but in case
        assert re.search('Bridge ["\']?%s["\']?' % switch_name, output[0]) is None
        return True

    def validate_add_phy_port(self, result, switch_name):
        """ Validate that physical port was added to bridge.
        """
        bridge = self._bridges[switch_name]
        output = bridge.run_vsctl(['show'], check_error=True)
        assert not output[1]  # there shouldn't be any stderr, but in case
        assert re.search('Port ["\']?%s["\']?' % result[0], output[0]) is not None
        assert re.search('Interface ["\']?%s["\']?' % result[0], output[0]) is not None
        return True

    def validate_add_vport(self, result, switch_name):
        """ Validate that virtual port was added to bridge.
        """
        return self.validate_add_phy_port(result, switch_name)

    def validate_del_port(self, result, switch_name, port_name):
        """ Validate that port_name was removed from bridge.
        """
        bridge = self._bridges[switch_name]
        output = bridge.run_vsctl(['show'], check_error=True)
        assert not output[1]  # there shouldn't be any stderr, but in case
        assert 'Port "%s"' % port_name not in output[0]
        return True

    def validate_add_flow(self, result, switch_name, flow, cache='off'):
        """ Validate insertion of the flow into the switch
        """
        if 'idle_timeout' in flow:
            del(flow['idle_timeout'])

        # Note: it should be possible to call `ovs-ofctl dump-flows switch flow`
        # to verify flow insertion, but it doesn't accept the same flow syntax
        # as add-flow, so we have to compare it the hard way

        # get dump of flows and compare them one by one
        flow_src = flow_key(flow)
        bridge = self._bridges[switch_name]
        output = bridge.run_ofctl(['dump-flows', switch_name], check_error=True)
        for flow_dump in output[0].split('\n'):
            if flow_match(flow_dump, flow_src):
                # flow was added correctly
                return True
        return False

    def validate_del_flow(self, result, switch_name, flow=None):
        """ Validate removal of the flow
        """
        if not flow:
            # what else we can do?
            return True
        return not self.validate_add_flow(result, switch_name, flow)

    def validate_dump_flows(self, result, switch_name):
        """ Validate call of flow dump
        """
        return True
