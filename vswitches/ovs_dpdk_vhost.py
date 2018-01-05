# Copyright 2015-2017 Intel Corporation.
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

from src.ovs import OFBridge
from src.dpdk import dpdk
from conf import settings as S
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

        vswitchd_args = []

        # legacy DPDK configuration through --dpdk option of vswitchd
        if self.old_dpdk_config():
            # override socket-mem settings
            tmp_dpdk_args = S.getValue('VSWITCHD_DPDK_ARGS')
            for tmp_arg in tmp_dpdk_args:
                if tmp_arg.startswith('--socket-mem'):
                    tmp_dpdk_args.remove(tmp_arg)
            tmp_dpdk_args += ['--socket-mem ' + ','.join(S.getValue('DPDK_SOCKET_MEM'))]
            vswitchd_args = ['--dpdk'] + tmp_dpdk_args
            # add dpdk args to generic ovs-vswitchd settings
            if self._vswitchd_args:
                self._vswitchd_args = vswitchd_args + ['--'] + self._vswitchd_args
            else:
                self._vswitchd_args = vswitchd_args

    def configure(self):
        """ Configure vswitchd DPDK options through ovsdb if needed
        """
        dpdk_config = S.getValue('VSWITCHD_DPDK_CONFIG')
        if dpdk_config and not self.old_dpdk_config():
            # override socket-mem settings
            dpdk_config['dpdk-socket-mem'] = ','.join(S.getValue('DPDK_SOCKET_MEM'))
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
        # old style OVS <= 2.5.0 multi-queue enable
        if S.getValue('OVS_OLD_STYLE_MQ') and \
                int(S.getValue('VSWITCH_DPDK_MULTI_QUEUES')):
            tmp_br = OFBridge(timeout=-1)
            tmp_br.set_db_attribute(
                'Open_vSwitch', '.', 'other_config:' +
                'n-dpdk-rxqs', S.getValue('VSWITCH_DPDK_MULTI_QUEUES'))

    def stop(self):
        """See IVswitch for general description

        Kills ovsdb and vswitchd and removes DPDK kernel modules.
        """

        super(OvsDpdkVhost, self).stop()
        dpdk.cleanup()

    def add_switch(self, switch_name, params=None):
        """See IVswitch for general description
        """
        switch_params = ['--', 'set', 'bridge', switch_name, 'datapath_type=netdev']
        if params:
            switch_params = switch_params + params

        super(OvsDpdkVhost, self).add_switch(switch_name, switch_params)
        if S.getValue('VSWITCH_AFFINITIZATION_ON') == 1:
            # Sets the PMD core mask to VSWITCH_PMD_CPU_MASK
            # for CPU core affinitization
            self._bridges[switch_name].set_db_attribute('Open_vSwitch', '.',
                                                        'other_config:pmd-cpu-mask',
                                                        S.getValue('VSWITCH_PMD_CPU_MASK'))

    def add_phy_port(self, switch_name):
        """See IVswitch for general description

        Creates a port of type dpdk.
        The new port is named dpdk<n> where n is an integer starting from 0.
        """
        _nics = S.getValue('NICS')
        bridge = self._bridges[switch_name]
        dpdk_count = self._get_port_count('type=dpdk')
        if dpdk_count == len(_nics):
            raise RuntimeError("Can't add phy port! There are only {} ports defined "
                               "by WHITELIST_NICS parameter!".format(len(_nics)))
        port_name = 'dpdk' + str(dpdk_count)
        # PCI info. Please note there must be no blank space, eg must be
        # like 'options:dpdk-devargs=0000:06:00.0'
        nic_pci = 'options:dpdk-devargs=' + _nics[dpdk_count]['pci']
        params = ['--', 'set', 'Interface', port_name, 'type=dpdk', nic_pci]
        # multi-queue enable

        if int(S.getValue('VSWITCH_DPDK_MULTI_QUEUES')) and \
                not S.getValue('OVS_OLD_STYLE_MQ'):
            params += ['options:n_rxq={}'.format(
                S.getValue('VSWITCH_DPDK_MULTI_QUEUES'))]
        if S.getValue('VSWITCH_JUMBO_FRAMES_ENABLED'):
            params += ['mtu_request={}'.format(
                S.getValue('VSWITCH_JUMBO_FRAMES_SIZE'))]
        of_port = bridge.add_port(port_name, params)
        return (port_name, of_port)

    def add_vport(self, switch_name):
        """See IVswitch for general description

        Creates a port of type dpdkvhost
        The new port is named dpdkvhost<n> where n is an integer starting
        from 0
        """
        bridge = self._bridges[switch_name]

        if S.getValue('VSWITCH_VHOSTUSER_SERVER_MODE'):
            nic_type = 'dpdkvhostuser'
        else:
            nic_type = 'dpdkvhostuserclient'

        vhost_count = self._get_port_count('type={}'.format(nic_type))
        port_name = nic_type + str(vhost_count)
        params = ['--', 'set', 'Interface', port_name, 'type={}'.format(nic_type)]
        if not S.getValue('VSWITCH_VHOSTUSER_SERVER_MODE'):
            params += ['--', 'set', 'Interface', port_name, 'options:vhost-server-path='
                       '{}{}'.format(S.getValue('TOOLS')['ovs_var_tmp'], port_name)]
        if S.getValue('VSWITCH_JUMBO_FRAMES_ENABLED'):
            params += ['mtu_request={}'.format(
                S.getValue('VSWITCH_JUMBO_FRAMES_SIZE'))]
        of_port = bridge.add_port(port_name, params)

        return (port_name, of_port)

    @staticmethod
    def old_dpdk_config():
        """Checks if ovs-vswitchd uses legacy dpdk configuration via --dpdk option

        :returns: True if legacy --dpdk option is supported, otherwise it returns False
        """

        ovs_vswitchd_bin = S.getValue('TOOLS')['ovs-vswitchd']
        try:
            subprocess.check_output(ovs_vswitchd_bin + r' --help | grep "\-\-dpdk"', shell=True)
            return True
        except subprocess.CalledProcessError:
            return False

    def add_connection(self, switch_name, port1, port2, bidir=False):
        """See IVswitch for general description
        """
        raise NotImplementedError()

    def del_connection(self, switch_name, port1, port2, bidir=False):
        """See IVswitch for general description
        """
        raise NotImplementedError()

    def dump_connections(self, switch_name):
        """See IVswitch for general description
        """
        raise NotImplementedError()
