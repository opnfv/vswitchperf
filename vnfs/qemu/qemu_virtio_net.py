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
from conf import get_test_param
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
        self._net1 = S.getValue('VANILLA_NIC1_NAME')[self._number]
        self._net2 = S.getValue('VANILLA_NIC2_NAME')[self._number]

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

    # helper functions

    def _config_guest_loopback(self):
        """
        Configure VM to perform forwarding between NICs
        """

        # Disable services (F16)
        self.execute_and_wait('systemctl stop iptables.service')
        self.execute_and_wait('systemctl stop irqbalance.service')

        nic1_name = get_test_param('vanilla_nic1_name', self._net1)
        self.execute('ifconfig ' + nic1_name + ' ' +
                     S.getValue('VANILLA_NIC1_IP_CIDR')[self._number])

        nic2_name = get_test_param('vanilla_nic2_name', self._net2)
        self.execute('ifconfig ' + nic2_name + ' ' +
                     S.getValue('VANILLA_NIC2_IP_CIDR')[self._number])

        # configure linux bridge
        self.execute('brctl addbr br0')
        self.execute('brctl addif br0 ' + self._net1 + ' ' + self._net2)
        self.execute('ifconfig br0 ' +
                     S.getValue('VANILLA_BRIDGE_IP')[self._number])

        # Add the arp entries for the IXIA ports and the bridge you are using.
        # Use command line values if provided.
        trafficgen_mac = get_test_param('vanilla_tgen_port1_mac',
                                        S.getValue('VANILLA_TGEN_PORT1_MAC'))
        trafficgen_ip = get_test_param('vanilla_tgen_port1_ip',
                                       S.getValue('VANILLA_TGEN_PORT1_IP'))

        self.execute('arp -s ' + trafficgen_ip + ' ' + trafficgen_mac)

        trafficgen_mac = get_test_param('vanilla_tgen_port2_mac',
                                        S.getValue('VANILLA_TGEN_PORT2_MAC'))
        trafficgen_ip = get_test_param('vanilla_tgen_port2_ip',
                                       S.getValue('VANILLA_TGEN_PORT2_IP'))

        self.execute('arp -s ' + trafficgen_ip + ' ' + trafficgen_mac)

        # Enable forwarding
        self.execute('sysctl -w net.ipv4.ip_forward=1')

        # Controls source route verification
        # 0 means no source validation
        self.execute('sysctl -w net.ipv4.conf.all.rp_filter=0')
        self.execute('sysctl -w net.ipv4.conf.' + self._net1 + '.rp_filter=0')
        self.execute('sysctl -w net.ipv4.conf.' + self._net2 + '.rp_filter=0')
