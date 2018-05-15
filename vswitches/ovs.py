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

"""VSPERF Open vSwitch base class
"""

import os
import re
import time
import datetime
import random
import socket
import netaddr
import pexpect

from conf import settings
from src.ovs import OFBridge, flow_key, flow_match
from vswitches.vswitch import IVSwitch
from tools import tasks
from tools.module_manager import ModuleManager

# enable caching of flows if their number exceeds given limit
_CACHE_FLOWS_LIMIT = 10

# pylint: disable=too-many-public-methods
class IVSwitchOvs(IVSwitch, tasks.Process):
    """Open vSwitch base class implementation

    The method docstrings document only considerations specific to this
    implementation. For generic information of the nature of the methods,
    see the interface.
    """
    _proc_name = 'ovs-vswitchd'

    def __init__(self):
        """See IVswitch for general description
        """
        super().__init__()
        self._logfile = os.path.join(settings.getValue('LOG_DIR'),
                                     settings.getValue('LOG_FILE_VSWITCHD'))
        self._ovsdb_pidfile_path = os.path.join(settings.getValue('TOOLS')['ovs_var_tmp'],
                                                "ovsdb-server.pid")
        self._vswitchd_pidfile_path = os.path.join(settings.getValue('TOOLS')['ovs_var_tmp'],
                                                   "{}.pid".format(self._proc_name))
        # sign '|' must be escaped or avoided, otherwise it is handled as 'or' by regex
        self._expect = r'bridge.INFO.{}'.format(self._proc_name)
        self._vswitchd_args = ['--pidfile=' + self._vswitchd_pidfile_path,
                               '--overwrite-pidfile', '--log-file=' + self._logfile]
        self._cmd_template = ['sudo', '-E', settings.getValue('TOOLS')['ovs-vswitchd']]
        self._module_manager = ModuleManager()
        self._flow_template = settings.getValue('OVS_FLOW_TEMPLATE').copy()
        self._flow_actions = ['output:{}']

        # if routing tables are enabled, then flows should go into table 1
        # see design document for details about Routing Tables feature
        if settings.getValue('OVS_ROUTING_TABLES'):
            # flows should be added into table 1
            self._flow_template.update({'table':'1', 'priority':'1'})
            # and chosen port will be propagated via metadata
            self._flow_actions = ['write_actions(output:{})',
                                  'write_metadata:{}',
                                  'goto_table:2']

    def start(self):
        """ Start ``ovsdb-server`` and ``ovs-vswitchd`` instance.

        :raises: pexpect.EOF, pexpect.TIMEOUT
        """
        self._logger.info("Starting vswitchd...")

        # insert kernel modules if required
        if 'vswitch_modules' in settings.getValue('TOOLS'):
            self._module_manager.insert_modules(settings.getValue('TOOLS')['vswitch_modules'])

        self._cmd = self._cmd_template + self._vswitchd_args

        # DB must be started before vswitchd
        self._reset_ovsdb()
        self._start_ovsdb()

        # DB must be up before vswitchd config is altered or vswitchd started
        time.sleep(3)

        self.configure()

        try:
            tasks.Process.start(self)
            self.relinquish()
        except (pexpect.EOF, pexpect.TIMEOUT) as exc:
            self._logger.error("Exception during VSwitch start.")
            self._kill_ovsdb()
            raise exc

        self._logger.info("Vswitchd...Started.")

    def restart(self):
        """ Restart ``ovs-vswitchd`` instance. ``ovsdb-server`` is not restarted.

        :raises: pexpect.EOF, pexpect.TIMEOUT
        """
        self._logger.info("Restarting vswitchd...")
        if os.path.isfile(self._vswitchd_pidfile_path):
            self._logger.info('Killing ovs-vswitchd...')
            with open(self._vswitchd_pidfile_path, "r") as pidfile:
                vswitchd_pid = pidfile.read().strip()
                tasks.terminate_task(vswitchd_pid, logger=self._logger)

        try:
            tasks.Process.start(self)
            self.relinquish()
        except (pexpect.EOF, pexpect.TIMEOUT) as exc:
            self._logger.error("Exception during VSwitch start.")
            self._kill_ovsdb()
            raise exc
        self._logger.info("Vswitchd...Started.")

    def configure(self):
        """ Configure vswitchd through ovsdb if needed
        """
        pass

    # Method could be a function
    # pylint: disable=no-self-use
    def get_version(self):
        """See IVswitch for general description
        """
        # OVS version can be read offline
        return []

    def stop(self):
        """See IVswitch for general description
        """
        for switch_name in list(self._switches):
            self.del_switch(switch_name)
        self._logger.info("Terminating vswitchd...")
        self.kill()
        self._switches = {}
        self._logger.info("Vswitchd...Terminated.")

    def add_switch(self, switch_name, params=None):
        """See IVswitch for general description
        """
        # create and configure new ovs bridge and delete all default flows
        bridge = OFBridge(switch_name)
        bridge.create(params)
        bridge.del_flow({})
        bridge.set_db_attribute('Open_vSwitch', '.',
                                'other_config:max-idle',
                                settings.getValue('VSWITCH_FLOW_TIMEOUT'))
        self._switches[switch_name] = bridge
        if settings.getValue('OVS_ROUTING_TABLES'):
            # table#0 - flows designed to force 5 & 13 tuple matches go here
            flow = {'table':'0', 'priority':'1', 'actions': ['goto_table:1']}
            bridge.add_flow(flow)

            # table#1 - flows to route packets between ports goes here. The
            # chosen port is communicated to subsequent tables by setting the
            # metadata value to the egress port number
            #
            # A placeholder - flows are added into this table by deployments
            #                 or by TestSteps via add_connection() method

            # table#2 - frame modification table. Frame modification flow rules are
            # isolated in this table so that they can be turned on or off
            # without affecting the routing or tuple-matching flow rules.
            flow = {'table':'2', 'priority':'1', 'actions': ['goto_table:3']}
            bridge.add_flow(flow)

            # table#3 - egress table
            # (NOTE) Billy O'Mahony - the drop action here actually required in
            # order to egress the packet. This is the subject of a thread on
            # ovs-discuss 2015-06-30.
            flow = {'table':'3', 'priority':'1', 'actions': ['drop']}
            bridge.add_flow(flow)

    def del_switch(self, switch_name):
        """See IVswitch for general description
        """
        bridge = self._switches[switch_name]
        for port in list(bridge.get_ports()):
            bridge.del_port(port)
        self._switches.pop(switch_name)
        bridge.destroy()

    def add_phy_port(self, switch_name):
        """See IVswitch for general description
        """
        raise NotImplementedError

    def add_vport(self, switch_name):
        """See IVswitch for general description
        """
        raise NotImplementedError

    def add_veth_pair_port(self, switch_name=None, remote_switch_name=None,
                           local_opts=None, remote_opts=None):
        """Creates veth-pair port between 'switch_name' and 'remote_switch_name'

        """
        if switch_name is None or remote_switch_name is None:
            return None

        bridge = self._switches[switch_name]
        remote_bridge = self._switches[remote_switch_name]
        pcount = str(self._get_port_count('type=patch'))
        # NOTE ::: What if interface name longer than allowed width??
        local_port_name = switch_name + '-' + remote_switch_name + '-' + pcount
        remote_port_name = remote_switch_name + '-' + switch_name + '-' + pcount
        local_params = ['--', 'set', 'Interface', local_port_name,
                        'type=patch',
                        'options:peer=' + remote_port_name]
        remote_params = ['--', 'set', 'Interface', remote_port_name,
                         'type=patch',
                         'options:peer=' + local_port_name]

        if local_opts is not None:
            local_params = local_params + local_opts

        if remote_opts is not None:
            remote_params = remote_params + remote_opts

        local_of_port = bridge.add_port(local_port_name, local_params)
        remote_of_port = remote_bridge.add_port(remote_port_name, remote_params)
        return [(local_port_name, local_of_port),
                (remote_port_name, remote_of_port)]

    def add_tunnel_port(self, switch_name, remote_ip, tunnel_type='vxlan', params=None):
        """Creates tunneling port
        """
        bridge = self._switches[switch_name]
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
        bridge = self._switches[switch_name]
        ports = list(bridge.get_ports().items())
        return [(name, of_port) for (name, (of_port, _)) in ports]

    def del_port(self, switch_name, port_name):
        """See IVswitch for general description
        """
        bridge = self._switches[switch_name]
        bridge.del_port(port_name)

    def add_flow(self, switch_name, flow, cache='off'):
        """See IVswitch for general description
        """
        bridge = self._switches[switch_name]
        bridge.add_flow(flow, cache=cache)

    def del_flow(self, switch_name, flow=None):
        """See IVswitch for general description
        """
        flow = flow or {}
        bridge = self._switches[switch_name]
        bridge.del_flow(flow)

    def dump_flows(self, switch_name):
        """See IVswitch for general description
        """
        bridge = self._switches[switch_name]
        bridge.dump_flows()

    def _prepare_flows(self, operation, switch_name, port1, port2, traffic=None):
        """Prepare flows for add_connection, del_connection and validate methods
           It returns a list of flows based on given parameters.
        """
        flows = []
        if operation == 'add':
            bridge = self._switches[switch_name]
            flow = self._flow_template.copy()
            actions = [action.format(bridge.get_ports()[port2][0]) for action in self._flow_actions]
            flow.update({'in_port': bridge.get_ports()[port1][0], 'actions': actions})
            # check if stream specific connection(s) should be crated for multistream feature
            if traffic and traffic['pre_installed_flows'].lower() == 'yes':
                for stream in range(traffic['multistream']):
                    tmp_flow = flow.copy()
                    # update flow based on trafficgen settings
                    if traffic['stream_type'] == 'L2':
                        dst_mac_value = netaddr.EUI(traffic['l2']['dstmac']).value
                        tmp_mac = netaddr.EUI(dst_mac_value + stream)
                        tmp_mac.dialect = netaddr.mac_unix_expanded
                        tmp_flow.update({'dl_dst':tmp_mac})
                    elif traffic['stream_type'] == 'L3':
                        dst_ip_value = netaddr.IPAddress(traffic['l3']['dstip']).value
                        tmp_ip = netaddr.IPAddress(dst_ip_value + stream)
                        tmp_flow.update({'dl_type':'0x0800', 'nw_dst':tmp_ip})
                    elif traffic['stream_type'] == 'L4':
                        tmp_flow.update({'dl_type':'0x0800',
                                         'nw_proto':socket.getprotobyname(traffic['l3']['proto'].lower()),
                                         'tp_dst':(traffic['l4']['dstport'] + stream) % 65536})
                    flows.append(tmp_flow)
            elif traffic and traffic['flow_type'].lower() == 'ip':
                flow.update({'dl_type':'0x0800', 'nw_src':traffic['l3']['srcip'],
                             'nw_dst':traffic['l3']['dstip']})
                flows.append(flow)
            else:
                flows.append(flow)
        elif operation == 'del' and port1:
            bridge = self._switches[switch_name]
            flows.append({'in_port': bridge.get_ports()[port1][0]})
        else:
            flows.append({})

        return flows

    def add_connection(self, switch_name, port1, port2, traffic=None):
        """See IVswitch for general description
        """
        flows = self._prepare_flows('add', switch_name, port1, port2, traffic)

        # enable flows caching for large number of flows
        cache = 'on' if len(flows) > _CACHE_FLOWS_LIMIT else 'off'

        for flow in flows:
            self.add_flow(switch_name, flow, cache)

        if cache == 'on':
            self.add_flow(switch_name, [], cache='flush')

    def del_connection(self, switch_name, port1=None, port2=None):
        """See IVswitch for general description
        """
        flows = self._prepare_flows('del', switch_name, port1, port2)

        for flow in flows:
            self.del_flow(switch_name, flow)

    def dump_connections(self, switch_name):
        """See IVswitch for general description
        """
        self.dump_flows(switch_name)

    def add_route(self, switch_name, network, destination):
        """See IVswitch for general description
        """
        bridge = self._switches[switch_name]
        bridge.add_route(network, destination)

    def set_tunnel_arp(self, ip_addr, mac_addr, switch_name):
        """See IVswitch for general description
        """
        bridge = self._switches[switch_name]
        bridge.set_tunnel_arp(ip_addr, mac_addr, switch_name)

    def _get_port_count(self, param):
        """Returns the number of ports having a certain parameter
        """
        cnt = 0
        for k in self._switches:
            pparams = [c for (_, (_, c)) in list(self._switches[k].get_ports().items())]
            phits = [i for i in pparams if param in i]
            cnt += len(phits)

        if cnt is None:
            cnt = 0
        return cnt

    def disable_stp(self, switch_name):
        """
        Disable stp protocol on the bridge
        :param switch_name: bridge to disable stp
        :return: None
        """
        bridge = self._switches[switch_name]
        bridge.set_stp(False)
        self._logger.info('Sleeping for 50 secs to allow stp to stop.')
        time.sleep(50)  # needs time to disable

    def enable_stp(self, switch_name):
        """
        Enable stp protocol on the bridge
        :param switch_name: bridge to enable stp
        :return: None
        """
        bridge = self._switches[switch_name]
        bridge.set_stp(True)
        self._logger.info('Sleeping for 50 secs to allow stp to start.')
        time.sleep(50)  # needs time to enable

    def disable_rstp(self, switch_name):
        """
        Disable rstp on the bridge
        :param switch_name: bridge to disable rstp
        :return: None
        """
        bridge = self._switches[switch_name]
        bridge.set_rstp(False)
        self._logger.info('Sleeping for 15 secs to allow rstp to stop.')
        time.sleep(15)  # needs time to disable

    def enable_rstp(self, switch_name):
        """
        Enable rstp on the bridge
        :param switch_name: bridge to enable rstp
        :return: None
        """
        bridge = self._switches[switch_name]
        bridge.set_rstp(True)
        self._logger.info('Sleeping for 15 secs to allow rstp to start.')
        time.sleep(15)  # needs time to enable

    def kill(self, signal='-15', sleep=10):
        """Kill ``ovs-vswitchd`` and ``ovs-ovsdb`` instances if they are alive.

        :returns: None
        """
        if os.path.isfile(self._vswitchd_pidfile_path):
            self._logger.info('Killing ovs-vswitchd...')
            with open(self._vswitchd_pidfile_path, "r") as pidfile:
                vswitchd_pid = pidfile.read().strip()
                tasks.terminate_task(vswitchd_pid, logger=self._logger)

        self._kill_ovsdb()  # ovsdb must be killed after vswitchd

        # just for case, that sudo envelope has not been terminated yet
        tasks.Process.kill(self, signal, sleep)

    # helper functions

    def _reset_ovsdb(self):
        """Reset system for 'ovsdb'.

        :returns: None
        """
        self._logger.info('Resetting system after last run...')

        # create a backup of ovs_var_tmp and ovs_etc_tmp; It is
        # essential for OVS installed from binary packages.
        self._stamp = '{:%Y%m%d_%H%M%S}_{}'.format(datetime.datetime.now(),
                                                   random.randrange(1000, 9999))
        for tmp_dir in ['ovs_var_tmp', 'ovs_etc_tmp']:
            if os.path.exists(settings.getValue('TOOLS')[tmp_dir]):
                orig_dir = os.path.normpath(settings.getValue('TOOLS')[tmp_dir])
                self._logger.info('Creating backup of %s directory...', tmp_dir)
                tasks.run_task(['sudo', 'mv', orig_dir, '{}.{}'.format(orig_dir, self._stamp)],
                               self._logger)

        # create fresh tmp dirs
        tasks.run_task(['sudo', 'mkdir', '-p', settings.getValue('TOOLS')['ovs_var_tmp']], self._logger)
        tasks.run_task(['sudo', 'mkdir', '-p', settings.getValue('TOOLS')['ovs_etc_tmp']], self._logger)

        self._logger.info('System reset after last run.')

    def _start_ovsdb(self):
        """Start ``ovsdb-server`` instance.

        :returns: None
        """
        ovsdb_tool_bin = settings.getValue('TOOLS')['ovsdb-tool']
        tasks.run_task(['sudo', ovsdb_tool_bin, 'create',
                        os.path.join(settings.getValue('TOOLS')['ovs_etc_tmp'], 'conf.db'),
                        settings.getValue('TOOLS')['ovsschema']],
                       self._logger,
                       'Creating ovsdb configuration database...')

        ovsdb_server_bin = settings.getValue('TOOLS')['ovsdb-server']

        tasks.run_background_task(
            ['sudo', ovsdb_server_bin,
             '--remote=punix:%s' % os.path.join(settings.getValue('TOOLS')['ovs_var_tmp'], 'db.sock'),
             '--remote=db:Open_vSwitch,Open_vSwitch,manager_options',
             '--pidfile=' + self._ovsdb_pidfile_path, '--overwrite-pidfile'],
            self._logger,
            'Starting ovsdb-server...')

    def _kill_ovsdb(self):
        """Kill ``ovsdb-server`` instance.

        :returns: None
        """
        if os.path.isfile(self._ovsdb_pidfile_path):
            with open(self._ovsdb_pidfile_path, "r") as pidfile:
                ovsdb_pid = pidfile.read().strip()

            self._logger.info("Killing ovsdb with pid: %s", ovsdb_pid)

            if ovsdb_pid:
                tasks.terminate_task(ovsdb_pid, logger=self._logger)

        # restore original content of ovs_var_tmp and ovs_etc_tmp; It is
        # essential for OVS installed from binary packages.
        if self._stamp:
            for tmp_dir in ['ovs_var_tmp', 'ovs_etc_tmp']:
                orig_dir = os.path.normpath(settings.getValue('TOOLS')[tmp_dir])
                if os.path.exists('{}.{}'.format(orig_dir, self._stamp)):
                    self._logger.info('Restoring backup of %s directory...', tmp_dir)
                    tasks.run_task(['sudo', 'rm', '-rf', orig_dir], self._logger)
                    tasks.run_task(['sudo', 'mv', '{}.{}'.format(orig_dir, self._stamp), orig_dir],
                                   self._logger)

    @staticmethod
    def get_db_sock_path():
        """Method returns location of db.sock file

        :returns: path to db.sock file.
        """
        return os.path.join(settings.getValue('TOOLS')['ovs_var_tmp'], 'db.sock')

    #
    # validate methods required for integration testcases
    #
    def validate_add_switch(self, _dummy_result, switch_name, _dummy_params=None):
        """Validate - Create a new logical switch with no ports
        """
        bridge = self._switches[switch_name]
        output = bridge.run_vsctl(['show'], check_error=True)
        assert not output[1]  # there shouldn't be any stderr, but in case
        assert re.search('Bridge ["\']?%s["\']?' % switch_name, output[0]) is not None
        return True

    # Method could be a function
    # pylint: disable=no-self-use
    def validate_del_switch(self, _dummy_result, switch_name):
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
        bridge = self._switches[switch_name]
        output = bridge.run_vsctl(['show'], check_error=True)
        assert not output[1]  # there shouldn't be any stderr, but in case
        assert re.search('Port ["\']?%s["\']?' % result[0], output[0]) is not None
        assert re.search('Interface ["\']?%s["\']?' % result[0], output[0]) is not None
        return True

    def validate_add_vport(self, result, switch_name):
        """ Validate that virtual port was added to bridge.
        """
        return self.validate_add_phy_port(result, switch_name)

    def validate_del_port(self, _dummy_result, switch_name, port_name):
        """ Validate that port_name was removed from bridge.
        """
        bridge = self._switches[switch_name]
        output = bridge.run_vsctl(['show'], check_error=True)
        assert not output[1]  # there shouldn't be any stderr, but in case
        assert 'Port "%s"' % port_name not in output[0]
        return True

    def validate_add_connection(self, result, switch_name, port1, port2, traffic=None):
        """ Validate that connection was added
        """
        for flow in self._prepare_flows('add', switch_name, port1, port2, traffic):
            if not self.validate_add_flow(result, switch_name, flow):
                return False

        return True

    def validate_del_connection(self, result, switch_name, port1, port2):
        """ Validate that connection was deleted
        """
        for flow in self._prepare_flows('del', switch_name, port1, port2):
            if not self.validate_del_flow(result, switch_name, flow):
                return False

        return True

    def validate_dump_connections(self, _dummy_result, _dummy_switch_name):
        """ Validate dump connections call
        """
        return True

    def validate_add_flow(self, _dummy_result, switch_name, flow, _dummy_cache='off'):
        """ Validate insertion of the flow into the switch
        """

        if 'idle_timeout' in flow:
            del flow['idle_timeout']

        # Note: it should be possible to call `ovs-ofctl dump-flows switch flow`
        # to verify flow insertion, but it doesn't accept the same flow syntax
        # as add-flow, so we have to compare it the hard way

        # get dump of flows and compare them one by one
        flow_src = flow_key(flow)
        bridge = self._switches[switch_name]
        output = bridge.run_ofctl(['dump-flows', switch_name], check_error=True)
        for flow_dump in output[0].split('\n'):
            if flow_match(flow_dump, flow_src):
                # flow was added correctly
                return True
        return False

    def validate_del_flow(self, _dummy_result, switch_name, flow=None):
        """ Validate removal of the flow
        """
        if not flow:
            # what else we can do?
            return True
        return not self.validate_add_flow(_dummy_result, switch_name, flow)

    def validate_dump_flows(self, _dummy_result, _dummy_switch_name):
        """ Validate call of flow dump
        """
        return True

    def validate_disable_rstp(self, _dummy_result, switch_name):
        """ Validate rstp disable
        """
        bridge = self._switches[switch_name]
        return 'rstp_enable         : false' in ''.join(bridge.bridge_info())

    def validate_enable_rstp(self, _dummy_result, switch_name):
        """ Validate rstp enable
        """
        bridge = self._switches[switch_name]
        return 'rstp_enable         : true' in ''.join(bridge.bridge_info())

    def validate_disable_stp(self, _dummy_result, switch_name):
        """ Validate stp disable
        """
        bridge = self._switches[switch_name]
        return 'stp_enable          : false' in ''.join(bridge.bridge_info())

    def validate_enable_stp(self, _dummy_result, switch_name):
        """ Validate stp enable
        """
        bridge = self._switches[switch_name]
        return 'stp_enable          : true' in ''.join(bridge.bridge_info())

    def validate_restart(self, _dummy_result):
        """ Validate restart
        """
        return True
