# Copyright 2015-2017 Intel Corporation.
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
""" VNF Controller interface
"""

import logging
import pexpect
from conf import settings
from vnfs.vnf.vnf import IVnf

class VnfController(object):
    """VNF controller class

    Used to set-up and control VNFs for specified scenario

    Attributes:
        _vnf_class: A class object representing the VNF to be used.
        _deployment: A string describing the scenario to set-up in the
            constructor.
        _vnfs: A list of vnfs controlled by the controller.
    """

    def __init__(self, deployment, vnf_class, extra_vnfs):
        """Sets up the VNF infrastructure based on deployment scenario

        :param vnf_class: The VNF class to be used.
        :param extra_vnfs: The number of VNFs not involved in given
            deployment scenario. It will be used to correctly expand
            configuration values and initialize shared dirs. This parameter
            is used in case, that additional VNFs are executed by TestSteps.
        """
        # reset VNF ID counter for each testcase
        IVnf.reset_vnf_counter()

        # setup controller with requested number of VNFs
        self._logger = logging.getLogger(__name__)
        self._vnf_class = vnf_class
        self._deployment = deployment.lower()
        self._vnfs = []
        if self._deployment == 'pvp':
            vm_number = 1
        elif (self._deployment.startswith('pvvp') or
              self._deployment.startswith('pvpv')):
            if len(self._deployment) > 4:
                vm_number = int(self._deployment[4:])
            else:
                vm_number = 2
        else:
            # VnfController is created for all deployments, including deployments
            # without VNFs like p2p
            vm_number = 0

        if vm_number + extra_vnfs > 0:
            self._logger.debug('Check configuration for %s guests.', vm_number + extra_vnfs)
            settings.check_vm_settings(vm_number + extra_vnfs)
            # enforce that GUEST_NIC_NR is 1 or even number of NICs
            updated = False
            nics_nr = settings.getValue('GUEST_NICS_NR')
            for index, value in enumerate(nics_nr):
                if value > 1 and value % 2:
                    updated = True
                    nics_nr[index] = int(value / 2) * 2
            if updated:
                settings.setValue('GUEST_NICS_NR', nics_nr)
                self._logger.warning('Odd number of NICs was detected. Configuration '
                                     'was updated to GUEST_NICS_NR = %s',
                                     settings.getValue('GUEST_NICS_NR'))

        if vm_number:
            self._vnfs = [vnf_class() for _ in range(vm_number)]

            self._logger.debug('__init__ ' + str(len(self._vnfs)) +
                               ' VNF[s] with ' + ' '.join(map(str, self._vnfs)))

    def get_vnfs(self):
        """Returns a list of vnfs controlled by this controller.
        """
        self._logger.debug('get_vnfs ' + str(len(self._vnfs)) +
                           ' VNF[s] with ' + ' '.join(map(str, self._vnfs)))
        return self._vnfs

    def get_vnfs_number(self):
        """Returns a number of vnfs controlled by this controller.
        """
        self._logger.debug('get_vnfs_number %s VNF[s]', str(len(self._vnfs)))
        return len(self._vnfs)

    def start(self):
        """Boots all VNFs set-up by __init__.

        This is a blocking function.
        """
        self._logger.debug('start ' + str(len(self._vnfs)) +
                           ' VNF[s] with ' + ' '.join(map(str, self._vnfs)))
        try:
            for vnf in self._vnfs:
                vnf.start()
        except pexpect.TIMEOUT:
            self.stop()
            raise

    def stop(self):
        """Stops all VNFs set-up by __init__.

        This is a blocking function.
        """
        self._logger.debug('stop ' + str(len(self._vnfs)) +
                           ' VNF[s] with ' + ' '.join(map(str, self._vnfs)))
        for vnf in self._vnfs:
            vnf.stop()

    def __enter__(self):
        self.start()

    def __exit__(self, type_, value, traceback):
        self.stop()
