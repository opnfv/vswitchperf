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

"""Automation of QEMU hypervisor for launching vhost-cuse enabled guests.
"""

from vnfs.qemu.qemu import IVnfQemu
from conf import settings as S

class IVnfQemuDpdk(IVnfQemu):
    """
    An abstract class for controling an instance of QEMU with DPDK vHost support
    """

    def __init__(self):
        """
        Initialisation function.
        """
        super(IVnfQemuDpdk, self).__init__()
        self._cmd += ['-drive',
                      'if=scsi,file=fat:rw:%s,snapshot=off' %
                      S.getValue('GUEST_SHARE_DIR')[self._number],
                     ]

    def _modify_dpdk_makefile(self):
        """
        Modifies DPDK makefile in Guest before compilation
        """
        pass

    def _config_guest_loopback(self):
        """
        Configure VM to run testpmd

        Configure performs the following:
        * Mount hugepages
        * mount shared directory for copying DPDK
        * Disable firewall
        * Compile DPDK
        * DPDK NIC bind
        * Run testpmd
        """

        # Guest images _should_ have 1024 hugepages by default,
        # but just in case:'''
        self.execute_and_wait('sysctl vm.nr_hugepages=1024')

        # Mount hugepages
        self.execute_and_wait('mkdir -p /dev/hugepages')
        self.execute_and_wait(
            'mount -t hugetlbfs hugetlbfs /dev/hugepages')

        # mount shared directory
        self.execute_and_wait('umount ' + S.getValue('OVS_DPDK_SHARE'))
        self.execute_and_wait('rm -rf ' + S.getValue('GUEST_OVS_DPDK_DIR'))
        self.execute_and_wait('mkdir -p ' + S.getValue('OVS_DPDK_SHARE'))
        self.execute_and_wait('mount -o iocharset=utf8 /dev/sdb1 ' +
                              S.getValue('OVS_DPDK_SHARE'))
        self.execute_and_wait('mkdir -p ' + S.getValue('GUEST_OVS_DPDK_DIR'))
        self.execute_and_wait('cp -a ' + S.getValue('OVS_DPDK_SHARE') + '/* ' +
                              S.getValue('GUEST_OVS_DPDK_DIR'))
        # Get VM info
        self.execute_and_wait('cat /etc/default/grub')

        # Disable services (F16)
        self.execute_and_wait('systemctl status iptables.service')
        self.execute_and_wait('systemctl stop iptables.service')

        # build and configure system for dpdk
        self.execute_and_wait('cd ' + S.getValue('GUEST_OVS_DPDK_DIR') +
                              '/DPDK')
        self.execute_and_wait('export CC=gcc')
        self.execute_and_wait('export RTE_SDK=' +
                              S.getValue('GUEST_OVS_DPDK_DIR') + '/DPDK')
        self.execute_and_wait('export RTE_TARGET=%s' % S.getValue('RTE_TARGET'))

        # modify makefile if needed
        self._modify_dpdk_makefile()

        self.execute_and_wait('make RTE_OUTPUT=$RTE_SDK/$RTE_TARGET -C '
                              '$RTE_SDK/lib/librte_eal/linuxapp/igb_uio')
        self.execute_and_wait('modprobe uio')
        self.execute_and_wait('insmod %s/kmod/igb_uio.ko' %
                              S.getValue('RTE_TARGET'))
        self.execute_and_wait('./tools/dpdk_nic_bind.py --status')
        self.execute_and_wait(
            './tools/dpdk_nic_bind.py -b igb_uio' ' ' +
            S.getValue('GUEST_NET1_PCI_ADDRESS')[self._number] + ' ' +
            S.getValue('GUEST_NET2_PCI_ADDRESS')[self._number])

        # build and run 'test-pmd'
        self.execute_and_wait('cd ' + S.getValue('GUEST_OVS_DPDK_DIR') +
                              '/DPDK/app/test-pmd')
        self.execute_and_wait('make clean')
        self.execute_and_wait('make')
        self.execute_and_wait('./testpmd -c 0x3 -n 4 --socket-mem 512 --'
                              ' --burst=64 -i --txqflags=0xf00 ' +
                              '--disable-hw-vlan', 60, "Done")
        self.execute('set fwd mac_retry', 1)
        self.execute_and_wait('start', 20,
                              'TX RS bit threshold=0 - TXQ flags=0xf00')
