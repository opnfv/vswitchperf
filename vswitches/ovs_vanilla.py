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

"""VSPERF Vanilla OVS implementation
"""

import time
from conf import settings
from vswitches.ovs import IVSwitchOvs
from src.ovs import DPCtl
from tools import tasks

class OvsVanilla(IVSwitchOvs):
    """ Open vSwitch

    This is wrapper for functionality implemented in src.ovs.

    The method docstrings document only considerations specific to this
    implementation. For generic information of the nature of the methods,
    see the interface definition.
    """

    _current_id = 0
    _vport_id = 0

    def __init__(self):
        super().__init__()
        self._ports = list(nic['device'] for nic in settings.getValue('NICS'))
        self._vswitchd_args += ["unix:%s" % self.get_db_sock_path()]
        self._vswitchd_args += settings.getValue('VSWITCHD_VANILLA_ARGS')

    def stop(self):
        """See IVswitch for general description

        Kills ovsdb and vswitchd and removes kernel modules.
        """
        # remove all tap interfaces
        for i in range(self._vport_id):
            tapx = 'tap' + str(i)
            tap_cmd_list = ['sudo', 'ip', 'tuntap', 'del', tapx, 'mode', 'tap']
            # let's assume, that all VMs have NIC QUEUES enabled or disabled
            # at the same time
            if int(settings.getValue('GUEST_NIC_QUEUES')[0]):
                tap_cmd_list += ['multi_queue']
            tasks.run_task(tap_cmd_list, self._logger, 'Deleting ' + tapx, False)
        self._vport_id = 0

        # remove datapath before vswitch shutdown
        dpctl = DPCtl()
        dpctl.del_dp()

        super(OvsVanilla, self).stop()

        # give vswitch time to terminate before modules are removed
        time.sleep(5)
        self._module_manager.remove_modules()

    def add_phy_port(self, switch_name):
        """
        Method adds port based on detected device names.

        See IVswitch for general description
        """
        if self._current_id == len(self._ports):
            raise RuntimeError("Can't add phy port! There are only {} ports defined "
                               "by WHITELIST_NICS parameter!".format(len(self._ports)))
        if not self._ports[self._current_id]:
            self._logger.error("Can't detect device name for NIC %s", self._current_id)
            raise ValueError("Invalid device name for %s" % self._current_id)

        bridge = self._switches[switch_name]
        port_name = self._ports[self._current_id]
        params = []

        # For PVP only
        tasks.run_task(['sudo', 'ip', 'addr', 'flush', 'dev', port_name],
                       self._logger, 'Remove IP', False)
        tasks.run_task(['sudo', 'ip', 'link', 'set', 'dev', port_name, 'up'],
                       self._logger, 'Bring up ' + port_name, False)

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
        tap_cmd_list = ['sudo', 'ip', 'tuntap', 'del', tap_name, 'mode', 'tap']
        # let's assume, that all VMs have NIC QUEUES enabled or disabled
        # at the same time
        if int(settings.getValue('GUEST_NIC_QUEUES')[0]):
            tap_cmd_list += ['multi_queue']
        tasks.run_task(tap_cmd_list, self._logger,
                       'Creating tap device...', False)

        tap_cmd_list = ['sudo', 'ip', 'tuntap', 'add', tap_name, 'mode', 'tap']
        # let's assume, that all VMs have NIC QUEUES enabled or disabled
        # at the same time
        if int(settings.getValue('GUEST_NIC_QUEUES')[0]):
            tap_cmd_list += ['multi_queue']
        tasks.run_task(tap_cmd_list, self._logger,
                       'Creating tap device...', False)
        if settings.getValue('VSWITCH_JUMBO_FRAMES_ENABLED'):
            tasks.run_task(['ifconfig', tap_name, 'mtu',
                            str(settings.getValue('VSWITCH_JUMBO_FRAMES_SIZE'))],
                           self._logger, 'Setting mtu size', False)

        tasks.run_task(['sudo', 'ip', 'addr', 'flush', 'dev', tap_name],
                       self._logger, 'Remove IP', False)
        tasks.run_task(['sudo', 'ip', 'link', 'set', 'dev', tap_name, 'up'],
                       self._logger, 'Bring up ' + tap_name, False)

        bridge = self._switches[switch_name]
        of_port = bridge.add_port(tap_name, [])
        return (tap_name, of_port)
