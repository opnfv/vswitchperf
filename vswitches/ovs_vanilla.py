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

"""VSPERF Vanilla OVS implementation
"""

import logging
from conf import settings
from vswitches.vswitch import IVSwitch
from src.ovs import VSwitchd, OFBridge
from tools.module_manager import ModuleManager, KernelModuleInsertMode

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

    def __init__(self):
        #vswitchd_args = VSWITCHD_CONST_ARGS
        vswitchd_args = ["unix:%s" % VSwitchd.getDbSockPath()]
        vswitchd_args += settings.getValue('VSWITCHD_VANILLA_ARGS')
        self._vswitchd = VSwitchd(vswitchd_args=vswitchd_args,
                                  expected_cmd="db.sock: connected")
        self._bridges = {}
        self._module_manager = ModuleManager(KernelModuleInsertMode.MODPROBE)

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
        self._vswitchd.kill()
        self._module_manager.remove_modules()

    def add_switch(self, switch_name):
        """See IVswitch for general description
        """
        bridge = OFBridge(switch_name)
        bridge.create()
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

        bridge = self._bridges[switch_name]
        port_name = self._ports[self._current_id]
        params = []
        of_port = bridge.add_port(port_name, params)
        self._current_id += 1
        return (port_name, of_port)

    def add_vport(self, switch_name):
        """See IVswitch for general description"""
        raise NotImplementedError("Not implemented for Vanilla OVS.")

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
