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

import os
import glob
import shutil
from conf import settings as S

#
# Support functions
#

def settings_update_paths():
    """ Configure paths to OVS, DPDK and QEMU sources and binaries based on
        selected vswitch type and src/binary switch. Data are taken from
        PATHS dictionary and after their processing they are stored inside TOOLS.
        PATHS dictionary have specific section for 'vswitch', 'qemu' and 'dpdk'
        Following processing is done for every item:
            'path' item - given string is checked for existence and prefixed with section name,
                e.g. TOOLS['dpdk_src'], TOOLS['vswitch_src'], etc
            'modules' item - every value from given list is checked for '.ko' suffix;
                In case it matches and it is not an absolute path to the module, then
                module name is prefixed with 'path' defined for the same section
                e.g. TOOLS['vswitch_modules']=['/tmp/vsperf/src_vanilla/ovs/ovs/datapath/linux/openvswitch.ko']
            all other items - if given string is relative path and item 'path' is defined for given section,
                then item content will be prefixed with 'path', otherwise tool name will be searched within
                standard system directories. Also any OS filename wildcards will be expanded
                to real path.
    """
    # set dpdk and ovs paths accorfing to VNF and VSWITCH
    paths_type = S.getValue('PATHS_TYPE')
    paths = {}
    paths['vswitch'] = S.getValue('PATHS')['vswitch'][S.getValue('VSWITCH')][paths_type]
    paths['dpdk'] = S.getValue('PATHS')['dpdk'][paths_type]
    paths['qemu'] = S.getValue('PATHS')['qemu'][paths_type]
    paths['paths'] = {}
    paths['paths']['ovs_var'] = S.getValue('PATHS')['vswitch']['ovs_var']
    paths['paths']['ovs_etc'] = S.getValue('PATHS')['vswitch']['ovs_etc']

    tools = {}
    for path_class in paths:
        for tool in paths[path_class]:
            tmp_tool = paths[path_class][tool]

            # store valid path of given class into tools dict
            if tool == 'path':
                if os.path.isdir(tmp_tool):
                    tools['{}_src'.format(path_class)] = tmp_tool
                    continue
                else:
                    raise RuntimeError('Path {} does not exist.'.format(tmp_tool))

            # store list of modules of given class into tools dict
            if tool == 'modules':
                tmp_modules = []
                for module in tmp_tool:
                    # add path to the .ko modules and check it for existence
                    if module.endswith('.ko') and not os.path.isabs(module):
                        module = os.path.join(paths[path_class]['path'], module)
                        if not os.path.exists(module):
                            raise RuntimeError('Cannot locate modlue {}'.format(module))

                    tmp_modules.append(module)

                tools['{}_modules'.format(path_class)] = tmp_modules
                continue

            # if path to the tool is relative, then 'path' will be prefixed
            # in case that 'path' is not defined, then tool will be searched
            # within standard system paths
            if not os.path.isabs(tmp_tool):
                if 'path' in paths[path_class]:
                    tmp_tool = os.path.join(paths[path_class]['path'], tmp_tool)
                elif shutil.which(tmp_tool):
                    tmp_tool = shutil.which(tmp_tool)
                else:
                    raise RuntimeError('Cannot locate tool {}'.format(tmp_tool))

            # expand OS wildcards in paths if needed
            if glob.has_magic(tmp_tool):
                tmp_glob = glob.glob(tmp_tool)
                if len(tmp_glob) == 0:
                    raise RuntimeError('Path to the {} is not valid: {}.'.format(tool, tmp_tool))
                elif len(tmp_glob) > 1:
                    raise RuntimeError('Path to the {} is ambiguous {}'.format(tool, tmp_glob))
                elif len(tmp_glob) == 1:
                    tmp_tool = tmp_glob[0]
            elif not os.path.exists(tmp_tool): 
                raise RuntimeError('Path to the {} is not valid: {}.'.format(tool, tmp_tool))

            tools[tool] = tmp_tool

    S.setValue('TOOLS', tools)
