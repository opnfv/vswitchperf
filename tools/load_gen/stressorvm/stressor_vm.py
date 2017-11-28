# Copyright 2016-2017 Spirent Communications.
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
Wrapper file to create and manage Stressor-VM as loadgen
"""

import hashlib
import logging
import os
from tools import tasks
from tools.load_gen.load_gen import ILoadGenerator
from conf import settings as S


def mac_hash(strid):
    """
    return a valid virtual MAC addr
    """
    mac_addr = hashlib.md5()
    mac_addr.update(strid.encode('utf-8'))
    mac_addr = mac_addr.hexdigest()[0:8]
    return "52:54:%s%s:%s%s:%s%s:%s%s" % tuple(mac_addr)


class QemuVM(tasks.Process):
    """
    Class for controling an instance of QEMU
    """
    def __init__(self, index):
        self._running = False
        self._logger = logging.getLogger(__name__)
        self._number = index
        pnumber = int(S.getValue('NN_BASE_VNC_PORT')) + self._number
        cpumask = ",".join(S.getValue('NN_CORE_BINDING')[self._number])
        self._monitor = '%s/vm%dmonitor' % ('/tmp', pnumber)
        self._logfile = (os.path.join(S.getValue('LOG_DIR'),
                                      S.getValue('NN_LOG_FILE')) +
                         str(self._number))
        self._log_prefix = 'vnf_%d_cmd : ' % pnumber
        name = 'NN%d' % index
        vnc = ':%d' % pnumber
        self._shared_dir = '%s/qemu%d_share' % ('/tmp', pnumber)
        if not os.path.exists(self._shared_dir):
            os.makedirs(self._shared_dir)
        self.nics_nr = S.getValue('NN_NICS_NR')[self._number]
        self.image = S.getValue('NN_IMAGE')[self._number]
        self._cmd = ['sudo', '-E', 'taskset', '-c', cpumask,
                     S.getValue('TOOLS')['qemu-system'],
                     '-m', S.getValue('NN_MEMORY')[self._number],
                     '-smp', S.getValue('NN_SMP')[self._number],
                     '-cpu', 'host,migratable=off',
                     '-drive', 'if={},file='.format(
                         S.getValue('NN_BOOT_DRIVE_TYPE')[self._number]) +
                     self.image, '-boot',
                     'c', '--enable-kvm',
                     '-monitor', 'unix:%s,server,nowait' % self._monitor,
                     '-nographic', '-vnc', str(vnc), '-name', name,
                     '-snapshot', '-net none', '-no-reboot',
                     '-drive',
                     'if=%s,format=raw,file=fat:rw:%s,snapshot=off' %
                     (S.getValue('NN_SHARED_DRIVE_TYPE')[self._number],
                      self._shared_dir)
                     ]
        self.gen_virtio_dev()

    def gen_virtio_dev(self):
        """
        generate `-netdev` and `-device` args for qemu
        """
        for nid in range(int(self.nics_nr)):
            mac = mac_hash(self.image + str(nid))
            self._cmd += ['-netdev', 'type=tap,id=hostnet' + str(nid) +
                          ',script=no,downscript=no,vhost=on',
                          '-device',
                          'virtio-net-pci,netdev=hostnet' +
                          str(nid) + ',mac=' + mac +
                          ',csum=off,gso=off,' +
                          'guest_tso4=off,guest_tso6=off,guest_ecn=off']

    def start(self):
        """
        Start QEMU instance
        """
        # insert vanilla ovs specific modules
        tasks.run_task(['sudo', 'modprobe', 'vhost_net'], self._logger,
                       'Loading vhost_net module...', True)
        super(QemuVM, self).start()
        self._running = True

    def stop(self, sig, slp):
        """
        Stops VNF instance.
        """
        if self._running:
            self._logger.info('Killing VNF...')
            # force termination of VNF and wait to terminate; It will avoid
            # sporadic reboot of host.
            super(QemuVM, self).kill(signal=sig, sleep=slp)
        # remove shared dir if it exists to avoid issues with file consistency
        if os.path.exists(self._shared_dir):
            tasks.run_task(['rm', '-f', '-r', self._shared_dir], self._logger,
                           'Removing content of shared directory...', True)
        self._running = False


class StressorVM(ILoadGenerator):
    def __init__(self, config):
        self.qvm_list = []
        for vmindex in range(int(S.getValue('NN_COUNT'))):
            qvm = QemuVM(vmindex)
            self.qvm_list.append(qvm)

    def start(self):
        """Start stressor VMs
        """
        for nvm in self.qvm_list:
            nvm.start()

    def kill(self, signal='-9', sleep=2):
        """
        Stop Stressor VMs
        """
        for nvm in self.qvm_list:
            nvm.stop(signal, sleep)
