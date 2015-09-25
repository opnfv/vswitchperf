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

import os
import logging
import locale
import re
import subprocess

from conf import settings as S
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
        :param timeout: Time to wait for login prompt. If set to
            0 do not wait.
        :param number: Number of QEMU instance, used when multiple QEMU
            instances are started at once.
        :param args: Arguments to pass to QEMU.

        :returns: None
        """
        super(IVnfQemu, self).__init__()
        self._logger = logging.getLogger(__name__)
        self._logfile = os.path.join(
            S.getValue('LOG_DIR'),
            S.getValue('LOG_FILE_QEMU')) + str(self._number)
        self._timeout = 120
        self._monitor = '%s/vm%dmonitor' % ('/tmp', self._number)

        name = 'Client%d' % self._number
        vnc = ':%d' % self._number
        # don't use taskset to affinize main qemu process; It causes hangup
        # of 2nd VM in case of DPDK. It also slows down VM responsivnes.
        self._cmd = ['sudo', '-E', S.getValue('QEMU_BIN'),
                     '-m', S.getValue('GUEST_MEMORY')[self._number],
                     '-smp', str(S.getValue('GUEST_SMP')[self._number]),
                     '-cpu', 'host',
                     '-drive', 'if=scsi,file=' +
                     S.getValue('GUEST_IMAGE')[self._number],
                     '-drive',
                     'if=scsi,file=fat:rw:%s,snapshot=off' %
                     S.getValue('GUEST_SHARE_DIR')[self._number],
                     '-boot', 'c', '--enable-kvm',
                     '-monitor', 'unix:%s,server,nowait' % self._monitor,
                     '-object',
                     'memory-backend-file,id=mem,size=' +
                     str(S.getValue('GUEST_MEMORY')[self._number]) + 'M,' +
                     'mem-path=' + S.getValue('HUGEPAGE_DIR') + ',share=on',
                     '-numa', 'node,memdev=mem -mem-prealloc',
                     '-nographic', '-vnc', str(vnc), '-name', name,
                     '-snapshot', '-net none', '-no-reboot',
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
        self._affinitize()

        if self._timeout:
            self._login()
            self._config_guest_loopback()

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

        cur_locale = locale.getlocale()[1]
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
        Configure VM to run VNF (e.g. port forwarding application)
        """
        pass

    def wait(self, prompt=S.getValue('GUEST_PROMPT'), timeout=30):
        super(IVnfQemu, self).wait(prompt=prompt, timeout=timeout)

    def execute_and_wait(self, cmd, timeout=30,
                         prompt=S.getValue('GUEST_PROMPT')):
        super(IVnfQemu, self).execute_and_wait(cmd, timeout=timeout,
                                               prompt=prompt)
