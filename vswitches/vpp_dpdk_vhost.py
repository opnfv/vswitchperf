# Copyright 2017-2018 Intel Corporation., Tieto
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

"""VSPERF VPP implementation using DPDK and vhostuser vports
"""

import os
import copy
import re
import pexpect

from src.dpdk import dpdk
from conf import settings as S
from vswitches.vswitch import IVSwitch
from tools import tasks
from tools.version import Version

# pylint: disable=too-many-public-methods
class VppDpdkVhost(IVSwitch, tasks.Process):
    """ VPP with DPDK support
    """
    _proc_name = 'vpp'
    _bridge_idx_counter = 100

    def __init__(self):
        """See IVswitch for general description
        """
        super().__init__()
        name, ext = os.path.splitext(S.getValue('LOG_FILE_VPP'))
        rename_vpplf = "{name}_{uid}{ex}".format(name=name,
                                                 uid=S.getValue(
                                                     'LOG_TIMESTAMP'),
                                                 ex=ext)
        self._logfile = os.path.join(S.getValue('LOG_DIR'), rename_vpplf)
        self._expect = r'vpp#'
        self._cmd_template = ['sudo', '-E', S.getValue('TOOLS')['vpp']]
        self._phy_ports = []
        self._virt_ports = []
        self._vpp_ctl = ['sudo', S.getValue('TOOLS')['vppctl']]

        # configure DPDK NICs
        tmp_args = copy.deepcopy(S.getValue('VSWITCH_VPP_ARGS'))
        if 'dpdk' not in tmp_args:
            tmp_args['dpdk'] = []

        # override socket-mem settings
        for tmp_arg in tmp_args['dpdk']:
            if tmp_arg.startswith('socket-mem'):
                tmp_args['dpdk'].remove(tmp_arg)
        tmp_args['dpdk'].append('socket-mem ' +
                                ','.join(S.getValue('DPDK_SOCKET_MEM')))

        # create directory for vhostuser sockets if needed
        if not os.path.exists(S.getValue('TOOLS')['ovs_var_tmp']):
            tasks.run_task(['sudo', 'mkdir', '-p',
                            S.getValue('TOOLS')['ovs_var_tmp']], self._logger)

        # configure path to the plugins
        tmp_args['plugin_path'] = S.getValue('TOOLS')['vpp_plugin_path']

        # cli sock file must be used for VPP 17.10 and newer
        if S.getValue('VSWITCH_VPP_CLI_SOCK'):
            self._vpp_ctl += ['-s', S.getValue('VSWITCH_VPP_CLI_SOCK')]
            tmp_args['unix'].append('cli-listen {}'.format(
                S.getValue('VSWITCH_VPP_CLI_SOCK')))

        mqs = int(S.getValue('VSWITCH_DPDK_MULTI_QUEUES'))
        tmp_rxqs = ''
        if mqs:
            tmp_rxqs = " {{ num-rx-queues {} }}".format(mqs)

        # configure physical ports
        for nic in S.getValue('NICS'):
            tmp_args['dpdk'].append("dev {}{}".format(nic['pci'], tmp_rxqs))
        self._vswitch_args = self._process_vpp_args(tmp_args)

    def _get_nic_info(self, key='Name'):
        """Read NIC info from VPP and return NIC details in a dictionary
           indexed by given ``key``

        :param key: Name of the key to be used for indexing result dictionary

        :returns: Dictionary with NIC infos including their PCI addresses
        """
        result = {}
        output = self.run_vppctl(['show', 'hardware', 'brief'])
        # parse output and store basic info about NICS
        ifaces = output[0].split('\n')
        keys = ifaces[0].split()
        keys.append('Pci')
        keyidx = keys.index(key)
        for iface in ifaces[1:]:
            tmpif = iface.split()
            if not tmpif:
                continue
            # get PCI address of given interface
            output = self.run_vppctl(['show', 'hardware', tmpif[1], 'detail'])
            match = re.search(r'pci address:\s*([\d:\.]+)', output[0])
            if match:
                # normalize PCI address, e.g. 0000:05:10.01 => 0000:05:10.1
                tmp_pci = match.group(1).split('.')
                tmp_pci[1] = str(int(tmp_pci[1]))
                tmpif.append('.'.join(tmp_pci))
            else:
                tmpif.append(None)
            # store only NICs with reasonable index
            if tmpif[keyidx] is not None:
                result[tmpif[keyidx]] = dict(zip(keys, tmpif))

        return result

    def _process_vpp_args(self, args):
        """Produce VPP CLI args from input dictionary ``args``
        """
        cli_args = []
        for cfg_key in args:
            cli_args.append(cfg_key)
            if isinstance(args[cfg_key], str):
                cli_args.append(args[cfg_key])
            else:
                cli_args.append("{{ {} }}".format(' '.join(args[cfg_key])))

        self._logger.debug("VPP CLI args: %s", cli_args)
        return cli_args

    def start(self):
        """Activates DPDK kernel modules and starts VPP

        :raises: pexpect.EOF, pexpect.TIMEOUT
        """
        dpdk.init()
        self._logger.info("Starting VPP...")

        self._cmd = self._cmd_template + self._vswitch_args

        try:
            tasks.Process.start(self)
            self.relinquish()
        except (pexpect.EOF, pexpect.TIMEOUT) as exc:
            self._logger.error("Exception during VPP start.")
            raise exc

        self._logger.info("VPP...Started.")

    def stop(self):
        """See IVswitch for general description

        Kills VPP and removes DPDK kernel modules.
        """
        self._logger.info("Terminating VPP...")
        self.kill()
        self._logger.info("VPP...Terminated.")
        dpdk.cleanup()

    def kill(self, signal='-15', sleep=10):
        """See IVswitch for general description

        Kills ``vpp``
        """
        if self.is_running():
            # try to get VPP pid
            output = self.run_vppctl(['show', 'version', 'verbose'])
            match = re.search(r'Current PID:\s*([0-9]+)', output[0])
            if match:
                vpp_pid = match.group(1)
                tasks.terminate_task(vpp_pid, logger=self._logger)

            # in case, that pid was not detected or sudo envelope
            # has not been terminated yet
            tasks.Process.kill(self, signal, sleep)

    def get_version(self):
        """See IVswitch for general description
        """
        versions = []
        output = self.run_vppctl(['show', 'version', 'verbose'])
        if output[1]:
            self._logger.warning("VPP version can not be read!")
            return versions

        match = re.search(r'Version:\s*(.+)', output[0])
        if match:
            versions.append(Version(S.getValue('VSWITCH'), match.group(1)))

        match = re.search(r'DPDK Version:\s*DPDK (.+)', output[0])
        if match:
            versions.append(Version('dpdk', match.group(1)))

        return versions

    def add_switch(self, switch_name, dummy_params=None):
        """See IVswitch for general description
        """
        # pylint: disable=unused-argument
        if switch_name in self._switches:
            self._logger.warning("switch %s already exists...", switch_name)
        else:
            self._switches[switch_name] = self._bridge_idx_counter
            self._bridge_idx_counter += 1

    def del_switch(self, switch_name):
        """See IVswitch for general description
        """
        if switch_name in self._switches:
            del self._switches[switch_name]

    def add_phy_port(self, dummy_switch_name):
        """See IVswitch for general description
        :raises: RuntimeError
        """
        # pylint: disable=unused-argument
        # get list of physical interfaces with PCI addresses
        vpp_nics = self._get_nic_info(key='Pci')
        # check if there are any NICs left
        if len(self._phy_ports) >= len(S.getValue('NICS')):
            raise RuntimeError("Can't add phy port! There are only {} ports defined "
                               "by WHITELIST_NICS parameter!".format(len(S.getValue('NICS'))))

        nic = S.getValue('NICS')[len(self._phy_ports)]
        if not nic['pci'] in vpp_nics:
            raise RuntimeError('VPP cannot access nic with PCI address: {}'.format(nic['pci']))
        nic_name = vpp_nics[nic['pci']]['Name']
        self._phy_ports.append(nic_name)
        self.run_vppctl(['set', 'int', 'state', nic_name, 'up'])
        return (nic_name, vpp_nics[nic['pci']]['Idx'])

    def add_vport(self, dummy_switch_name):
        """See IVswitch for general description
        """
        # pylint: disable=unused-argument
        socket_name = S.getValue('TOOLS')['ovs_var_tmp'] + 'dpdkvhostuser' + str(len(self._virt_ports))
        if S.getValue('VSWITCH_VHOSTUSER_SERVER_MODE'):
            mode = ['server']
        else:
            mode = []
        output = self.run_vppctl(['create', 'vhost-user', 'socket', socket_name] + mode +
                                 S.getValue('VSWITCH_VPP_VHOSTUSER_ARGS'))
        if output[0].find('returned') >= 0:
            raise RuntimeError('VPP VhostUser interface cannot be created.')
        nic_name = output[0].strip()
        self._virt_ports.append(nic_name)
        self.run_vppctl(['set', 'int', 'state', nic_name, 'up'])
        return (nic_name, None)

    def del_port(self, switch_name, port_name):
        """See IVswitch for general description
        """
        if port_name in self._phy_ports:
            self.run_vppctl(['set', 'int', 'state', port_name, 'down'])
            self._phy_ports.remove(port_name)
        elif port_name in self._virt_ports:
            self.run_vppctl(['set', 'int', 'state', port_name, 'down'])
            self.run_vppctl(['delete', 'vhost-user', port_name])
            self._virt_ports.remove(port_name)
        else:
            self._logger.warning("Port %s is not configured.", port_name)

    def add_l2patch(self, port1, port2):
        """Create l2patch connection between given ports
        """
        self.run_vppctl(['test', 'l2patch', 'rx', port1, 'tx', port2])

    def add_xconnect(self, port1, port2):
        """Create l2patch connection between given ports
        """
        self.run_vppctl(['set', 'interface', 'l2', 'xconnect', port1, port2])

    def add_bridge(self, switch_name, port1, port2):
        """Add given ports to bridge ``switch_name``
        """
        self.run_vppctl(['set', 'interface', 'l2', 'bridge', port1,
                         str(self._switches[switch_name])])
        self.run_vppctl(['set', 'interface', 'l2', 'bridge', port2,
                         str(self._switches[switch_name])])

    def add_connection(self, switch_name, port1, port2, traffic=None):
        """See IVswitch for general description

        :raises: RuntimeError
        """
        if traffic:
            self._logger.warning("VPP add_connection() does not support 'traffic' options.")

        mode = S.getValue('VSWITCH_VPP_L2_CONNECT_MODE')
        if mode == 'l2patch':
            self.add_l2patch(port1, port2)
        elif mode == 'xconnect':
            self.add_xconnect(port1, port2)
        elif mode == 'bridge':
            self.add_bridge(switch_name, port1, port2)
        else:
            raise RuntimeError('VPP: Unsupported l2 connection mode detected %s' % mode)

    def del_l2patch(self, port1, port2):
        """Remove l2patch connection between given ports

        :param port1: port to be used in connection
        :param port2: port to be used in connection
        """
        self.run_vppctl(['test', 'l2patch', 'rx', port1, 'tx', port2, 'del'])

    def del_xconnect(self, port1, port2):
        """Remove xconnect connection between given ports
        """
        self.run_vppctl(['set', 'interface', 'l3', port1])
        self.run_vppctl(['set', 'interface', 'l3', port2])

    def del_bridge(self, _dummy_switch_name, port1, port2):
        """Remove given ports from the bridge
        """
        self.run_vppctl(['set', 'interface', 'l3', port1])
        self.run_vppctl(['set', 'interface', 'l3', port2])

    def del_connection(self, switch_name, port1=None, port2=None):
        """See IVswitch for general description

        :raises: RuntimeError
        """
        if port1 and port2:
            mode = S.getValue('VSWITCH_VPP_L2_CONNECT_MODE')
            if mode == 'l2patch':
                self.del_l2patch(port1, port2)
            elif mode == 'xconnect':
                self.del_xconnect(port1, port2)
            elif mode == 'bridge':
                self.del_bridge(switch_name, port1, port2)
            else:
                raise RuntimeError('VPP: Unsupported l2 connection mode detected %s' % mode)

    def dump_l2patch(self):
        """Dump l2patch connections
        """
        self.run_vppctl(['show', 'l2patch'])

    def dump_xconnect(self):
        """Dump l2 xconnect connections
        """
        self.run_vppctl(['show', 'mode'] + self._phy_ports + self._virt_ports)

    def dump_bridge(self, switch_name):
        """Show bridge details

        :param switch_name: switch on which to operate
        """
        self.run_vppctl(['show', 'bridge-domain', str(self._switches[switch_name]), 'int'])

    def dump_connections(self, switch_name):
        """See IVswitch for general description

        :raises: RuntimeError
        """
        mode = S.getValue('VSWITCH_VPP_L2_CONNECT_MODE')
        if mode == 'l2patch':
            self.dump_l2patch()
        elif mode == 'xconnect':
            self.dump_xconnect()
        elif mode == 'bridge':
            self.dump_bridge(switch_name)
        else:
            raise RuntimeError('VPP: Unsupported l2 connection mode detected %s' % mode)

    def run_vppctl(self, args, check_error=False):
        """Run ``vppctl`` with supplied arguments.

        :param args: Arguments to pass to ``vppctl``
        :param check_error: Throw exception on error

        :return: None
        """
        cmd = self._vpp_ctl + args
        return tasks.run_task(cmd, self._logger, 'Running vppctl...', check_error)

    #
    # Validate methods
    #
    def validate_add_switch(self, _dummy_result, switch_name, _dummy_params=None):
        """Validate - Create a new logical switch with no ports
        """
        return switch_name in self._switches

    def validate_del_switch(self, _dummy_result, switch_name):
        """Validate removal of switch
        """
        return not self.validate_add_switch(_dummy_result, switch_name)

    def validate_add_phy_port(self, result, _dummy_switch_name):
        """ Validate that physical port was added to bridge.
        """
        return result[0] in self._phy_ports

    def validate_add_vport(self, result, _dummy_switch_name):
        """ Validate that virtual port was added to bridge.
        """
        return result[0] in self._virt_ports

    def validate_del_port(self, _dummy_result, _dummy_switch_name, port_name):
        """ Validate that port_name was removed from bridge.
        """
        return not (port_name in self._phy_ports or port_name in self._virt_ports)

    # pylint: disable=no-self-use
    def validate_add_connection(self, _dummy_result, _dummy_switch_name, _dummy_port1,
                                _dummy_port2, _dummy_traffic=None):
        """ Validate that connection was added
        """
        return True

    def validate_del_connection(self, _dummy_result, _dummy_switch_name, _dummy_port1,
                                _dummy_port2):
        """ Validate that connection was deleted
        """
        return True

    def validate_dump_connections(self, _dummy_result, _dummy_switch_name):
        """ Validate dump connections call
        """
        return True

    def validate_run_vppctl(self, result, _dummy_args, _dummy_check_error=False):
        """validate execution of ``vppctl`` with supplied arguments.
        """
        # there shouldn't be any stderr
        return not result[1]

    #
    # Non implemented methods
    #
    def add_route(self, switch_name, network, destination):
        """See IVswitch for general description
        """
        raise NotImplementedError()

    def set_tunnel_arp(self, ip_addr, mac_addr, switch_name):
        """See IVswitch for general description
        """
        raise NotImplementedError()

    def add_tunnel_port(self, switch_name, remote_ip, tunnel_type='vxlan', params=None):
        """See IVswitch for general description
        """
        raise NotImplementedError()

    def get_ports(self, switch_name):
        """See IVswitch for general description
        """
        raise NotImplementedError()
