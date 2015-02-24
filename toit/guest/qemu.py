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

"""
Automation of QEMU hypervisor.

Part of 'toit' - The OVS Integration Testsuite.
"""

from __future__ import print_function

import os
import time
import logging
import re
import subprocess

from toit import utils
from toit.conf import settings

# if this is not set, use the QEMU binary from the PATH
if getattr(settings, 'QEMU_DIR'):
    QEMU_BIN = os.path.join(getattr(settings, 'QEMU_DIR'), 'x86_64-softmmu',
                            getattr(settings, 'QEMU_BIN'))
else:
    QEMU_BIN = getattr(settings, 'QEMU_BIN')
if getattr(settings, 'QEMU_WRAP_DIR'):
    QEMU_WRAP_BIN = os.path.join(getattr(settings, 'QEMU_WRAP_DIR'),
                                 getattr(settings, 'QEMU_WRAP_BIN'))
else:
    QEMU_WRAP_BIN = getattr(settings, 'QEMU_WRAP_BIN')

GUEST_MEMORY = '4096M'
GUEST_SMP = '2'
GUEST_CORE_BINDING = [(4, 5), (6, 7), (9, 10)]

GUEST_IMAGE = getattr(settings, 'GUEST_IMAGE')
GUEST_SHARE_DIR = getattr(settings, 'GUEST_SHARE_DIR')

GUEST_USERNAME = getattr(settings, 'GUEST_USERNAME')
GUEST_PASSWORD = getattr(settings, 'GUEST_PASSWORD')

GUEST_PROMPT_LOGIN = getattr(settings, 'GUEST_PROMPT_LOGIN')
GUEST_PROMPT_PASSWORD = getattr(settings, 'GUEST_PROMPT_PASSWORD')
GUEST_PROMPT = getattr(settings, 'GUEST_PROMPT')

LOG_FILE_QEMU = os.path.join(
    getattr(settings, 'LOG_DIR'), getattr(settings, 'LOG_FILE_QEMU'))
LOG_FILE_GUEST_CMDS = os.path.join(
    getattr(settings, 'LOG_DIR'), getattr(settings, 'LOG_FILE_GUEST_CMDS'))


class Qemu(utils.Process):
    """
    Control an instance of QEMU.
    """
    _bin = QEMU_BIN
    _logfile = LOG_FILE_QEMU
    _cmd = None
    _expect = GUEST_PROMPT_LOGIN
    _proc_name = 'qemu'

    class GuestCommandFilter(logging.Filter):
        """
        Filter out strings beginning with 'guestcmd :'.
        """
        def filter(self, record):
            return record.getMessage().startswith(self.prefix)

    def __init__(self, timeout=120, number=1, args=None):
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
        self._logfile = self._logfile + str(number)
        self._log_prefix = 'guest_%d_cmd : ' % number
        self._timeout = timeout
        self._number = number
        self._monitor = '/tmp/vm%dmonitor' % number

        name = 'Client%d' % number
        vnc = ':%d' % number
        self._cmd = [
            'sudo', '-E', self._bin, '-cpu', 'host', '-boot', 'c',
            '-m', GUEST_MEMORY, '-smp', GUEST_SMP, '-hda', GUEST_IMAGE,
            '-drive', 'file=fat:rw:%s,snapshot=off' % GUEST_SHARE_DIR,
            '--enable-kvm', '-nographic', '-vnc', vnc, '-name', name,
            '-monitor', 'unix:%s,server,nowait' % self._monitor, '-snapshot']

        if args:
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
        super(Qemu, self).start()

        self.affinitize()

        if self._timeout:
            self.login()

    def kill(self):
        """
        Kill QEMU instance if it is alive.
        """
        self._logger.info('Killing QEMU...')

        super(Qemu, self).kill()

    # helper functions

    def login(self, timeout=120):
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

    def send(self, cmd, delay=0):
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

    def send_and_wait(self, cmd, timeout=30):
        """
        Send ``cmd`` and wait ``timeout`` seconds for prompt.

        :param cmd: Command to send to guest.
        :param timeout: Time to wait for prompt.

        :returns: None
        """
        self.send(cmd)
        self.wait(GUEST_PROMPT, timeout=timeout)

    def send_and_pass(self, cmd, timeout=30):
        """
        Send ``cmd`` and wait ``timeout`` seconds for it to pass.

        :param cmd: Command to send to guest.
        :param timeout: Time to wait for prompt before checking return code.

        :returns: None
        """
        self.send(cmd)
        self.wait(GUEST_PROMPT, timeout=timeout)
        self.send('echo $?')
        self._child.expect('^0$', timeout=1)  # expect a 0
        self.wait(GUEST_PROMPT, timeout=timeout)

    def affinitize(self, core=None):
        """
        Affinitize the SMP cores of a QEMU instance.

        This is a bit of a hack. The 'socat' utility is used to
        interact with the QEMU HMP. This is necessary due to the lack
        of QMP in older versions of QEMU, like v1.6.2. In future
        releases, this should be replaced with calls to libvirt or
        another Python-QEMU wrapper library.

        :param core: Core to affinitize QEMU process to.

        :returns: None
        """
        thread_id = (r'.* CPU #%d: .* thread_id=(\d+)')

        self._logger.info('Affinitizing guest...')

        proc = subprocess.Popen(
            ('echo', 'info cpus'), stdout=subprocess.PIPE)
        output = subprocess.check_output(
            ('sudo', 'socat', '-', 'UNIX-CONNECT:%s' % self._monitor),
            stdin=proc.stdout)
        proc.wait()

        for cpu in range(0, int(GUEST_SMP)):
            match = None
            for line in output.split('\n'):
                match = re.search(thread_id % cpu, line)
                if match:
                    self._affinitize_pid(
                        GUEST_CORE_BINDING[self._number - 1][cpu],
                        match.group(1))
                    break

            if not match:
                self._logger.error('Failed to affinitize guest core #%d. Could'
                                   ' not parse tid.', cpu)


class QemuWrap(Qemu):
    """
    Control an instance of 'qemu-wrap.py'.
    """
    _bin = QEMU_WRAP_BIN
    _proc_name = 'qemu-wrap'


if __name__ == '__main__':
    import sys

    with Qemu() as vm1:
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
            USER_INPUT = raw_input()
            vm1.send_and_wait(USER_INPUT, timeout=5)
