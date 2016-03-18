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
from vswitches.ovs import IVSwitchOvs
from src.ovs import VSwitchd, DPCtl
from tools.module_manager import ModuleManager
from tools import tasks

class OvsVanilla(IVSwitchOvs):
    """ Open vSwitch

    This is wrapper for functionality implemented in src.ovs.

    The method docstrings document only considerations specific to this
    implementation. For generic information of the nature of the methods,
    see the interface definition.
    """

    _ports = list(nic['device'] for nic in settings.getValue('NICS'))
    _current_id = 0
    _vport_id = 0

    def __init__(self):
        super(OvsVanilla, self).__init__()
        self._logger = logging.getLogger(__name__)
        self._vswitchd_args = ["unix:%s" % VSwitchd.get_db_sock_path()]
        self._vswitchd_args += settings.getValue('VSWITCHD_VANILLA_ARGS')
        self._vswitchd = VSwitchd(vswitchd_args=self._vswitchd_args,
                                  expected_cmd="db.sock: connected")
        self._bridges = {}
        self._module_manager = ModuleManager()

    def start(self):
        """See IVswitch for general description

        Activates kernel modules, ovsdb and vswitchd.
        """
        self._module_manager.insert_modules(
            settings.getValue('VSWITCH_VANILLA_KERNEL_MODULES'))
        super(OvsVanilla, self).start()

    def stop(self):
        """See IVswitch for general description

        Kills ovsdb and vswitchd and removes kernel modules.
        """
        # remove all tap interfaces
        for i in range(self._vport_id):
            tapx = 'tap' + str(i)
            tasks.run_task(['sudo', 'ip', 'tuntap', 'del',
                            tapx, 'mode', 'tap'],
                           self._logger, 'Deleting ' + tapx, False)
        self._vport_id = 0

        super(OvsVanilla, self).stop()
        dpctl = DPCtl()
        dpctl.del_dp()

        self._module_manager.remove_modules()


    def add_phy_port(self, switch_name):
        """
        Method adds port based on detected device names.

        See IVswitch for general description
        """
        if self._current_id == len(self._ports):
            self._logger.error("Can't add port! There are only " +
                               len(self._ports) + " ports " +
                               "defined in config!")
            raise

        if not self._ports[self._current_id]:
            self._logger.error("Can't detect device name for NIC %s", self._current_id)
            raise ValueError("Invalid device name for %s" % self._current_id)

        bridge = self._bridges[switch_name]
        port_name = self._ports[self._current_id]
        params = []

        # For PVP only
        tasks.run_task(['sudo', 'ifconfig', port_name, '0'],
                       self._logger, 'Remove IP', False)

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
                       self._logger, 'Creating tap device...', False)

        tasks.run_task(['sudo', 'ip', 'tuntap', 'add',
                        tap_name, 'mode', 'tap'],
                       self._logger, 'Creating tap device...', False)

        tasks.run_task(['sudo', 'ifconfig', tap_name, '0'],
                       self._logger, 'Bring up ' + tap_name, False)

        bridge = self._bridges[switch_name]
        of_port = bridge.add_port(tap_name, [])
        return (tap_name, of_port)


