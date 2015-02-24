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

"""
Automation of ``ovs-dpdk`` and ``ovs-dpctl``.

Much of this code is based on ``ovs-lib.py`` from Open Stack:

    https://github.com/openstack/neutron/blob/6eac1dc99124ca024d6a69b3abfa3bc69c735667/neutron/agent/linux/ovs_lib.py

This is intentional, as it allows it to serve as a psuedo-acceptance test in
their own right:

    https://01.org/packet-processing/intel%C2%AE-onp-servers

Part of 'toit' - The OVS Integration Testsuite.
"""

import os
import logging
import string

from toit import utils
from toit.conf import settings

OVS_VSCTL_BIN = os.path.join(getattr(settings, 'OVS_DIR'), 'utilities',
                             'ovs-vsctl')
OVS_OFCTL_BIN = os.path.join(getattr(settings, 'OVS_DIR'), 'utilities',
                             'ovs-ofctl')


class OFBase(object):
    """
    Add/remove/show datapaths using ``ovs-ofctl``.
    """
    def __init__(self, timeout=10):
        """
        Initialise logger.

        :param timeout: Timeout to be used for each command

        :returns: None
        """
        self.logger = logging.getLogger(__name__)
        self.timeout = timeout

    # helpers

    def run_vsctl(self, args, check_error=False):
        """
        Run ``ovs-vsctl`` with supplied arguments.

        :param args: Arguments to pass to ``ovs-vsctl``
        :param check_error: Throw exception on error

        :return: None
        """
        cmd = ['sudo', OVS_VSCTL_BIN, '--timeout', str(self.timeout)] + args
        return utils.run_task(
            cmd, self.logger, 'Running ovs-vsctl...', check_error)

    # datapath management

    def add_br(self, br_name='br0'):
        """
        Add datapath.

        :param br_name: Name of bridge

        :return: Instance of :class OFBridge:
        """
        self.logger.debug('add bridge')
        self.run_vsctl(['add-br', br_name])

        return OFBridge(br_name, self.timeout)

    def del_br(self, br_name='br0'):
        """
        Delete datapath.

        :param br_name: Name of bridge

        :return: None
        """
        self.logger.debug('delete bridge')
        self.run_vsctl(['del-br', br_name])


class OFBridge(OFBase):
    """
    Control a bridge instance using ``ovs-vsctl`` and ``ovs-ofctl``.
    """
    def __init__(self, br_name='br0', timeout=10):
        """
        Initialise bridge.

        :param br_name: Bridge name
        :param timeout: Timeout to be used for each command

        :returns: None
        """
        super(OFBridge, self).__init__(timeout)
        self.br_name = br_name

    # context manager

    def __enter__(self):
        """
        Create datapath, and and return self.
        """
        return self

    def __exit__(self, type_, value, traceback):
        """
        Remove datapath.
        """
        if not traceback:
            self.destroy()

    # helpers

    def run_ofctl(self, args, check_error=False):
        """
        Run ``ovs-ofctl`` with supplied arguments.

        :param args: Arguments to pass to ``ovs-ofctl``
        :param check_error: Throw exception on error

        :return: None
        """
        cmd = ['sudo', OVS_OFCTL_BIN, '--timeout', str(self.timeout)] + args
        return utils.run_task(
            cmd, self.logger, 'Running ovs-ofctl...', check_error)

    def create(self):
        """
        Create bridge.
        """
        self.logger.debug('create bridge')
        self.add_br(self.br_name)

    def destroy(self):
        """
        Destroy bridge.
        """
        self.logger.debug('destroy bridge')
        self.del_br(self.br_name)

    def reset(self):
        """
        Reset bridge.
        """
        self.logger.debug('reset bridge')
        self.destroy()
        self.create()

    # port mangement

    def add_port(self, port_name):
        """
        Add port to bridge.

        :param port_name: Name of port

        :return: None
        """
        self.logger.debug('add port')
        self.run_vsctl(['add-port', self.br_name, port_name])

    def del_port(self, port_name):
        """
        Remove port from bridge.

        :param port_name: Name of port

        :return: None
        """
        self.logger.debug('delete port')
        self.run_vsctl(['del-port', self.br_name, port_name])

    def set_db_attribute(self, table_name, record, column, value):
        """
        Set database attribute.

        :param table_name: Name of table
        :param record: Name of record
        :param column: Name of column
        :param value: Value to set

        :return: None
        """
        self.logger.debug('set attribute')
        self.run_vsctl(['set', table_name, record, '%s=%s' % (column, value)])

    def clear_db_attribute(self, table_name, record, column):
        """
        Clear database attribute.

        :param table_name: Name of table
        :param record: Name of record
        :param column: Name of column

        :return: None
        """
        self.logger.debug('clear attribute')
        self.run_vsctl(['clear', table_name, record, column])

    # flow mangement

    def add_flow(self, **kwargs):
        """
        Add flow to bridge.

        :param kwargs: Flow arguments

        :return: None
        """
        if not kwargs.get('actions'):
            self.logger.error('add flow requires actions')
            return

        self.logger.debug('add flow')
        _flow_key = flow_key(**kwargs)
        self.logger.debug('key : %s', _flow_key)
        self.run_ofctl(['add-flow', self.br_name, _flow_key])

    def del_flow(self, **kwargs):
        """
        Delete flow from bridge.

        :param kwargs: Flow arguments

        :return: None
        """
        self.logger.debug('delete flow')
        _flow_key = flow_key(**kwargs)
        self.logger.debug('key : %s', _flow_key)
        self.run_ofctl(['del-flows', self.br_name, _flow_key])

    def del_flows(self):
        """
        Delete all flows from bridge.
        """
        self.logger.debug('delete flows')
        self.run_ofctl(['del-flows', self.br_name])

    def dump_flows(self):
        """
        Dump all flows from bridge.
        """
        self.logger.debug('dump flows')
        self.run_ofctl(['dump-flows', self.br_name])

#
# helper functions
#


def flow_key(**kwargs):
    """
    Model a flow key string for ``ovs-ofctl``.

    Syntax taken from ``ovs-ofctl`` manpages:
        http://openvswitch.org/cgi-bin/ovsman.cgi?page=utilities%2Fovs-ofctl.8

    :param kwargs: Flow arguments

    :return: String
    :rtype: str
    """
    _flow_add_key = string.Template('${fields},action=${actions}')
    _flow_del_key = string.Template('${fields}')

    field_params = []

    user_params = (x for x in kwargs.iteritems() if x[0] != 'actions')
    for (key, default) in user_params:
        field_params.append('%(field)s=%(value)s' %
                            {'field': key, 'value': default})

    field_params = ','.join(field_params)

    _flow_key_param = {
        'fields': field_params,
    }

    # no actions == delete key
    if 'actions' in kwargs:
        _flow_key_param['actions'] = ','.join(kwargs['actions'])

        flow_str = _flow_add_key.substitute(_flow_key_param)
    else:
        flow_str = _flow_del_key.substitute(_flow_key_param)

    return flow_str
