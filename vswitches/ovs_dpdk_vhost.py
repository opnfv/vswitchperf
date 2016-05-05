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

"""VSPERF VSwitch implementation using DPDK and vhost ports
"""

import logging
import subprocess
import os

from src.ovs import OFBridge
from src.dpdk import dpdk
from conf import settings
from vswitches.ovs import IVSwitchOvs

class OvsDpdkVhost(IVSwitchOvs):
    """ Open vSwitch with DPDK support

    Generic OVS wrapper functionality in src.ovs is maximally used. This
    class wraps DPDK system configuration along with DPDK specific OVS
    parameters

    The method docstrings document only considerations specific to this
    implementation. For generic information of the nature of the methods,
    see the interface.
    """

    def __init__(self):
        super(OvsDpdkVhost, self).__init__()
        self._logger = logging.getLogger(__name__)
        self._expect = r'EAL: Master l*core \d+ is ready'

        vswitchd_args = []

        # legacy DPDK configuration through --dpdk option of vswitchd
        if self.old_dpdk_config():
            vswitchd_args = ['--dpdk'] + settings.getValue('VSWITCHD_DPDK_ARGS')
            if self._vswitchd_args:
                self._vswitchd_args = vswitchd_args + ['--'] + self._vswitchd_args
            else:
                self._vswitchd_args = vswitchd_args

        if settings.getValue('VNF').endswith('Cuse'):
            self._logger.info("Inserting VHOST Cuse modules into kernel...")
            dpdk.insert_vhost_modules()

    def configure(self):
        """ Configure vswitchd DPDK options through ovsdb if needed
        """
        dpdk_config = settings.getValue('VSWITCHD_DPDK_CONFIG')
        if dpdk_config and not self.old_dpdk_config():
            # enforce calls to ovs-vsctl with --no-wait
            tmp_br = OFBridge(timeout=-1)
            for option in dpdk_config:
                tmp_br.set_db_attribute('Open_vSwitch', '.',
                                        'other_config:' + option, dpdk_config[option])

    def start(self):
        """See IVswitch for general description

        Activates DPDK kernel modules, ovsdb and vswitchd.
        """
        dpdk.init()
        super(OvsDpdkVhost, self).start()

    def stop(self):
        """See IVswitch for general description

        Kills ovsdb and vswitchd and removes DPDK kernel modules.
        """
        super(OvsDpdkVhost, self).stop()
        dpdk.cleanup()
        dpdk.remove_vhost_modules()

    def add_switch(self, switch_name, params=None):
        """See IVswitch for general description
        """
        switch_params = ['--', 'set', 'bridge', switch_name, 'datapath_type=netdev']
        if params:
            switch_params = switch_params + params

        super(OvsDpdkVhost, self).add_switch(switch_name, switch_params)

        if settings.getValue('VSWITCH_AFFINITIZATION_ON') == 1:
            # Sets the PMD core mask to VSWITCH_PMD_CPU_MASK
            # for CPU core affinitization
            self._bridges[switch_name].set_db_attribute('Open_vSwitch', '.',
                                                        'other_config:pmd-cpu-mask',
                                                        settings.getValue('VSWITCH_PMD_CPU_MASK'))

    def add_phy_port(self, switch_name):
        """See IVswitch for general description

        Creates a port of type dpdk.
        The new port is named dpdk<n> where n is an integer starting from 0.
        """
        bridge = self._bridges[switch_name]
        dpdk_count = self._get_port_count('type=dpdk')
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
        # Changed dpdkvhost to dpdkvhostuser to be able to run in Qemu 2.2
        if settings.getValue('VNF').endswith('Cuse'):
            vhost_count = self._get_port_count('type=dpdkvhostcuse')
            port_name = 'dpdkvhostcuse' + str(vhost_count)
            params = ['--', 'set', 'Interface', port_name, 'type=dpdkvhostcuse']
        else:
            vhost_count = self._get_port_count('type=dpdkvhostuser')
            port_name = 'dpdkvhostuser' + str(vhost_count)
            params = ['--', 'set', 'Interface', port_name, 'type=dpdkvhostuser']

        of_port = bridge.add_port(port_name, params)

        return (port_name, of_port)

    @staticmethod
    def old_dpdk_config():
        """Checks if ovs-vswitchd uses legacy dpdk configuration via --dpdk option

        :returns: True if legacy --dpdk option is supported, otherwise it returns False
        """

        ovs_vswitchd_bin = os.path.join(settings.getValue('OVS_DIR'), 'vswitchd', 'ovs-vswitchd')
        try:
            subprocess.check_output(ovs_vswitchd_bin + r' --help | grep "\-\-dpdk"', shell=True)
            return True
        except subprocess.CalledProcessError:
            return False
