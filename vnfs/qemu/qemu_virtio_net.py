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

"""Automation of QEMU hypervisor for launching virtio-net enabled guests.
"""

import logging
from vnfs.qemu.qemu import IVnfQemu
from conf import settings as S
from tools import tasks

class QemuVirtioNet(IVnfQemu):
    """
    Control an instance of QEMU with virtio-net guest communication.
    """

    def __init__(self):
        """
        Initialisation function.
        """
        super(QemuVirtioNet, self).__init__()
        self._logger = logging.getLogger(__name__)

        # insert vanilla ovs specific modules
        tasks.run_task(['sudo', 'modprobe', 'vhost_net'], self._logger,
                       'Loading vhost_net module...', True)

        # calculate index of first interface, i.e. check how many
        # interfaces has been created for previous VMs, where 1st NIC
        # of 1st VM has index 0
        start_index = sum(S.getValue('GUEST_NICS_NR')[:self._number])

        # multi-queue values
        if int(S.getValue('GUEST_NIC_QUEUES')[self._number]):
            queue_str = ',queues={}'.format(
                S.getValue('GUEST_NIC_QUEUES')[self._number])
            mq_vector_str = ',mq=on,vectors={}'.format(
                int(S.getValue('GUEST_NIC_QUEUES')[self._number]) * 2 + 2)
        else:
            queue_str, mq_vector_str = '', ''

        # setup requested number of interfaces
        for nic in range(len(self._nics)):
            index = start_index + nic
            ifi = str(index)
            self._cmd += ['-netdev', 'type=tap,id=' +
                          self._nics[nic]['device'] + queue_str +
                          ',script=no,downscript=no,' +
                          'ifname=tap' + ifi + ',vhost=on',
                          '-device',
                          'virtio-net-pci,mac=' +
                          self._nics[nic]['mac'] + ',netdev=' +
                          self._nics[nic]['device'] +
                          ',csum=off,gso=off,' +
                          'guest_tso4=off,guest_tso6=off,guest_ecn=off' +
                          mq_vector_str,
                         ]
