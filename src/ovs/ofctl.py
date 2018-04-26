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

"""Wrapper for an OVS bridge for convenient use of ``ovs-vsctl`` and
``ovs-ofctl`` on it.

Much of this code is based on ``ovs-lib.py`` from Open Stack:

https://github.com/openstack/neutron/blob/6eac1dc99124ca024d6a69b3abfa3bc69c735667/neutron/agent/linux/ovs_lib.py
"""
import logging
import string
import re
import netaddr

from tools import tasks
from conf import settings as S

_OVS_BRIDGE_NAME = S.getValue('VSWITCH_BRIDGE_NAME')
_OVS_CMD_TIMEOUT = S.getValue('OVS_CMD_TIMEOUT')

_CACHE_FILE_NAME = '/tmp/vsperf_flows_cache'

# only simple regex is used; validity of IPv4 is not checked by regex
_IPV4_REGEX = r"([0-9]{1,3}(\.[0-9]{1,3}){3}(\/[0-9]{1,2})?)"

class OFBase(object):
    """Add/remove/show datapaths using ``ovs-ofctl``.
    """
    def __init__(self, timeout=_OVS_CMD_TIMEOUT):
        """Initialise logger.

        :param timeout: Timeout to be used for each command

        :returns: None
        """
        self.logger = logging.getLogger(__name__)
        self.timeout = timeout

    # helpers

    def run_vsctl(self, args, check_error=False):
        """Run ``ovs-vsctl`` with supplied arguments.

        In case that timeout is set to -1, then ovs-vsctl
        will be called with --no-wait option.

        :param args: Arguments to pass to ``ovs-vsctl``
        :param check_error: Throw exception on error

        :return: None
        """
        if self.timeout == -1:
            cmd = ['sudo', S.getValue('TOOLS')['ovs-vsctl'], '--no-wait'] + \
                  S.getValue('OVS_VSCTL_ARGS') + args
        else:
            cmd = ['sudo', S.getValue('TOOLS')['ovs-vsctl'], '--timeout',
                   str(self.timeout)] + S.getValue('OVS_VSCTL_ARGS') + args
        return tasks.run_task(
            cmd, self.logger, 'Running ovs-vsctl...', check_error)


    def run_appctl(self, args, check_error=False):
        """Run ``ovs-appctl`` with supplied arguments.

        :param args: Arguments to pass to ``ovs-appctl``
        :param check_error: Throw exception on error

        :return: None
        """
        cmd = ['sudo', S.getValue('TOOLS')['ovs-appctl'],
               '--timeout',
               str(self.timeout)] + S.getValue('OVS_APPCTL_ARGS') + args
        return tasks.run_task(
            cmd, self.logger, 'Running ovs-appctl...', check_error)


    # datapath management

    def add_br(self, br_name=_OVS_BRIDGE_NAME, params=None):
        """Add datapath.

        :param br_name: Name of bridge

        :return: Instance of :class OFBridge:
        """
        if params is None:
            params = []

        self.logger.debug('add bridge')
        self.run_vsctl(['add-br', br_name]+params)

        return OFBridge(br_name, self.timeout)

    def del_br(self, br_name=_OVS_BRIDGE_NAME):
        """Delete datapath.

        :param br_name: Name of bridge

        :return: None
        """
        self.logger.debug('delete bridge')
        self.run_vsctl(['del-br', br_name])

    # Route and ARP functions

    def add_route(self, network, destination):
        """Add route to tunneling routing table.

        :param network: Network
        :param destination: Gateway

        :return: None
        """
        self.logger.debug('add ovs/route')
        self.run_appctl(['ovs/route/add', network, destination])


    def set_tunnel_arp(self, ip_addr, mac_addr, br_name=_OVS_BRIDGE_NAME):
        """Add OVS arp entry for tunneling

        :param ip: IP of bridge
        :param mac_addr: MAC address of the bridge
        :param br_name: Name of the bridge

        :return: None
        """
        self.logger.debug('tnl/arp/set')
        self.run_appctl(['tnl/arp/set', br_name, ip_addr, mac_addr])


class OFBridge(OFBase):
    """Control a bridge instance using ``ovs-vsctl`` and ``ovs-ofctl``.
    """
    def __init__(self, br_name=_OVS_BRIDGE_NAME, timeout=_OVS_CMD_TIMEOUT):
        """Initialise bridge.

        :param br_name: Bridge name
        :param timeout: Timeout to be used for each command

        :returns: None
        """
        super(OFBridge, self).__init__(timeout)
        self.br_name = br_name
        self._ports = {}
        self._cache_file = None

    # helpers

    def run_ofctl(self, args, check_error=False, timeout=None):
        """Run ``ovs-ofctl`` with supplied arguments.

        :param args: Arguments to pass to ``ovs-ofctl``
        :param check_error: Throw exception on error

        :return: None
        """
        tmp_timeout = self.timeout if timeout is None else timeout
        cmd = ['sudo', S.getValue('TOOLS')['ovs-ofctl'], '--timeout',
               str(tmp_timeout)] + S.getValue('OVS_OFCTL_ARGS') + args
        return tasks.run_task(
            cmd, self.logger, 'Running ovs-ofctl...', check_error)

    def create(self, params=None):
        """Create bridge.
        """
        if params is None:
            params = []

        self.logger.debug('create bridge')
        self.add_br(self.br_name, params=params)

    def destroy(self):
        """Destroy bridge.
        """
        self.logger.debug('destroy bridge')
        self.del_br(self.br_name)

    def reset(self):
        """Reset bridge.
        """
        self.logger.debug('reset bridge')
        self.destroy()
        self.create()

    # port management

    def add_port(self, port_name, params):
        """Add port to bridge.

        :param port_name: Name of port
        :param params: Additional list of parameters to add-port

        :return: OpenFlow port number for the port
        """
        self.logger.debug('add port')
        self.run_vsctl(['add-port', self.br_name, port_name]+params)

        # This is how port number allocation works currently
        # This possibly will not work correctly if there are port deletions
        # in between
        of_port = len(self._ports) + 1
        self._ports[port_name] = (of_port, params)
        return of_port

    def del_port(self, port_name):
        """Remove port from bridge.

        :param port_name: Name of port

        :return: None
        """
        self.logger.debug('delete port')
        self.run_vsctl(['del-port', self.br_name, port_name])
        self._ports.pop(port_name)

    def set_db_attribute(self, table_name, record, column, value):
        """Set database attribute.

        :param table_name: Name of table
        :param record: Name of record
        :param column: Name of column
        :param value: Value to set

        :return: None
        """
        self.logger.debug('set attribute')
        self.run_vsctl(['set', table_name, record, '%s=%s' % (column, value)])

    def get_ports(self):
        """Get the ports of this bridge

        Structure of the returned ports dictionary is
        'portname': (openflow_port_number, extra_parameters)

        Example:
        ports = {
            'dpdkport0':
                (1, ['--', 'set', 'Interface', 'dpdkport0', 'type=dpdk']),
            'dpdkvhostport0':
                (2, ['--', 'set', 'Interface', 'dpdkvhostport0',
                     'type=dpdkvhost'])
        }

        :return: Dictionary of ports
        """
        return self._ports

    def clear_db_attribute(self, table_name, record, column):
        """Clear database attribute.

        :param table_name: Name of table
        :param record: Name of record
        :param column: Name of column

        :return: None
        """
        self.logger.debug('clear attribute')
        self.run_vsctl(['clear', table_name, record, column])

    # flow mangement

    def add_flow(self, flow, cache='off'):
        """Add flow to bridge.

        :param flow: Flow description as a dictionary
        For flow dictionary structure, see function flow_key

        :return: None
        """
        # insert flows from cache into OVS if needed
        if cache == 'flush':
            if self._cache_file is None:
                self.logger.error('flow cache flush called, but nothing is cached')
                return
            self.logger.debug('flows cached in %s will be added to the bridge', _CACHE_FILE_NAME)
            self._cache_file.close()
            self._cache_file = None
            self.run_ofctl(['add-flows', self.br_name, _CACHE_FILE_NAME], timeout=600)
            return

        if not flow.get('actions'):
            self.logger.error('add flow requires actions')
            return

        _flow_key = flow_key(flow)
        self.logger.debug('key : %s', _flow_key)

        # insert flow to the cache or OVS
        if cache == 'on':
            # create and open cache file if needed
            if self._cache_file is None:
                self._cache_file = open(_CACHE_FILE_NAME, 'w')
            self._cache_file.write(_flow_key + '\n')
        else:
            self.run_ofctl(['add-flow', self.br_name, _flow_key])

    def del_flow(self, flow):
        """Delete flow from bridge.

        :param flow: Flow description as a dictionary
        For flow dictionary structure, see function flow_key
        flow=None will delete all flows

        :return: None
        """
        self.logger.debug('delete flow')
        _flow_key = flow_key(flow)
        self.logger.debug('key : %s', _flow_key)
        self.run_ofctl(['del-flows', self.br_name, _flow_key])

    def del_flows(self):
        """Delete all flows from bridge.
        """
        self.logger.debug('delete flows')
        self.run_ofctl(['del-flows', self.br_name])

    def dump_flows(self):
        """Dump all flows from bridge.
        """
        self.logger.debug('dump flows')
        self.run_ofctl(['dump-flows', self.br_name], timeout=120)

    def set_stp(self, enable=True):
        """
        Set stp status
        :param enable: Boolean to enable or disable stp
        :return: None
        """
        self.logger.debug(
            'Setting stp on bridge to %s', 'on' if enable else 'off')
        self.run_vsctl(
            ['set', 'Bridge', self.br_name, 'stp_enable={}'.format(
                'true' if enable else 'false')])

    def set_rstp(self, enable=True):
        """
        Set rstp status
        :param enable: Boolean to enable or disable rstp
        :return: None
        """
        self.logger.debug(
            'Setting rstp on bridge to %s', 'on' if enable else 'off')
        self.run_vsctl(
            ['set', 'Bridge', self.br_name, 'rstp_enable={}'.format(
                'true' if enable else 'false')])

    def bridge_info(self):
        """
        Get bridge info
        :return: Returns bridge info from list bridge command
        """
        return self.run_vsctl(['list', 'bridge', self.br_name])

#
# helper functions
#

def flow_key(flow):
    """Model a flow key string for ``ovs-ofctl``.

    Syntax taken from ``ovs-ofctl`` manpages:
        http://openvswitch.org/cgi-bin/ovsman.cgi?page=utilities%2Fovs-ofctl.8

    Example flow dictionary:
    flow = {
        'in_port': '1',
        'idle_timeout': '0',
        'actions': ['output:3']
    }

    :param flow: Flow description as a dictionary

    :return: String
    :rtype: str
    """
    _flow_add_key = string.Template('${fields},action=${actions}')
    _flow_del_key = string.Template('${fields}')

    field_params = []

    user_params = (x for x in list(flow.items()) if x[0] != 'actions')
    for (key, default) in user_params:
        field_params.append('%(field)s=%(value)s' %
                            {'field': key, 'value': default})

    field_params_str = ','.join(field_params)

    _flow_key_param = {
        'fields': field_params_str,
    }

    # no actions == delete key
    if 'actions' in flow:
        _flow_key_param['actions'] = ','.join(flow['actions'])

        flow_str = _flow_add_key.substitute(_flow_key_param)
    else:
        flow_str = _flow_del_key.substitute(_flow_key_param)

    return flow_str

def flow_match(flow_dump, flow_src):
    """ Compares two flows

    :param flow_dump: string - a string with flow obtained by ovs-ofctl dump-flows
    :param flow_src: string - a string with flow obtained by call of flow_key()

    :return: boolean
    """
    # perform unifications on both source and destination flows
    flow_dump = flow_dump.replace('actions=', 'action=')
    flow_src = flow_src.replace('actions=', 'action=')
    # For complex flows the output of "ovs-ofctl dump-flows" can use the
    # shorthand notation.
    # eg if we set a flow with constraints on UDP ports like in the following
    # {'dl_type': '0x0800', 'nw_proto': '17', 'in_port': '1', 'udp_dst': '0', 'actions': ['output:2']}
    # dump-flows output can combine the first 2 constraints into 'udp' and translate
    # 'udp_dst' into 'tp_dst' like
    # "udp,in_port=1,tp_dst=0 actions=output:2".
    # So the next replacements are needed.
    flow_dump = flow_dump.replace('ip', 'dl_type=0x0800')
    flow_dump = flow_dump.replace('tcp', 'nw_proto=6,dl_type=0x0800')
    flow_dump = flow_dump.replace('udp', 'nw_proto=17,dl_type=0x0800')
    flow_src = flow_src.replace('udp_src', 'tp_src')
    flow_src = flow_src.replace('udp_dst', 'tp_dst')
    flow_src = flow_src.replace('tcp_src', 'tp_src')
    flow_src = flow_src.replace('tcp_dst', 'tp_dst')
    flow_src = flow_src.replace('0x800', '0x0800')

    # modify IPv4 CIDR to real network addresses
    for ipv4_cidr in re.findall(_IPV4_REGEX, flow_src):
        if ipv4_cidr[2]:
            tmp_cidr = str(netaddr.IPNetwork(ipv4_cidr[0]).cidr)
            flow_src = flow_src.replace(ipv4_cidr[0], tmp_cidr)

    # split flow strings into lists of comparable elements
    flow_dump_list = re.findall(r"[\w.:=()/]+", flow_dump)
    flow_src_list = re.findall(r"[\w.:=()/]+", flow_src)

    # check if all items from source flow are present in dump flow
    flow_src_ctrl = list(flow_src_list)
    for rule in flow_src_list:
        if rule in flow_dump_list:
            flow_src_ctrl.remove(rule)
    return True if not flow_src_ctrl else False
