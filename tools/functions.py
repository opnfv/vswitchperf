# Copyright 2016-2017 Intel Corporation.
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
import logging
import glob
import shutil
from conf import settings as S

MAX_L4_FLOWS = 65536

#
# Support functions
#
# pylint: disable=too-many-branches
def settings_update_paths():
    """ Configure paths to OVS, DPDK and QEMU sources and binaries based on
        selected vswitch type and src/binary switch. Data are taken from
        PATHS dictionary and after their processing they are stored inside TOOLS.
        PATHS dictionary has specific section for 'vswitch', 'qemu' and 'dpdk'
        Following processing is done for every item:
            item 'type' - string, which defines the type of paths ('src' or 'bin') to be selected
                  for a given section:
                      'src' means, that VSPERF will use OVS, DPDK or QEMU built from sources
                          e.g. by execution of systems/build_base_machine.sh script during VSPERF
                          installation
                      'bin' means, that VSPERF will use OVS, DPDK or QEMU binaries installed
                          in the OS, e.g. via OS specific packaging system
            item 'path' - string with valid path; Its content is checked for existence, prefixed
                  with section name and stored into TOOLS for later use
                  e.g. TOOLS['dpdk_src'] or TOOLS['vswitch_src']
            item 'modules' - list of strings; Every value from given list is checked for '.ko'
                  suffix. In case it matches and it is not an absolute path to the module, then
                  module name is prefixed with 'path' defined for the same section
                  e.g. TOOLS['vswitch_modules'] = [
                      '/tmp/vsperf/src_vanilla/ovs/ovs/datapath/linux/openvswitch.ko']
            all other items - string - if given string is a relative path and item 'path'
                  is defined for a given section, then item content will be prefixed with
                  content of the 'path'. Otherwise tool name will be searched within
                  standard system directories. Also any OS filename wildcards will be
                  expanded to the real path. At the end of processing, every absolute
                  path is checked for its existence. In case that temporary path (i.e. path
                  with '_tmp' suffix) doesn't exist, then log will be written and vsperf will
                  continue. If any other path will not exist, then vsperf execution will
                  be terminated with runtime error.

        Note: In case that 'bin' type is set for DPDK, then TOOLS['dpdk_src'] will be set to
        the value of PATHS['dpdk']['src']['path']. The reason is, that VSPERF uses downloaded
        DPDK sources to copy DPDK and testpmd into the GUEST, where testpmd is built. In case,
        that DPDK sources are not available, then vsperf will continue with test execution,
        but testpmd can't be used as a guest loopback. This is useful in case, that other guest
        loopback applications (e.g. buildin) are used by CI jobs, etc.
    """
    # set dpdk and ovs paths according to VNF, VSWITCH and TRAFFICGEN selection
    paths = {}
    if S.getValue("mode") != 'trafficgen':
        # VSWITCH & (probably) VNF are needed
        vswitch_type = S.getValue('PATHS')['vswitch'][S.getValue('VSWITCH')]['type']
        paths['vswitch'] = S.getValue('PATHS')['vswitch'][S.getValue('VSWITCH')][vswitch_type]
        paths['dpdk'] = S.getValue('PATHS')['dpdk'][S.getValue('PATHS')['dpdk']['type']]
        paths['qemu'] = S.getValue('PATHS')['qemu'][S.getValue('PATHS')['qemu']['type']]
        paths['paths'] = {}
        paths['paths']['ovs_var_tmp'] = S.getValue('PATHS')['vswitch']['ovs_var_tmp']
        paths['paths']['ovs_etc_tmp'] = S.getValue('PATHS')['vswitch']['ovs_etc_tmp']

    if S.getValue("mode") != 'trafficgen-off':
        # TRAFFCIGEN is required
        if S.getValue('TRAFFICGEN') in S.getValue('PATHS')['trafficgen']:
            tmp_trafficgen = S.getValue('PATHS')['trafficgen'][S.getValue('TRAFFICGEN')]
            paths['trafficgen'] = tmp_trafficgen[tmp_trafficgen['type']]

    tools = {}
    # pylint: disable=too-many-nested-blocks
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
                if tool.endswith('_tmp'):
                    logging.getLogger().debug('Temporary path to the %s does not '
                                              'exist: %s', tool, tmp_tool)
                else:
                    raise RuntimeError('Path to the {} is not valid: {}'.format(tool, tmp_tool))

            tools[tool] = tmp_tool

    # ensure, that dpkg_src for bin will be set to downloaded DPDK sources, so it can
    # be copied to the guest share dir and used by GUEST to build and run testpmd
    # Validity of the path is not checked by purpose, so user can use VSPERF without
    # downloading DPDK sources. In that case guest loopback can't be set to 'testpmd'
    if S.getValue('PATHS')['dpdk']['type'] == 'bin':
        tools['dpdk_src'] = S.getValue('PATHS')['dpdk']['src']['path']

    S.setValue('TOOLS', tools)

def check_traffic(traffic):
    """Check traffic definition and correct it if possible.
    """
    # check if requested networking layers make sense
    if traffic['l4']['enabled']:
        if not traffic['l3']['enabled']:
            raise RuntimeError('TRAFFIC misconfiguration: l3 must be enabled '
                               'if l4 is enabled.')

    # check if multistream configuration makes sense
    if traffic['multistream']:
        if traffic['stream_type'] == 'L3':
            if not traffic['l3']['enabled']:
                raise RuntimeError('TRAFFIC misconfiguration: l3 must be '
                                   'enabled if l3 streams are requested.')
        if traffic['stream_type'] == 'L4':
            if not traffic['l4']['enabled']:
                raise RuntimeError('TRAFFIC misconfiguration: l4 must be '
                                   'enabled if l4 streams are requested.')

            # in case of UDP ports we have only 65536 (0-65535) unique options
            if traffic['multistream'] > MAX_L4_FLOWS:
                logging.getLogger().warning(
                    'Requested amount of L4 flows %s is bigger than number of '
                    'transport protocol ports. It was set to %s.',
                    traffic['multistream'], MAX_L4_FLOWS)
                traffic['multistream'] = MAX_L4_FLOWS

    return traffic
