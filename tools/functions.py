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

"""Various helper functions
"""

from conf import settings

#
# Support functions
#

def settings_update_paths():
    """ Configure paths to OVS and DPDK based on VSWITCH and VNF values
    """
    # set dpdk and ovs paths accorfing to VNF and VSWITCH
    if settings.getValue('VSWITCH').endswith('Vanilla'):
        # settings paths for Vanilla
        settings.setValue('OVS_DIR', (settings.getValue('OVS_DIR_VANILLA')))
    elif settings.getValue('VSWITCH').endswith('Vhost'):
        if settings.getValue('VNF').endswith('Cuse'):
            # settings paths for Cuse
            settings.setValue('RTE_SDK', (settings.getValue('RTE_SDK_CUSE')))
            settings.setValue('OVS_DIR', (settings.getValue('OVS_DIR_CUSE')))
        else:
            # settings paths for VhostUser
            settings.setValue('RTE_SDK', (settings.getValue('RTE_SDK_USER')))
            settings.setValue('OVS_DIR', (settings.getValue('OVS_DIR_USER')))
    else:
        # default - set to VHOST USER but can be changed during enhancement
        settings.setValue('RTE_SDK', (settings.getValue('RTE_SDK_USER')))
        settings.setValue('OVS_DIR', (settings.getValue('OVS_DIR_USER')))
