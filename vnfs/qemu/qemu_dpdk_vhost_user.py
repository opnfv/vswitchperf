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

"""Automation of QEMU hypervisor for launching vhost-user enabled guests.
"""

import logging

from conf import settings as S
from conf import get_test_param
from vnfs.qemu.qemu import IVnfQemu

class QemuDpdkVhostUser(IVnfQemu):
    """
    Control an instance of QEMU with vHost user guest communication.
    """
    def __init__(self):
        """
        Initialisation function.
        """
        super(QemuDpdkVhostUser, self).__init__()
        self._logger = logging.getLogger(__name__)

        # multi-queue values
        guest_nic_queues = int(get_test_param('guest_nic_queues', 0))
        if guest_nic_queues:
            override_list = [guest_nic_queues] * (self._number + 1)
            S.setValue('GUEST_NIC_QUEUES', override_list)
        if int(S.getValue('GUEST_NIC_QUEUES')[self._number]):
            queue_str = ',queues={}'.format(S.getValue('GUEST_NIC_QUEUES')[self._number])
            mq_vector_str = ',mq=on,vectors={}'.format(
                int(S.getValue('GUEST_NIC_QUEUES')[self._number]) * 2 + 2)
        else:
            queue_str, mq_vector_str = '', ''

        # Guest merge buffer setting
        if S.getValue('GUEST_NIC_MERGE_BUFFERS_DISABLE')[self._number]:
            merge_buff = 'mrg_rxbuf=off,'
        else:
            merge_buff = ''

        # calculate index of first interface, i.e. check how many
        # interfaces has been created for previous VMs, where 1st NIC
        # of 1st VM has index 0
        start_index = sum(S.getValue('GUEST_NICS_NR')[:self._number])

        # setup requested number of interfaces
        for nic in range(len(self._nics)):
            index = start_index + nic
            ifi = str(index)
            net = 'net' + str(index + 1)

            self._cmd += ['-chardev',
                          'socket,id=char' + ifi +
                          ',path=' + S.getValue('TOOLS')['ovs_var_tmp'] +
                          'dpdkvhostuser' + ifi,
                          '-netdev',
                          'type=vhost-user,id=' + net +
                          ',chardev=char' + ifi + ',vhostforce' + queue_str,
                          '-device',
                          'virtio-net-pci,mac=' +
                          self._nics[nic]['mac'] +
                          ',netdev=' + net + ',csum=off,' + merge_buff +
                          'gso=off,' +
                          'guest_tso4=off,guest_tso6=off,guest_ecn=off' +
                          mq_vector_str,
                         ]
