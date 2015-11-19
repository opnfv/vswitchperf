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

        # calculate indexes of guest devices (e.g. charx, dpdkvhostuserx)
        i = self._number * 2
        if1 = str(i)
        if2 = str(i + 1)
        net1 = 'net' + str(i + 1)
        net2 = 'net' + str(i + 2)

        self._cmd += ['-chardev',
                      'socket,id=char' + if1 +
                      ',path=' + S.getValue('OVS_VAR_DIR') +
                      'dpdkvhostuser' + if1,
                      '-chardev',
                      'socket,id=char' + if2 +
                      ',path=' + S.getValue('OVS_VAR_DIR') +
                      'dpdkvhostuser' + if2,
                      '-netdev',
                      'type=vhost-user,id=' + net1 +
                      ',chardev=char' + if1 + ',vhostforce',
                      '-device',
                      'virtio-net-pci,mac=' +
                      S.getValue('GUEST_NET1_MAC')[self._number] +
                      ',netdev=' + net1 + ',csum=off,gso=off,' +
                      'guest_tso4=off,guest_tso6=off,guest_ecn=off',
                      '-netdev',
                      'type=vhost-user,id=' + net2 +
                      ',chardev=char' + if2 + ',vhostforce',
                      '-device',
                      'virtio-net-pci,mac=' +
                      S.getValue('GUEST_NET2_MAC')[self._number] +
                      ',netdev=' + net2 + ',csum=off,gso=off,' +
                      'guest_tso4=off,guest_tso6=off,guest_ecn=off',
                     ]

