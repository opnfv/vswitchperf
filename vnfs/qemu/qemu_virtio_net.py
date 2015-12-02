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

        # calculate indexes of guest devices (e.g. charx, dpdkvhostuserx)
        i = self._number * 2
        if1 = str(i)
        if2 = str(i + 1)

        self._cmd += ['-netdev',
                      'type=tap,id=' + self._net1 +
                      ',script=no,downscript=no,' +
                      'ifname=tap' + if1 + ',vhost=on',
                      '-device',
                      'virtio-net-pci,mac=' +
                      S.getValue('GUEST_NET1_MAC')[self._number] +
                      ',netdev=' + self._net1 + ',csum=off,gso=off,' +
                      'guest_tso4=off,guest_tso6=off,guest_ecn=off',
                      '-netdev',
                      'type=tap,id=' + self._net2 +
                      ',script=no,downscript=no,' +
                      'ifname=tap' + if2 + ',vhost=on',
                      '-device',
                      'virtio-net-pci,mac=' +
                      S.getValue('GUEST_NET2_MAC')[self._number] +
                      ',netdev=' + self._net2 + ',csum=off,gso=off,' +
                      'guest_tso4=off,guest_tso6=off,guest_ecn=off',
                     ]
