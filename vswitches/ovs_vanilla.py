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

"""VSPERF Vanilla OVS implementation
"""

import logging
from conf import settings
from vswitches.vswitch import IVSwitch
from src.ovs import VSwitchd, OFBridge, DPCtl
from tools.module_manager import ModuleManager
from tools import tasks

_LOGGER = logging.getLogger(__name__)
VSWITCHD_CONST_ARGS = ['--', '--log-file']

class OvsVanilla(IVSwitch):
    """VSwitch Vanilla implementation

    This is wrapper for functionality implemented in src.ovs.

    The method docstrings document only considerations specific to this
    implementation. For generic information of the nature of the methods,
    see the interface definition.
    """

    _logger = logging.getLogger()
    _ports = settings.getValue('VSWITCH_VANILLA_PHY_PORT_NAMES')
    _current_id = 0
    _vport_id = 0

    def __init__(self):
        #vswitchd_args = VSWITCHD_CONST_ARGS
        vswitchd_args = ["unix:%s" % VSwitchd.get_db_sock_path()]
        vswitchd_args += settings.getValue('VSWITCHD_VANILLA_ARGS')
        self._vswitchd = VSwitchd(vswitchd_args=vswitchd_args,
                                  expected_cmd="db.sock: connected")
        self._bridges = {}
        self._module_manager = ModuleManager()

    def start(self):
        """See IVswitch for general description

        Activates kernel modules, ovsdb and vswitchd.
        """
        self._module_manager.insert_modules(
            settings.getValue('VSWITCH_VANILLA_KERNEL_MODULES'))
        self._logger.info("Starting Vswitchd...")
        self._vswitchd.start()
        self._logger.info("Vswitchd...Started.")

    def stop(self):
        """See IVswitch for general description

        Kills ovsdb and vswitchd and removes kernel modules.
        """
        # remove all tap interfaces
        for i in range(self._vport_id):
            tapx = 'tap' + str(i)
            tasks.run_task(['sudo', 'ip', 'tuntap', 'del',
                            tapx, 'mode', 'tap'],
                           _LOGGER, 'Deleting ' + tapx, False)
        self._vport_id = 0

        self._vswitchd.kill()
        dpctl = DPCtl()
        dpctl.del_dp()

        self._module_manager.remove_modules()


    def add_switch(self, switch_name, params=None):
        """See IVswitch for general description
        """
        bridge = OFBridge(switch_name)
        bridge.create(params)
        bridge.set_db_attribute('Open_vSwitch', '.',
                                'other_config:max-idle', '60000')
        self._bridges[switch_name] = bridge

    def del_switch(self, switch_name):
        """See IVswitch for general description
        """
        bridge = self._bridges[switch_name]
        self._bridges.pop(switch_name)
        bridge.destroy()

    def add_phy_port(self, switch_name):
        """
        Method adds port based on configured VSWITCH_VANILLA_PHY_PORT_NAMES
        stored in config file.

        See IVswitch for general description
        """
        if self._current_id == len(self._ports):
            self._logger.error("Can't add port! There are only " +
                               len(self._ports) + " ports " +
                               "defined in config!")
            raise

        if not self._ports[self._current_id]:
            self._logger.error("VSWITCH_VANILLA_PHY_PORT_NAMES not set")
            raise ValueError("Invalid VSWITCH_VANILLA_PHY_PORT_NAMES")

        bridge = self._bridges[switch_name]
        port_name = self._ports[self._current_id]
        params = []

        # For PVP only
        tasks.run_task(['sudo', 'ifconfig', port_name, '0'],
                       _LOGGER, 'Remove IP', False)

        of_port = bridge.add_port(port_name, params)
        self._current_id += 1
        return (port_name, of_port)

    def add_vport(self, switch_name):
        """
        Method adds virtual port into OVS vanilla

        See IVswitch for general description
        """
        # Create tap devices for the VM
        tap_name = 'tap' + str(self._vport_id)
        self._vport_id += 1

        tasks.run_task(['sudo', 'ip', 'tuntap', 'del',
                        tap_name, 'mode', 'tap'],
                       _LOGGER, 'Creating tap device...', False)

        tasks.run_task(['sudo', 'ip', 'tuntap', 'add',
                        tap_name, 'mode', 'tap'],
                       _LOGGER, 'Creating tap device...', False)

        tasks.run_task(['sudo', 'ifconfig', tap_name, '0'],
                       _LOGGER, 'Bring up ' + tap_name, False)

        bridge = self._bridges[switch_name]
        of_port = bridge.add_port(tap_name, [])
        return (tap_name, of_port)

    def add_tunnel_port(self, switch_name, remote_ip, tunnel_type='vxlan',
                        params=None):
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

        :param bridge: The src.ovs.ofctl.OFBridge on which to operate
        :param param: The parameter to search for
        :returns: Count of matches
        """
        cnt = 0
        for k in self._bridges:
            pparams = [c for (_, (_, c)) in list(self._bridges[k].get_ports().items())]
            phits = [i for i in pparams if param in i]
            cnt += len(phits)

        if cnt is None:
            cnt = 0
        return cnt


