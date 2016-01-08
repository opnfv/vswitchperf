# Copyright 2016 Intel Corporation.
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

"""Wrapper for an OVS dpctl (``ovs-dpctl``) for managing datapaths.

"""

import os
import logging
import string

from tools import tasks
from conf import settings

_OVS_DPCTL_BIN = os.path.join(settings.getValue('OVS_DIR'), 'utilities',
                              'ovs-dpctl')

_OVS_LOCAL_DATAPATH = 'ovs-system'

class DPCtl(object):
    """remove/show datapaths using ``ovs-dpctl``.
    """
    def __init__(self, timeout=10):
        """Initialise logger.

        :param timeout: Timeout to be used for each command

        :returns: None
        """
        self.logger = logging.getLogger(__name__)
        self.timeout = timeout

    # helpers

    def run_dpctl(self, args, check_error=False):
        """Run ``ovs-dpctl`` with supplied arguments.

        :param args: Arguments to pass to ``ovs-dpctl``
        :param check_error: Throw exception on error

        :return: None
        """
        cmd = ['sudo', _OVS_DPCTL_BIN,
               '--timeout',
               str(self.timeout)] + args
        return tasks.run_task(
            cmd, self.logger, 'Running ovs-dpctl ..', check_error)

    # datapath management

    def del_dp(self, dp_name=_OVS_LOCAL_DATAPATH):
        """Delete local datapath (ovs-dpctl).

        :param br_name: Name of bridge

        :return: None
        """
        self.logger.debug('delete datapath ' + dp_name)
        self.run_dpctl(['del-dp', dp_name])

