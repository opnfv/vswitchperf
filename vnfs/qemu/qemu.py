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

"""Automation of QEMU hypervisor for launching vhost-cuse enabled guests.
"""

import os
import logging
import locale
import re
import subprocess

from conf import settings as S
from conf import get_test_param
from vnfs.vnf.vnf import IVnf

class IVnfQemu(IVnf):
    """
    Abstract class for controling an instance of QEMU
    """
    _cmd = None
    _expect = S.getValue('GUEST_PROMPT_LOGIN')
    _proc_name = 'qemu'

    class GuestCommandFilter(logging.Filter):
        """
        Filter out strings beginning with 'guestcmd :'.
        """
        def filter(self, record):
            return record.getMessage().startswith(self.prefix)

    def __init__(self):
        """
        Initialisation function.
        """
        super(IVnfQemu, self).__init__()
        self._logger = logging.getLogger(__name__)
        self._logfile = os.path.join(
            S.getValue('LOG_DIR'),
            S.getValue('LOG_FILE_QEMU')) + str(self._number)
        self._timeout = S.getValue('GUEST_TIMEOUT')[self._number]
        self._monitor = '%s/vm%dmonitor' % ('/tmp', self._number)
        self._net1 = get_test_param('guest_nic1_name', None)
        if self._net1 == None:
            self._net1 = S.getValue('GUEST_NIC1_NAME')[self._number]
        else:
            self._net1 = self._net1.split(',')[self._number]
        self._net2 = get_test_param('guest_nic2_name', None)
        if self._net2 == None:
            self._net2 = S.getValue('GUEST_NIC2_NAME')[self._number]
        else:
            self._net2 = self._net2.split(',')[self._number]

        # set guest loopback application based on VNF configuration
        # cli option take precedence to config file values
        self._guest_loopback = S.getValue('GUEST_LOOPBACK')[self._number]


        name = 'Client%d' % self._number
        vnc = ':%d' % self._number
        # don't use taskset to affinize main qemu process; It causes hangup
        # of 2nd VM in case of DPDK. It also slows down VM responsivnes.
        self._cmd = ['sudo', '-E', S.getValue('QEMU_BIN'),
                     '-m', S.getValue('GUEST_MEMORY')[self._number],
                     '-smp', str(S.getValue('GUEST_SMP')[self._number]),
                     '-cpu', 'host,migratable=off',
                     '-drive', 'if=scsi,file=' +
                     S.getValue('GUEST_IMAGE')[self._number],
                     '-boot', 'c', '--enable-kvm',
                     '-monitor', 'unix:%s,server,nowait' % self._monitor,
                     '-object',
                     'memory-backend-file,id=mem,size=' +
                     str(S.getValue('GUEST_MEMORY')[self._number]) + 'M,' +
                     'mem-path=' + S.getValue('HUGEPAGE_DIR') + ',share=on',
                     '-numa', 'node,memdev=mem -mem-prealloc',
                     '-nographic', '-vnc', str(vnc), '-name', name,
                     '-snapshot', '-net none', '-no-reboot',
                     '-drive',
                     'if=scsi,format=raw,file=fat:rw:%s,snapshot=off' %
                     S.getValue('GUEST_SHARE_DIR')[self._number],
                    ]
        self._configure_logging()

    def _configure_logging(self):
        """
        Configure logging.
        """
        self.GuestCommandFilter.prefix = self._log_prefix

        logger = logging.getLogger()
        cmd_logger = logging.FileHandler(
            filename=os.path.join(S.getValue('LOG_DIR'),
                                  S.getValue('LOG_FILE_GUEST_CMDS')) +
            str(self._number))
        cmd_logger.setLevel(logging.DEBUG)
        cmd_logger.addFilter(self.GuestCommandFilter())
        logger.addHandler(cmd_logger)

    # startup/Shutdown

    def start(self):
        """
        Start QEMU instance, login and prepare for commands.
        """
        super(IVnfQemu, self).start()
        if S.getValue('VNF_AFFINITIZATION_ON'):
            self._affinitize()

        if self._timeout:
            self._config_guest_loopback()

    def stop(self):
        """
        Stops VNF instance gracefully first.
        """
        # exit testpmd if needed
        if self._guest_loopback == 'testpmd':
            self.execute_and_wait('stop', 120, "Done")
            self.execute_and_wait('quit', 120, "bye")

        # turn off VM
        self.execute_and_wait('poweroff', 120, "Power down")

        # just for case that graceful shutdown failed
        super(IVnfQemu, self).stop()

    # helper functions

    def _login(self, timeout=120):
        """
        Login to QEMU instance.

        This can be used immediately after booting the machine, provided a
        sufficiently long ``timeout`` is given.

        :param timeout: Timeout to wait for login to complete.

        :returns: None
        """
        # if no timeout was set, we likely started QEMU without waiting for it
        # to boot. This being the case, we best check that it has finished
        # first.
        if not self._timeout:
            self._expect_process(timeout=timeout)

        self._child.sendline(S.getValue('GUEST_USERNAME'))
        self._child.expect(S.getValue('GUEST_PROMPT_PASSWORD'), timeout=5)
        self._child.sendline(S.getValue('GUEST_PASSWORD'))

        self._expect_process(S.getValue('GUEST_PROMPT'), timeout=5)

    def send_and_pass(self, cmd, timeout=30):
        """
        Send ``cmd`` and wait ``timeout`` seconds for it to pass.

        :param cmd: Command to send to guest.
        :param timeout: Time to wait for prompt before checking return code.

        :returns: None
        """
        self.execute(cmd)
        self.wait(S.getValue('GUEST_PROMPT'), timeout=timeout)
        self.execute('echo $?')
        self._child.expect('^0$', timeout=1)  # expect a 0
        self.wait(S.getValue('GUEST_PROMPT'), timeout=timeout)

    def _affinitize(self):
        """
        Affinitize the SMP cores of a QEMU instance.

        This is a bit of a hack. The 'socat' utility is used to
        interact with the QEMU HMP. This is necessary due to the lack
        of QMP in older versions of QEMU, like v1.6.2. In future
        releases, this should be replaced with calls to libvirt or
        another Python-QEMU wrapper library.

        :returns: None
        """
        thread_id = (r'.* CPU #%d: .* thread_id=(\d+)')

        self._logger.info('Affinitizing guest...')

        cur_locale = locale.getdefaultlocale()[1]
        proc = subprocess.Popen(
            ('echo', 'info cpus'), stdout=subprocess.PIPE)
        output = subprocess.check_output(
            ('sudo', 'socat', '-', 'UNIX-CONNECT:%s' % self._monitor),
            stdin=proc.stdout)
        proc.wait()

        for cpu in range(0, int(S.getValue('GUEST_SMP')[self._number])):
            match = None
            for line in output.decode(cur_locale).split('\n'):
                match = re.search(thread_id % cpu, line)
                if match:
                    self._affinitize_pid(
                        S.getValue('GUEST_CORE_BINDING')[self._number][cpu],
                        match.group(1))
                    break

            if not match:
                self._logger.error('Failed to affinitize guest core #%d. Could'
                                   ' not parse tid.', cpu)

    def _config_guest_loopback(self):
        """
        Configure VM to run VNF, e.g. port forwarding application based on the configuration
        """
        if self._guest_loopback == 'testpmd':
            self._login()
            self._configure_testpmd()
        elif self._guest_loopback == 'l2fwd':
            self._login()
            self._configure_l2fwd()
        elif self._guest_loopback == 'linux_bridge':
            self._login()
            self._configure_linux_bridge()
        elif self._guest_loopback != 'buildin':
            self._logger.error('Unsupported guest loopback method "%s" was specified. Option'
                               ' "buildin" will be used as a fallback.', self._guest_loopback)

    def wait(self, prompt=S.getValue('GUEST_PROMPT'), timeout=30):
        super(IVnfQemu, self).wait(prompt=prompt, timeout=timeout)

    def execute_and_wait(self, cmd, timeout=30,
                         prompt=S.getValue('GUEST_PROMPT')):
        super(IVnfQemu, self).execute_and_wait(cmd, timeout=timeout,
                                               prompt=prompt)

    def _modify_dpdk_makefile(self):
        """
        Modifies DPDK makefile in Guest before compilation
        """
        pass

    def _configure_copy_sources(self, dirname):
        """
        Mount shared directory and copy DPDK and l2fwd sources
        """
        # mount shared directory
        self.execute_and_wait('umount ' + S.getValue('OVS_DPDK_SHARE'))
        self.execute_and_wait('rm -rf ' + S.getValue('GUEST_OVS_DPDK_DIR'))
        self.execute_and_wait('mkdir -p ' + S.getValue('OVS_DPDK_SHARE'))
        self.execute_and_wait('mount -o iocharset=utf8 /dev/sdb1 ' +
                              S.getValue('OVS_DPDK_SHARE'))
        self.execute_and_wait('mkdir -p ' + S.getValue('GUEST_OVS_DPDK_DIR'))
        self.execute_and_wait('cp -ra ' + os.path.join(S.getValue('OVS_DPDK_SHARE'), dirname) +
                              ' ' + S.getValue('GUEST_OVS_DPDK_DIR'))

    def _configure_disable_firewall(self):
        """
        Disable firewall in VM
        """
        for iptables in ['iptables', 'ip6tables']:
            # filter table
            for chain in ['INPUT', 'FORWARD', 'OUTPUT']:
                self.execute_and_wait("{} -t filter -P {} ACCEPT".format(iptables, chain))
            # mangle table
            for chain in ['PREROUTING', 'INPUT', 'FORWARD', 'OUTPUT', 'POSTROUTING']:
                self.execute_and_wait("{} -t mangle -P {} ACCEPT".format(iptables, chain))
            # nat table
            for chain in ['PREROUTING', 'INPUT', 'OUTPUT', 'POSTROUTING']:
                self.execute_and_wait("{} -t nat -P {} ACCEPT".format(iptables, chain))

            # flush rules and delete chains created by user
            for table in ['filter', 'mangle', 'nat']:
                self.execute_and_wait("{} -t {} -F".format(iptables, table))
                self.execute_and_wait("{} -t {} -X".format(iptables, table))


    def _configure_testpmd(self):
        """
        Configure VM to perform L2 forwarding between NICs by DPDK's testpmd
        """
        self._configure_copy_sources('DPDK')
        self._configure_disable_firewall()

        # Guest images _should_ have 1024 hugepages by default,
        # but just in case:'''
        self.execute_and_wait('sysctl vm.nr_hugepages=1024')

        # Mount hugepages
        self.execute_and_wait('mkdir -p /dev/hugepages')
        self.execute_and_wait(
            'mount -t hugetlbfs hugetlbfs /dev/hugepages')

        # build and configure system for dpdk
        self.execute_and_wait('cd ' + S.getValue('GUEST_OVS_DPDK_DIR') +
                              '/DPDK')
        self.execute_and_wait('export CC=gcc')
        self.execute_and_wait('export RTE_SDK=' +
                              S.getValue('GUEST_OVS_DPDK_DIR') + '/DPDK')
        self.execute_and_wait('export RTE_TARGET=%s' % S.getValue('RTE_TARGET'))

        # modify makefile if needed
        self._modify_dpdk_makefile()

        # disable network interfaces, so DPDK can take care of them
        self.execute_and_wait('ifdown ' + self._net1)
        self.execute_and_wait('ifdown ' + self._net2)

        # build and insert igb_uio and rebind interfaces to it
        self.execute_and_wait('make RTE_OUTPUT=$RTE_SDK/$RTE_TARGET -C '
                              '$RTE_SDK/lib/librte_eal/linuxapp/igb_uio')
        self.execute_and_wait('modprobe uio')
        self.execute_and_wait('insmod %s/kmod/igb_uio.ko' %
                              S.getValue('RTE_TARGET'))
        self.execute_and_wait('./tools/dpdk_nic_bind.py --status')
        self.execute_and_wait(
            './tools/dpdk_nic_bind.py -u' ' ' +
            S.getValue('GUEST_NET1_PCI_ADDRESS')[self._number] + ' ' +
            S.getValue('GUEST_NET2_PCI_ADDRESS')[self._number])
        self.execute_and_wait(
            './tools/dpdk_nic_bind.py -b igb_uio' ' ' +
            S.getValue('GUEST_NET1_PCI_ADDRESS')[self._number] + ' ' +
            S.getValue('GUEST_NET2_PCI_ADDRESS')[self._number])
        self.execute_and_wait('./tools/dpdk_nic_bind.py --status')

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
                              'TX RS bit threshold=.+ - TXQ flags=0xf00')

    def _configure_l2fwd(self):
        """
        Configure VM to perform L2 forwarding between NICs by l2fwd module
        """
        self._configure_copy_sources('l2fwd')
        self._configure_disable_firewall()

        # build and configure system for l2fwd
        self.execute_and_wait('cd ' + S.getValue('GUEST_OVS_DPDK_DIR') +
                              '/l2fwd')
        self.execute_and_wait('export CC=gcc')

        self.execute_and_wait('make')
        self.execute_and_wait('insmod ' + S.getValue('GUEST_OVS_DPDK_DIR') +
                              '/l2fwd' + '/l2fwd.ko net1=' + self._net1 +
                              ' net2=' + self._net2)

    def _configure_linux_bridge(self):
        """
        Configure VM to perform L2 forwarding between NICs by linux bridge
        """
        self._configure_disable_firewall()

        self.execute('ifconfig ' + self._net1 + ' ' +
                     S.getValue('VANILLA_NIC1_IP_CIDR')[self._number])

        self.execute('ifconfig ' + self._net2 + ' ' +
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
