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
import os
import time
import pexpect
from conf import settings
from vswitches.vswitch import IVSwitch
from src.ovs import OFBridge, flow_key, flow_match
from tools import tasks

_OVS_VAR_DIR = settings.getValue('OVS_VAR_DIR')
_OVS_ETC_DIR = settings.getValue('OVS_ETC_DIR')

class IVSwitchOvs(IVSwitch, tasks.Process):
    """Open vSwitch base class implementation

    The method docstrings document only considerations specific to this
    implementation. For generic information of the nature of the methods,
    see the interface.
    """
    _logfile = os.path.join(settings.getValue('LOG_DIR'), settings.getValue('LOG_FILE_VSWITCHD'))
    _ovsdb_pidfile_path = os.path.join(settings.getValue('LOG_DIR'), "ovsdb_pidfile.pid")
    _vswitchd_pidfile_path = os.path.join(settings.getValue('LOG_DIR'), "vswitchd_pidfile.pid")
    _proc_name = 'ovs-vswitchd'

    def __init__(self):
        """See IVswitch for general description
        """
        self._logger = logging.getLogger(__name__)
        self._expect = None
        self._timeout = 30
        self._bridges = {}
        self._vswitchd_args = ['--pidfile=' + self._vswitchd_pidfile_path,
                               '--overwrite-pidfile', '--log-file=' + self._logfile]
        self._cmd = []
        self._cmd_template = ['sudo', '-E', os.path.join(settings.getValue('OVS_DIR'),
                                                         'vswitchd', 'ovs-vswitchd')]

    def start(self):
        """ Start ``ovsdb-server`` and ``ovs-vswitchd`` instance.

        :raises: pexpect.EOF, pexpect.TIMEOUT
        """
        self._logger.info("Starting vswitchd...")

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
            logging.error("Exception during VSwitch start.")
            self._kill_ovsdb()
            raise exc

        self._logger.info("Vswitchd...Started.")

    def configure(self):
        """ Configure vswitchd through ovsdb if needed
        """
        pass

    def stop(self):
        """See IVswitch for general description
        """
        self._logger.info("Terminating vswitchd...")
        self.kill()
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

        tasks.run_task(['sudo', 'rm', '-rf', _OVS_VAR_DIR], self._logger)
        tasks.run_task(['sudo', 'mkdir', '-p', _OVS_VAR_DIR], self._logger)
        tasks.run_task(['sudo', 'rm', '-rf', _OVS_ETC_DIR], self._logger)
        tasks.run_task(['sudo', 'mkdir', '-p', _OVS_ETC_DIR], self._logger)

        tasks.run_task(['sudo', 'rm', '-f',
                        os.path.join(_OVS_ETC_DIR, 'conf.db')],
                       self._logger)

        self._logger.info('System reset after last run.')

    def _start_ovsdb(self):
        """Start ``ovsdb-server`` instance.

        :returns: None
        """
        ovsdb_tool_bin = os.path.join(
            settings.getValue('OVS_DIR'), 'ovsdb', 'ovsdb-tool')
        tasks.run_task(['sudo', ovsdb_tool_bin, 'create',
                        os.path.join(_OVS_ETC_DIR, 'conf.db'),
                        os.path.join(settings.getValue('OVS_DIR'), 'vswitchd',
                                     'vswitch.ovsschema')],
                       self._logger,
                       'Creating ovsdb configuration database...')

        ovsdb_server_bin = os.path.join(
            settings.getValue('OVS_DIR'), 'ovsdb', 'ovsdb-server')

        tasks.run_background_task(
            ['sudo', ovsdb_server_bin,
             '--remote=punix:%s' % os.path.join(_OVS_VAR_DIR, 'db.sock'),
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

            self._logger.info("Killing ovsdb with pid: " + ovsdb_pid)

            if ovsdb_pid:
                tasks.terminate_task(ovsdb_pid, logger=self._logger)

    @staticmethod
    def get_db_sock_path():
        """Method returns location of db.sock file

        :returns: path to db.sock file.
        """
        return os.path.join(_OVS_VAR_DIR, 'db.sock')

    #
    # validate methods required for integration testcases
    #

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
