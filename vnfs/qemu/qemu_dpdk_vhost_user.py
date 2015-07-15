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

import os
import time
import logging
import locale
import re
import subprocess

from tools import tasks
from conf import settings
from vnfs.vnf.vnf import IVnf

_QEMU_BIN = settings.getValue('QEMU_BIN')
_RTE_TARGET = settings.getValue('RTE_TARGET')

GUEST_MEMORY = '4096M'
GUEST_SMP = '2'
GUEST_CORE_BINDING = [(4, 5), (6, 7), (9, 10)]

GUEST_IMAGE = settings.getValue('GUEST_IMAGE')
GUEST_SHARE_DIR = settings.getValue('GUEST_SHARE_DIR')

GUEST_USERNAME = settings.getValue('GUEST_USERNAME')
GUEST_PASSWORD = settings.getValue('GUEST_PASSWORD')

GUEST_PROMPT_LOGIN = settings.getValue('GUEST_PROMPT_LOGIN')
GUEST_PROMPT_PASSWORD = settings.getValue('GUEST_PROMPT_PASSWORD')
GUEST_PROMPT = settings.getValue('GUEST_PROMPT')

_QEMU_GUEST_DPDK_PROMPT = settings.getValue('QEMU_GUEST_DPDK_PROMPT')
_QEMU_GUEST_TEST_PMD_PROMPT = settings.getValue('QEMU_GUEST_TEST_PMD_PROMPT')
_HUGEPAGE_DIR = settings.getValue('HUGEPAGE_DIR')

_GUEST_OVS_DPDK_DIR = '/root/ovs_dpdk'
_OVS_DPDK_SHARE = '/mnt/ovs_dpdk_share'

LOG_FILE_QEMU = os.path.join(
    settings.getValue('LOG_DIR'), settings.getValue('LOG_FILE_QEMU'))
LOG_FILE_GUEST_CMDS = os.path.join(
    settings.getValue('LOG_DIR'), settings.getValue('LOG_FILE_GUEST_CMDS'))

VHOST_DEV_PATH = os.path.join('/dev', settings.getValue('VHOST_DEV_FILE'))

_OVS_VAR_DIR = settings.getValue('OVS_VAR_DIR')
_GUEST_NET1_MAC = settings.getValue('GUEST_NET1_MAC')
_GUEST_NET2_MAC = settings.getValue('GUEST_NET2_MAC')
_GUEST_NET1_PCI_ADDRESS = settings.getValue('GUEST_NET1_PCI_ADDRESS')
_GUEST_NET2_PCI_ADDRESS = settings.getValue('GUEST_NET2_PCI_ADDRESS')

class QemuDpdkVhost(tasks.Process, IVnf):
    """
    Control an instance of QEMU with vHost user guest communication.
    """
    _bin = _QEMU_BIN
    _logfile = LOG_FILE_QEMU
    _cmd = None
    _expect = GUEST_PROMPT_LOGIN
    _proc_name = 'qemu'
    _number_vnfs = 0

    class GuestCommandFilter(logging.Filter):
        """
        Filter out strings beginning with 'guestcmd :'.
        """
        def filter(self, record):
            return record.getMessage().startswith(self.prefix)

    def __init__(self, memory=GUEST_MEMORY, cpus=GUEST_SMP,
                 monitor_path='/tmp', shared_path_host=GUEST_SHARE_DIR,
                 args='', timeout=120, deployment="P2P"):
        """
        Initialisation function.

        :param timeout: Time to wait for login prompt. If set to
            0 do not wait.
        :param number: Number of QEMU instance, used when multiple QEMU
            instances are started at once.
        :param args: Arguments to pass to QEMU.

        :returns: None
        """
        self._logger = logging.getLogger(__name__)
        self._number = self._number_vnfs
        self._number_vnfs = self._number_vnfs + 1
        self._logfile = self._logfile + str(self._number)
        self._log_prefix = 'guest_%d_cmd : ' % self._number
        self._timeout = timeout
        self._monitor = '%s/vm%dmonitor' % (monitor_path, self._number)

        name = 'Client%d' % self._number
        vnc = ':%d' % self._number
        self._cmd = ['sudo', '-E', self._bin, '-m', str(memory),
                     '-smp', str(cpus), '-cpu', 'host',
                     '-drive', 'if=scsi,file='+GUEST_IMAGE,
                     '-drive',
                     'if=scsi,file=fat:rw:%s,snapshot=off' % shared_path_host,
                     '-boot', 'c', '--enable-kvm', '-pidfile', '/tmp/vm1.pid',
                     '-monitor', 'unix:%s,server,nowait' % self._monitor,
                     '-object',
                     'memory-backend-file,id=mem,size=4096M,' +
                     'mem-path=' + _HUGEPAGE_DIR + ',share=on',
                     '-numa', 'node,memdev=mem -mem-prealloc',
                     '-chardev',
                     'socket,id=char0,path=' + _OVS_VAR_DIR + 'dpdkvhostuser0',
                     '-chardev',
                     'socket,id=char1,path=' + _OVS_VAR_DIR + 'dpdkvhostuser1',
                     '-netdev',
                     'type=vhost-user,id=net1,chardev=char0,vhostforce',
                     '-device',
                     'virtio-net-pci,mac=' + _GUEST_NET1_MAC +
                     ',netdev=net1,csum=off,gso=off,' +
                     'guest_tso4=off,guest_tso6=off,guest_ecn=off',
                     '-netdev',
                     'type=vhost-user,id=net2,chardev=char1,vhostforce',
                     '-device',
                     'virtio-net-pci,mac=' + _GUEST_NET2_MAC +
                     ',netdev=net2,csum=off,gso=off,' +
                     'guest_tso4=off,guest_tso6=off,guest_ecn=off',
                     '-nographic', '-vnc', str(vnc), '-name', name,
                     '-snapshot',
                    ]
        self._cmd.extend(args)
        self._configure_logging()

    def _configure_logging(self):
        """
        Configure logging.
        """
        self.GuestCommandFilter.prefix = self._log_prefix

        logger = logging.getLogger()
        cmd_logger = logging.FileHandler(
            filename=LOG_FILE_GUEST_CMDS + str(self._number))
        cmd_logger.setLevel(logging.DEBUG)
        cmd_logger.addFilter(self.GuestCommandFilter())
        logger.addHandler(cmd_logger)

    # startup/Shutdown

    def start(self):
        """
        Start QEMU instance, login and prepare for commands.
        """
        super(QemuDpdkVhost, self).start()
        self._affinitize()

        if self._timeout:
            self._login()
            self._config_guest_loopback()

    def stop(self):
        """
        Kill QEMU instance if it is alive.
        """
        self._logger.info('Killing QEMU...')

        super(QemuDpdkVhost, self).kill()

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

        self._child.sendline(GUEST_USERNAME)
        self._child.expect(GUEST_PROMPT_PASSWORD, timeout=5)
        self._child.sendline(GUEST_PASSWORD)

        self._expect_process(GUEST_PROMPT, timeout=5)

    def execute(self, cmd, delay=0):
        """
        Send ``cmd`` with no wait.

        Useful for asynchronous commands.

        :param cmd: Command to send to guest.
        :param timeout: Delay to wait after sending command before returning.

        :returns: None
        """
        self._logger.debug('%s%s', self._log_prefix, cmd)
        self._child.sendline(cmd)
        time.sleep(delay)

    def wait(self, msg=GUEST_PROMPT, timeout=30):
        """
        Wait for ``msg``.

        :param msg: Message to wait for from guest.
        :param timeout: Time to wait for message.

        :returns: None
        """
        self._child.expect(msg, timeout=timeout)

    def execute_and_wait(self, cmd, timeout=30, prompt=GUEST_PROMPT):
        """
        Send ``cmd`` and wait ``timeout`` seconds for prompt.

        :param cmd: Command to send to guest.
        :param timeout: Time to wait for prompt.

        :returns: None
        """
        self.execute(cmd)
        self.wait(prompt, timeout=timeout)

    def send_and_pass(self, cmd, timeout=30):
        """
        Send ``cmd`` and wait ``timeout`` seconds for it to pass.

        :param cmd: Command to send to guest.
        :param timeout: Time to wait for prompt before checking return code.

        :returns: None
        """
        self.execute(cmd)
        self.wait(GUEST_PROMPT, timeout=timeout)
        self.execute('echo $?')
        self._child.expect('^0$', timeout=1)  # expect a 0
        self.wait(GUEST_PROMPT, timeout=timeout)

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

        cur_locale = locale.getlocale()[1]
        proc = subprocess.Popen(
            ('echo', 'info cpus'), stdout=subprocess.PIPE)
        output = subprocess.check_output(
            ('sudo', 'socat', '-', 'UNIX-CONNECT:%s' % self._monitor),
            stdin=proc.stdout)
        proc.wait()

        for cpu in range(0, int(GUEST_SMP)):
            match = None
            for line in output.decode(cur_locale).split('\n'):
                match = re.search(thread_id % cpu, line)
                if match:
                    self._affinitize_pid(
                        GUEST_CORE_BINDING[self._number - 1][cpu],
                        match.group(1))
                    break

            if not match:
                self._logger.error('Failed to affinitize guest core #%d. Could'
                                   ' not parse tid.', cpu)

    def _config_guest_loopback(self):
        '''# mount hugepages
        # Guest images _should_ have 1024 hugepages by default,
        # but just in case:'''
        self.execute_and_wait('sysctl vm.nr_hugepages=1024')
        self.execute_and_wait('mkdir -p /dev/hugepages')
        self.execute_and_wait(
            'mount -t hugetlbfs hugetlbfs /dev/hugepages')

        # mount shared directory
        self.execute_and_wait('umount ' + _OVS_DPDK_SHARE)
        self.execute_and_wait('rm -rf ' + _GUEST_OVS_DPDK_DIR)
        self.execute_and_wait('mkdir -p ' + _OVS_DPDK_SHARE)
        self.execute_and_wait('mount -o iocharset=utf8 /dev/sdb1 ' +
                              _OVS_DPDK_SHARE)
        self.execute_and_wait('mkdir -p ' + _GUEST_OVS_DPDK_DIR)
        self.execute_and_wait('cp -a ' + _OVS_DPDK_SHARE + '/* ' + _GUEST_OVS_DPDK_DIR)
        # Get VM info
        self.execute_and_wait('cat /etc/default/grub')

        # Disable services (F16)
        self.execute_and_wait('systemctl status iptables.service')
        self.execute_and_wait('systemctl stop iptables.service')

        # build and configure system for dpdk
        self.execute_and_wait('cd ' + _GUEST_OVS_DPDK_DIR + '/DPDK',
                              prompt=_QEMU_GUEST_DPDK_PROMPT)

        self.execute_and_wait('export CC=gcc', prompt=_QEMU_GUEST_DPDK_PROMPT)
        self.execute_and_wait('export RTE_SDK=' + _GUEST_OVS_DPDK_DIR + '/DPDK',
                              prompt=_QEMU_GUEST_DPDK_PROMPT)
        self.execute_and_wait('export RTE_TARGET=%s' % _RTE_TARGET,
                              prompt=_QEMU_GUEST_DPDK_PROMPT)

        self.execute_and_wait('make uninstall', prompt=_QEMU_GUEST_DPDK_PROMPT)
        self.execute_and_wait('make install T=%s -j 2' % _RTE_TARGET,
                              timeout=300, prompt=_QEMU_GUEST_DPDK_PROMPT)

        self.execute_and_wait('modprobe uio', prompt=_QEMU_GUEST_DPDK_PROMPT)
        self.execute_and_wait('insmod %s/kmod/igb_uio.ko' % _RTE_TARGET,
                              prompt=_QEMU_GUEST_DPDK_PROMPT)
        self.execute_and_wait('./tools/dpdk_nic_bind.py --status',
                              prompt=_QEMU_GUEST_DPDK_PROMPT)
        self.execute_and_wait('./tools/dpdk_nic_bind.py -b igb_uio'
                              ' ' + _GUEST_NET1_PCI_ADDRESS + ' '
                              + _GUEST_NET2_PCI_ADDRESS,
                              prompt=_QEMU_GUEST_DPDK_PROMPT)

        # build and run 'test-pmd'
        self.execute_and_wait('cd ' + _GUEST_OVS_DPDK_DIR +
                              '/DPDK/app/test-pmd',
                              prompt=_QEMU_GUEST_TEST_PMD_PROMPT)
        self.execute_and_wait('make clean', prompt=_QEMU_GUEST_TEST_PMD_PROMPT)
        self.execute_and_wait('make', prompt=_QEMU_GUEST_TEST_PMD_PROMPT)
        self.execute_and_wait('./testpmd -c 0x3 -n 4 --socket-mem 512 --'
                              ' --burst=64 -i --txqflags=0xf00 ' +
                              '--disable-hw-vlan', 20, "Done")
        self.execute('set fwd mac_retry', 1)
        self.execute_and_wait('start', 20,
                              'TX RS bit threshold=0 - TXQ flags=0xf00')


if __name__ == '__main__':
    import sys

    with QemuDpdkVhost() as vm1:
        print(
            '\n\n************************\n'
            'Basic command line suitable for ls, cd, grep and cat.\n If you'
            ' try to run Vim from here you\'re going to have a bad time.\n'
            'For more complex tasks please use \'vncviewer :1\' to connect to'
            ' this VM\nUsername: %s Password: %s\nPress ctrl-C to quit\n'
            '************************\n' % (GUEST_USERNAME, GUEST_PASSWORD))

        if sys.argv[1]:
            with open(sys.argv[1], 'r') as file_:
                for logline in file_:
                    # lines are of format:
                    #   guest_N_cmd : <command>
                    # and we only want the <command> piece
                    cmdline = logline.split(':')[1].strip()

                    # use a no timeout since we don't know how long we
                    # should wait
                    vm1.send_and_wait(cmdline, timeout=-1)

        while True:
            USER_INPUT = input()
            vm1.send_and_wait(USER_INPUT, timeout=5)
