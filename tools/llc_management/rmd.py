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
Perform L3-cache allocations for different workloads- VNFs, PMDs, vSwitch etc.
based on the user-defined policies. This is done using Intel-RMD.
Details about RMD can be found in: https://github.com/intel/rmd
"""

# pylint: disable=invalid-name

import itertools
import json
import logging
import math
import socket

from collections import defaultdict
from conf import settings as S
from tools.llc_management import resthttp

DEFAULT_PORT = 8888
DEFAULT_SERVER = '127.0.0.1'
DEFAULT_VERSION = 'v1'


def cpumask2coreids(mask):
    """
    Convert CPU mask in hex-string to list of core-IDs
    """
    intmask = int(mask, 16)
    i = 1
    coreids = []
    while i <= intmask:
        if i & intmask:
            coreids.append(str(math.frexp(i)[1] - 1))
        i = i << 1
    return coreids


def get_cos(category):
    """
    Obtain the Classof service for a particular category
    """
    return S.getValue(category.upper() + '_COS')


def get_minmax(category):
    """
    Obtain the min-max values for a particular category
    """
    return S.getValue(category.upper() + '_CA')


def guest_vm_settings_expanded(cores):
    """
    Check if are running pv+p mode
    """
    for core in cores:
        if isinstance(core, str) and '#' in core:
            return False
    return True


class IrmdHttp(object):
    """
    Intel RMD ReST API wrapper object
    """

    def __init__(self, server=None, port=None, api_version=None):
        if not port:
            server = DEFAULT_SERVER
        if not port:
            port = DEFAULT_PORT
        if not api_version:
            api_version = DEFAULT_VERSION
        url = resthttp.RestHttp.url('http', server, port, api_version)
        rest = resthttp.RestHttp(url, None, None, False, True)
        try:
            rest.get_request('workloads')
        except (socket.error, resthttp.ConnError,
                resthttp.RestHttpError):
            raise RuntimeError('Cannot connect to RMD server: %s:%s' %
                               (server, port))
        self._rest = rest
        self.workloadids = []
        self._logger = logging.getLogger(__name__)

    def setup_cacheways(self, affinity_map):
        """
        Sets up the cacheways using RMD apis.
        """
        for cos_cat in affinity_map:
            if S.getValue('POLICY_TYPE') == 'COS':
                params = {'core_ids': affinity_map[cos_cat],
                          'policy': get_cos(cos_cat)}
            else:
                minmax = get_minmax(cos_cat)
                if len(minmax) < 2:
                    return
                params = {'core_ids': affinity_map[cos_cat],
                          'min_cache': minmax[0],
                          'max_cache': minmax[1]}
            try:
                _, data = self._rest.post_request('workloads', None,
                                                  params)
                if 'id' in data:
                    wl_id = data['id']
                    self.workloadids.append(wl_id)

            except resthttp.RestHttpError as e:
                if str(e).find('already exists') >= 0:
                    raise RuntimeError("The cacheway already exist")
                else:
                    raise RuntimeError('Failed to connect: ' + str(e))

    def reset_all_cacheways(self):
        """
        Resets the cacheways
        """
        try:
            for wl_id in self.workloadids:
                self._rest.delete_request('workloads', str(wl_id))
        except resthttp.RestHttpError as e:
            raise RuntimeError('Failed to connect: ' + str(e))

    def log_allocations(self):
        """
        Log the current cacheway settings.
        """
        try:
            _, data = self._rest.get_request('workloads')
            self._logger.info("Current Allocations: %s",
                              json.dumps(data, indent=4, sort_keys=True))
        except resthttp.RestHttpError as e:
            raise RuntimeError('Failed to connect: ' + str(e))


class CacheAllocator(object):
    """
    This class exposes APIs for VSPERF to perform
    Cache-allocation management operations.
    """

    def __init__(self):
        port = S.getValue('RMD_PORT')
        api_version = S.getValue('RMD_API_VERSION')
        server_ip = S.getValue('RMD_SERVER_IP')
        self.irmd_manager = IrmdHttp(str(server_ip), str(port),
                                     str(api_version))

    def setup_llc_allocation(self):
        """
        Wrapper for settingup cacheways
        """
        cpumap = defaultdict(list)
        vswitchmask = S.getValue('VSWITCHD_DPDK_CONFIG')['dpdk-lcore-mask']
        vnfcores = list(itertools.chain.from_iterable(
            S.getValue('GUEST_CORE_BINDING')))
        if not guest_vm_settings_expanded(vnfcores):
            vnfcores = None
        nncores = None
        if S.getValue('LOADGEN') == 'StressorVM':
            nncores = list(itertools.chain.from_iterable(
                S.getValue('NN_CORE_BINDING')))
        pmdcores = cpumask2coreids(S.getValue('VSWITCH_PMD_CPU_MASK'))
        vswitchcores = cpumask2coreids(vswitchmask)
        if vswitchcores:
            cpumap['vswitch'] = vswitchcores
        if vnfcores:
            cpumap['vnf'] = vnfcores
        if pmdcores:
            cpumap['pmd'] = pmdcores
        if nncores:
            cpumap['noisevm'] = nncores
        self.irmd_manager.setup_cacheways(cpumap)

    def cleanup_llc_allocation(self):
        """
        Wrapper for cacheway cleanup
        """
        self.irmd_manager.reset_all_cacheways()

    def log_allocations(self):
        """
        Wrapper for logging cacheway allocations
        """
        self.irmd_manager.log_allocations()
