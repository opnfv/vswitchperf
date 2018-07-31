# Copyright 2015-2018 Intel Corporation, Tieto and others.
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
"""TestCase base class
"""

from collections import OrderedDict
import copy
import csv
import logging
import math
import os
import re
import time
import subprocess

from datetime import datetime as dt
from conf import settings as S
from conf import merge_spec
import core.component_factory as component_factory
from core.loader import Loader
from core.results.results_constants import ResultsConstants
from tools import tasks
from tools import hugepages
from tools import functions
from tools import namespace
from tools import veth
from tools.teststepstools import TestStepsTools
from tools.llc_management import rmd

# Validation methods required for integration TCs will have following prefix before the name
# of original method.
CHECK_PREFIX = 'validate_'

# Several parameters can be defined by both TC definition keywords and configuration parameters.
# Following mapping table is used to correctly evaluate priority of testcase configuration, where
# TC definition keywords (i.e. mapping table keys) have higher priority than appropriate TC
# parameters (i.e. mapping table values). TC parameters can be defined within "Parameters"
# section, via CLI parameters or within configuration files.
MAPPING_TC_CFG2CONF = {'vSwitch':'VSWITCH', 'VNF':'VNF', 'Trafficgen':'TRAFFICGEN', 'Tunnel Type':'TUNNEL_TYPE'}

# pylint: disable=too-many-instance-attributes
class TestCase(object):
    """TestCase base class

    In this basic form runs RFC2544 throughput test
    """
    # pylint: disable=too-many-statements
    def __init__(self, test_cfg):
        """Pull out fields from test config

        :param test_cfg: A dictionary of string-value pairs describing the test
            configuration. Both the key and values strings use well-known
            values.
        :param results_dir: Where the csv formatted results are written.
        """
        # make a local copy of test configuration to avoid modification of
        # original content used in vsperf main script
        cfg = copy.deepcopy(test_cfg)

        self._testcase_start_time = time.time()
        self._testcase_stop_time = self._testcase_start_time
        self._hugepages_mounted = False
        self._traffic_ctl = None
        self._vnf_ctl = None
        self._vswitch_ctl = None
        self._vswitch_pkt = None
        self._collector = None
        self._loadgen = None
        self._output_file = None
        self._tc_results = None
        self._settings_paths_modified = False
        self._testcast_run_time = None
        self._versions = []
        # initialization of step driven specific members
        self._step_check = False    # by default don't check result for step driven testcases
        self._step_vnf_list = {}
        self._step_result = []
        self._step_result_mapping = {}
        self._step_status = None
        self._step_send_traffic = False # indication if send_traffic was called within test steps
        self._vnf_list = []
        self._testcase_run_time = None

        S.setValue('VSWITCH', cfg.get('vSwitch', S.getValue('VSWITCH')))
        S.setValue('VNF', cfg.get('VNF', S.getValue('VNF')))
        S.setValue('TRAFFICGEN', cfg.get('Trafficgen', S.getValue('TRAFFICGEN')))
        S.setValue('TUNNEL_TYPE', cfg.get('Tunnel Type', S.getValue('TUNNEL_TYPE')))
        test_params = copy.deepcopy(S.getValue('TEST_PARAMS'))
        tc_test_params = cfg.get('Parameters', S.getValue('TEST_PARAMS'))
        test_params = merge_spec(test_params, tc_test_params)

        # ensure that parameters from TC definition have the highest priority, see MAPPING_TC_CFG2CONF
        for (cfg_param, param) in MAPPING_TC_CFG2CONF.items():
            if cfg_param in cfg and param in test_params:
                del test_params[param]

        S.setValue('TEST_PARAMS', test_params)
        S.check_test_params()

        # override all redefined GUEST_ values to have them expanded correctly
        tmp_test_params = copy.deepcopy(S.getValue('TEST_PARAMS'))
        for key in tmp_test_params:
            if key.startswith('GUEST_'):
                S.setValue(key, S.getValue(key))
                S.getValue('TEST_PARAMS').pop(key)

        # update global settings
        functions.settings_update_paths()

        # set test parameters; CLI options take precedence to testcase settings
        self._logger = logging.getLogger(__name__)
        self.name = cfg['Name']
        self.desc = cfg.get('Description', 'No description given.')
        self.test = cfg.get('TestSteps', None)

        # log testcase name and details
        tmp_desc = functions.format_description(self.desc, 50)
        self._logger.info('############################################################')
        self._logger.info('# Test:    %s', self.name)
        self._logger.info('# Details: %s', tmp_desc[0])
        for i in range(1, len(tmp_desc)):
            self._logger.info('#          %s', tmp_desc[i])
        self._logger.info('############################################################')

        bidirectional = S.getValue('TRAFFIC')['bidir']
        if not isinstance(S.getValue('TRAFFIC')['bidir'], str):
            raise TypeError(
                'Bi-dir value must be of type string')
        bidirectional = bidirectional.title()  # Keep things consistent

        self.deployment = cfg['Deployment']
        self._frame_mod = cfg.get('Frame Modification', None)

        self._tunnel_operation = cfg.get('Tunnel Operation', None)

        # check if test requires background load and which generator it uses
        self._load_cfg = cfg.get('Load', None)

        if self._frame_mod:
            self._frame_mod = self._frame_mod.lower()
        self._results_dir = S.getValue('RESULTS_PATH')

        # set traffic details, so they can be passed to vswitch and traffic ctls
        self._traffic = copy.deepcopy(S.getValue('TRAFFIC'))
        self._traffic.update({'bidir': bidirectional})

        # Packet Forwarding mode
        self._vswitch_none = str(S.getValue('VSWITCH')).strip().lower() == 'none'

        # trafficgen configuration required for tests of tunneling protocols
        if self._tunnel_operation:
            self._traffic.update({'tunnel_type': S.getValue('TUNNEL_TYPE')})
            self._traffic['l2'].update({'srcmac':
                                        S.getValue('TRAFFICGEN_PORT1_MAC'),
                                        'dstmac':
                                        S.getValue('TRAFFICGEN_PORT2_MAC')})

            self._traffic['l3'].update({'srcip':
                                        S.getValue('TRAFFICGEN_PORT1_IP'),
                                        'dstip':
                                        S.getValue('TRAFFICGEN_PORT2_IP')})

            if self._tunnel_operation == "decapsulation":
                self._traffic['l2'].update(S.getValue(S.getValue('TUNNEL_TYPE').upper() + '_FRAME_L2'))
                self._traffic['l3'].update(S.getValue(S.getValue('TUNNEL_TYPE').upper() + '_FRAME_L3'))
                self._traffic['l4'].update(S.getValue(S.getValue('TUNNEL_TYPE').upper() + '_FRAME_L4'))
                self._traffic['l2']['dstmac'] = S.getValue('NICS')[1]['mac']
        elif len(S.getValue('NICS')) >= 2 and \
             (S.getValue('NICS')[0]['type'] == 'vf' or
              S.getValue('NICS')[1]['type'] == 'vf'):
            mac1 = S.getValue('NICS')[0]['mac']
            mac2 = S.getValue('NICS')[1]['mac']
            if mac1 and mac2:
                self._traffic['l2'].update({'srcmac': mac2, 'dstmac': mac1})
            else:
                self._logger.debug("MAC addresses can not be read")

        self._traffic = functions.check_traffic(self._traffic)

        # count how many VNFs are involved in TestSteps
        if self.test:
            for step in self.test:
                if step[0].startswith('vnf'):
                    self._step_vnf_list[step[0]] = None

        # if llc allocation is required, initialize it.
        if S.getValue('LLC_ALLOCATION'):
            self._rmd = rmd.CacheAllocator()

    def run_initialize(self):
        """ Prepare test execution environment
        """
        # mount hugepages if needed
        self._mount_hugepages()

        self._logger.debug("Controllers:")
        loader = Loader()
        self._traffic_ctl = component_factory.create_traffic(
            self._traffic['traffic_type'],
            loader.get_trafficgen_class())

        self._vnf_ctl = component_factory.create_vnf(
            self.deployment,
            loader.get_vnf_class(),
            len(self._step_vnf_list))

        self._vnf_list = self._vnf_ctl.get_vnfs()

        # verify enough hugepages are free to run the testcase
        if not self._check_for_enough_hugepages():
            raise RuntimeError('Not enough hugepages free to run test.')

        # perform guest related handling
        tmp_vm_count = self._vnf_ctl.get_vnfs_number() + len(self._step_vnf_list)
        if tmp_vm_count:
            # copy sources of l2 forwarding tools into VM shared dir if needed
            self._copy_fwd_tools_for_all_guests(tmp_vm_count)

            # in case of multi VM in parallel, set the number of streams to the number of VMs
            if self.deployment.startswith('pvpv'):
                # for each VM NIC pair we need an unique stream
                streams = 0
                for vm_nic in S.getValue('GUEST_NICS_NR')[:tmp_vm_count]:
                    streams += int(vm_nic / 2) if vm_nic > 1 else 1
                self._logger.debug("VMs with parallel connection were detected. "
                                   "Thus Number of streams was set to %s", streams)
                # update streams if needed; In case of additional VNFs deployed by TestSteps
                # user can define a proper stream count manually
                if 'multistream' not in self._traffic or self._traffic['multistream'] < streams:
                    self._traffic.update({'multistream': streams})

            # OVS Vanilla requires guest VM MAC address and IPs to work
            if 'linux_bridge' in S.getValue('GUEST_LOOPBACK'):
                self._traffic['l2'].update({'srcmac': S.getValue('VANILLA_TGEN_PORT1_MAC'),
                                            'dstmac': S.getValue('VANILLA_TGEN_PORT2_MAC')})
                self._traffic['l3'].update({'srcip': S.getValue('VANILLA_TGEN_PORT1_IP'),
                                            'dstip': S.getValue('VANILLA_TGEN_PORT2_IP')})

        if self._vswitch_none:
            self._vswitch_ctl = component_factory.create_pktfwd(
                self.deployment,
                loader.get_pktfwd_class())
        else:
            self._vswitch_ctl = component_factory.create_vswitch(
                self.deployment,
                loader.get_vswitch_class(),
                self._traffic,
                self._tunnel_operation)
            self._vswitch_pkt = component_factory.create_pktfwd(
                self.deployment,
                loader.get_pktfwd_class())

        self._collector = component_factory.create_collector(
            loader.get_collector_class(),
            self._results_dir, self.name)
        self._loadgen = component_factory.create_loadgen(
            loader.get_loadgen_class(),
            self._load_cfg)

        self._output_file = os.path.join(self._results_dir, "result_{}_{}_{}.csv".format(
            str(S.getValue('_TEST_INDEX')), self.name, self.deployment))

        self._step_status = {'status' : True, 'details' : ''}

        # Perform LLC-allocations
        if S.getValue('LLC_ALLOCATION'):
            self._rmd.setup_llc_allocation()

        self._logger.debug("Setup:")

    def run_finalize(self):
        """ Tear down test execution environment and record test results
        """
        # Stop all VNFs started by TestSteps in case that something went wrong
        self.step_stop_vnfs()

        # Cleanup any LLC-allocations
        if S.getValue('LLC_ALLOCATION'):
            self._rmd.cleanup_llc_allocation()

        # Stop all processes executed by testcase
        tasks.terminate_all_tasks(self._logger)

        # umount hugepages if mounted
        self._umount_hugepages()

        # cleanup any namespaces created
        if os.path.isdir('/tmp/namespaces'):
            namespace_list = os.listdir('/tmp/namespaces')
            if namespace_list:
                self._logger.info('Cleaning up namespaces')
            for name in namespace_list:
                namespace.delete_namespace(name)
            os.rmdir('/tmp/namespaces')
        # cleanup any veth ports created
        if os.path.isdir('/tmp/veth'):
            veth_list = os.listdir('/tmp/veth')
            if veth_list:
                self._logger.info('Cleaning up veth ports')
            for eth in veth_list:
                port1, port2 = eth.split('-')
                veth.del_veth_port(port1, port2)
            os.rmdir('/tmp/veth')

    def run_report(self):
        """ Report test results
        """
        self._logger.debug("self._collector Results:")
        self._collector.print_results()

        results = self._traffic_ctl.get_results()
        if results:
            self._logger.debug("Traffic Results:")
            self._traffic_ctl.print_results()

        if self._tc_results is None:
            self._tc_results = self._append_results(results)
        else:
            # integration step driven tests have their status and possible
            # failure details stored inside self._tc_results
            results = self._append_results(results)
            if len(self._tc_results) < len(results):
                if len(self._tc_results) > 1:
                    raise RuntimeError('Testcase results do not match:'
                                       'results: %s\n'
                                       'trafficgen results: %s\n' %
                                       self._tc_results,
                                       results)
                else:
                    tmp_results = copy.deepcopy(self._tc_results[0])
                    self._tc_results = []
                    for res in results:
                        tmp_res = copy.deepcopy(tmp_results)
                        tmp_res.update(res)
                        self._tc_results.append(tmp_res)
            else:
                for i, result in enumerate(results):
                    self._tc_results[i].update(result)

        TestCase.write_result_to_file(self._tc_results, self._output_file)

    def run(self):
        """Run the test

        All setup and teardown through controllers is included.
        """
        # prepare test execution environment
        self.run_initialize()

        try:
            with self._vswitch_ctl:
                with self._vnf_ctl, self._collector, self._loadgen:
                    if not self._vswitch_none:
                        self._add_flows()

                    self._versions += self._vswitch_ctl.get_vswitch().get_version()

                    with self._traffic_ctl:
                        # execute test based on TestSteps definition if needed...
                        if self.step_run():
                            # ...and continue with traffic generation, but keep
                            # in mind, that clean deployment does not configure
                            # OVS nor executes the traffic
                            if self.deployment != 'clean' and not self._step_send_traffic:
                                self._traffic_ctl.send_traffic(self._traffic)

                        # dump vswitch flows before they are affected by VNF termination
                        if not self._vswitch_none:
                            self._vswitch_ctl.dump_vswitch_connections()

                    # garbage collection for case that TestSteps modify existing deployment
                    self.step_stop_vnfs()

        finally:
            # tear down test execution environment and log results
            self.run_finalize()

        self._testcase_stop_time = time.time()
        self._testcase_run_time = time.strftime("%H:%M:%S",
                                                time.gmtime(self._testcase_stop_time -
                                                            self._testcase_start_time))
        logging.info("Testcase execution time: %s", self._testcase_run_time)
        # report test results
        self.run_report()

    def _append_results(self, results):
        """
        Method appends mandatory Test Case results to list of dictionaries.

        :param results: list of dictionaries which contains results from
                traffic generator.

        :returns: modified list of dictionaries.
        """
        for item in results:
            item[ResultsConstants.ID] = self.name
            item[ResultsConstants.DEPLOYMENT] = self.deployment
            item[ResultsConstants.VSWITCH] = S.getValue('VSWITCH')
            item[ResultsConstants.TRAFFIC_TYPE] = self._traffic['l3']['proto']
            item[ResultsConstants.TEST_RUN_TIME] = self._testcase_run_time
            # convert timestamps to human readable format
            item[ResultsConstants.TEST_START_TIME] = dt.fromtimestamp(
                self._testcase_start_time).strftime('%Y-%m-%d %H:%M:%S')
            item[ResultsConstants.TEST_STOP_TIME] = dt.fromtimestamp(
                self._testcase_stop_time).strftime('%Y-%m-%d %H:%M:%S')
            if self._traffic['multistream']:
                item[ResultsConstants.SCAL_STREAM_COUNT] = self._traffic['multistream']
                item[ResultsConstants.SCAL_STREAM_TYPE] = self._traffic['stream_type']
                item[ResultsConstants.SCAL_PRE_INSTALLED_FLOWS] = self._traffic['pre_installed_flows']
            if self._vnf_ctl.get_vnfs_number():
                item[ResultsConstants.GUEST_LOOPBACK] = ' '.join(S.getValue('GUEST_LOOPBACK'))
            if self._tunnel_operation:
                item[ResultsConstants.TUNNEL_TYPE] = S.getValue('TUNNEL_TYPE')
        return results

    def _copy_fwd_tools_for_all_guests(self, vm_count):
        """Copy dpdk and l2fwd code to GUEST_SHARE_DIR[s] based on selected deployment.
        """
        # consider only VNFs involved in the test
        for guest_dir in set(S.getValue('GUEST_SHARE_DIR')[:vm_count]):
            self._copy_fwd_tools_for_guest(guest_dir)

    def _copy_fwd_tools_for_guest(self, guest_dir):
        """Copy dpdk and l2fwd code to GUEST_SHARE_DIR of VM

        :param index: Index of VM starting from 1 (i.e. 1st VM has index 1)
        """
        # remove shared dir if it exists to avoid issues with file consistency
        if os.path.exists(guest_dir):
            tasks.run_task(['rm', '-f', '-r', guest_dir], self._logger,
                           'Removing content of shared directory...', True)

        # directory to share files between host and guest
        os.makedirs(guest_dir)

        # copy sources into shared dir only if neccessary
        guest_loopback = set(S.getValue('GUEST_LOOPBACK'))
        if 'testpmd' in guest_loopback:
            try:
                # exclude whole .git/ subdirectory and all o-files;
                # It is assumed, that the same RTE_TARGET is used in both host
                # and VMs; This simplification significantly speeds up testpmd
                # build. If we will need a different RTE_TARGET in VM,
                # then we have to build whole DPDK from the scratch in VM.
                # In that case we can copy just DPDK sources (e.g. by excluding
                # all items obtained by git status -unormal --porcelain).
                # NOTE: Excluding RTE_TARGET directory won't help on systems,
                # where DPDK is built for multiple targets (e.g. for gcc & icc)
                exclude = []
                exclude.append(r'--exclude=.git/')
                exclude.append(r'--exclude=*.o')
                tasks.run_task(['rsync', '-a', '-r', '-l'] + exclude +
                               [os.path.join(S.getValue('TOOLS')['dpdk_src'], ''),
                                os.path.join(guest_dir, 'DPDK')],
                               self._logger,
                               'Copying DPDK to shared directory...',
                               True)
            except subprocess.CalledProcessError:
                self._logger.error('Unable to copy DPDK to shared directory')
                raise
        if 'l2fwd' in guest_loopback:
            try:
                tasks.run_task(['rsync', '-a', '-r', '-l',
                                os.path.join(S.getValue('ROOT_DIR'), 'src/l2fwd/'),
                                os.path.join(guest_dir, 'l2fwd')],
                               self._logger,
                               'Copying l2fwd to shared directory...',
                               True)
            except subprocess.CalledProcessError:
                self._logger.error('Unable to copy l2fwd to shared directory')
                raise

    def _mount_hugepages(self):
        """Mount hugepages if usage of DPDK or Qemu is detected
        """
        # pylint: disable=too-many-boolean-expressions
        # hugepages are needed by DPDK and Qemu
        if not self._hugepages_mounted and \
            (self.deployment.count('v') or \
             str(S.getValue('VSWITCH')).lower().count('dpdk') or \
             self._vswitch_none or \
             self.test and 'vnf' in [step[0][0:3] for step in self.test]):
            hugepages.mount_hugepages()
            self._hugepages_mounted = True

    def _umount_hugepages(self):
        """Umount hugepages if they were mounted before
        """
        if self._hugepages_mounted:
            hugepages.umount_hugepages()
            self._hugepages_mounted = False

    def _check_for_enough_hugepages(self):
        """Check to make sure enough hugepages are free to satisfy the
        test environment.
        """
        hugepages_needed = 0
        hugepage_size = hugepages.get_hugepage_size()
        # get hugepage amounts per guest involved in the test
        for guest in range(self._vnf_ctl.get_vnfs_number()):
            hugepages_needed += math.ceil((int(S.getValue(
                'GUEST_MEMORY')[guest]) * 1000) / hugepage_size)

        # get hugepage amounts for each socket on dpdk
        sock0_mem, sock1_mem = 0, 0

        if str(S.getValue('VSWITCH')).lower().count('dpdk'):
            sock_mem = S.getValue('DPDK_SOCKET_MEM')
            sock0_mem, sock1_mem = (int(sock_mem[0]) * 1024 / hugepage_size,
                                    int(sock_mem[1]) * 1024 / hugepage_size)

        # If hugepages needed, verify the amounts are free
        if any([hugepages_needed, sock0_mem, sock1_mem]):
            free_hugepages = hugepages.get_free_hugepages()
            if hugepages_needed:
                logging.info('Need %s hugepages free for guests',
                             hugepages_needed)
                result1 = free_hugepages >= hugepages_needed
                free_hugepages -= hugepages_needed
            else:
                result1 = True

            if sock0_mem:
                logging.info('Need %s hugepages free for dpdk socket 0',
                             sock0_mem)
                result2 = hugepages.get_free_hugepages('0') >= sock0_mem
                free_hugepages -= sock0_mem
            else:
                result2 = True

            if sock1_mem:
                logging.info('Need %s hugepages free for dpdk socket 1',
                             sock1_mem)
                result3 = hugepages.get_free_hugepages('1') >= sock1_mem
                free_hugepages -= sock1_mem
            else:
                result3 = True

            logging.info('Need a total of %s total hugepages',
                         hugepages_needed + sock1_mem + sock0_mem)

            # The only drawback here is sometimes dpdk doesn't release
            # its hugepages on a test failure. This could cause a test
            # to fail when dpdk would be OK to start because it will just
            # use the previously allocated hugepages.
            result4 = True if free_hugepages >= 0 else False

            return all([result1, result2, result3, result4])
        else:
            return True

    @staticmethod
    def write_result_to_file(results, output):
        """Write list of dictionaries to a CSV file.

        Each element on list will create separate row in output file.
        If output file already exists, data will be appended at the end,
        otherwise it will be created.

        :param results: list of dictionaries.
        :param output: path to output file.
        """
        with open(output, 'a') as csvfile:

            logging.info("Write results to file: %s", output)
            fieldnames = TestCase._get_unique_keys(results)

            writer = csv.DictWriter(csvfile, fieldnames)

            if not csvfile.tell():  # file is now empty
                writer.writeheader()

            for result in results:
                writer.writerow(result)

    @staticmethod
    def _get_unique_keys(list_of_dicts):
        """Gets unique key values as ordered list of strings in given dicts

        :param list_of_dicts: list of dictionaries.

        :returns: list of unique keys(strings).
        """
        result = OrderedDict()
        for item in list_of_dicts:
            for key in item.keys():
                result[key] = ''

        return list(result.keys())

    def _add_flows(self):
        """Add flows to the vswitch
        """
        vswitch = self._vswitch_ctl.get_vswitch()
        # NOTE BOM 15-08-07 the frame mod code assumes that the
        # physical ports are ports 1 & 2. The actual numbers
        # need to be retrived from the vSwitch and the metadata value
        # updated accordingly.
        bridge = S.getValue('VSWITCH_BRIDGE_NAME')
        if self._frame_mod == "vlan":
            # 0x8100 => VLAN ethertype
            self._logger.debug(" ****   VLAN   ***** ")
            flow = {'table':'2', 'priority':'1000', 'metadata':'2',
                    'actions': ['push_vlan:0x8100', 'goto_table:3']}
            vswitch.add_flow(bridge, flow)
            flow = {'table':'2', 'priority':'1000', 'metadata':'1',
                    'actions': ['push_vlan:0x8100', 'goto_table:3']}
            vswitch.add_flow(bridge, flow)
        elif self._frame_mod == "mpls":
            # 0x8847 => MPLS unicast ethertype
            self._logger.debug(" ****   MPLS  ***** ")
            flow = {'table':'2', 'priority':'1000', 'metadata':'2',
                    'actions': ['push_mpls:0x8847', 'goto_table:3']}
            vswitch.add_flow(bridge, flow)
            flow = {'table':'2', 'priority':'1000', 'metadata':'1',
                    'actions': ['push_mpls:0x8847', 'goto_table:3']}
            vswitch.add_flow(bridge, flow)
        elif self._frame_mod == "mac":
            flow = {'table':'2', 'priority':'1000', 'metadata':'2',
                    'actions': ['mod_dl_src:22:22:22:22:22:22',
                                'goto_table:3']}
            vswitch.add_flow(bridge, flow)
            flow = {'table':'2', 'priority':'1000', 'metadata':'1',
                    'actions': ['mod_dl_src:11:11:11:11:11:11',
                                'goto_table:3']}
            vswitch.add_flow(bridge, flow)
        elif self._frame_mod == "dscp":
            # DSCP 184d == 0x4E<<2 => 'Expedited Forwarding'
            flow = {'table':'2', 'priority':'1000', 'metadata':'2',
                    'dl_type':'0x0800',
                    'actions': ['mod_nw_tos:184', 'goto_table:3']}
            vswitch.add_flow(bridge, flow)
            flow = {'table':'2', 'priority':'1000', 'metadata':'1',
                    'dl_type':'0x0800',
                    'actions': ['mod_nw_tos:184', 'goto_table:3']}
            vswitch.add_flow(bridge, flow)
        elif self._frame_mod == "ttl":
            # 251 and 241 are the highest prime numbers < 255
            flow = {'table':'2', 'priority':'1000', 'metadata':'2',
                    'dl_type':'0x0800',
                    'actions': ['mod_nw_ttl:251', 'goto_table:3']}
            vswitch.add_flow(bridge, flow)
            flow = {'table':'2', 'priority':'1000', 'metadata':'1',
                    'dl_type':'0x0800',
                    'actions': ['mod_nw_ttl:241', 'goto_table:3']}
            vswitch.add_flow(bridge, flow)
        elif self._frame_mod == "ip_addr":
            flow = {'table':'2', 'priority':'1000', 'metadata':'2',
                    'dl_type':'0x0800',
                    'actions': ['mod_nw_src:10.10.10.10',
                                'mod_nw_dst:20.20.20.20',
                                'goto_table:3']}
            vswitch.add_flow(bridge, flow)
            flow = {'table':'2', 'priority':'1000', 'metadata':'1',
                    'dl_type':'0x0800',
                    'actions': ['mod_nw_src:20.20.20.20',
                                'mod_nw_dst:10.10.10.10',
                                'goto_table:3']}
            vswitch.add_flow(bridge, flow)
        elif self._frame_mod == "ip_port":
            # NOTE BOM 15-08-27 The traffic generated is assumed
            # to be UDP (nw_proto 17d) which is the default case but
            # we will need to pick up the actual traffic params in use.
            flow = {'table':'2', 'priority':'1000', 'metadata':'2',
                    'dl_type':'0x0800', 'nw_proto':'17',
                    'actions': ['mod_tp_src:44444',
                                'mod_tp_dst:44444', 'goto_table:3']}
            vswitch.add_flow(bridge, flow)
            flow = {'table':'2', 'priority':'1000', 'metadata':'1',
                    'dl_type':'0x0800', 'nw_proto':'17',
                    'actions': ['mod_tp_src:44444',
                                'mod_tp_dst:44444', 'goto_table:3']}
            vswitch.add_flow(bridge, flow)
        else:
            pass


    #
    # TestSteps realted methods
    #
    def step_report_status(self, label, status):
        """ Log status of test step
        """
        self._logger.info("%s ... %s", label, 'OK' if status else 'FAILED')

    def step_stop_vnfs(self):
        """ Stop all VNFs started by TestSteps
        """
        for vnf in self._step_vnf_list:
            if self._step_vnf_list[vnf]:
                self._step_vnf_list[vnf].stop()

    def step_eval_param(self, param, step_result):
        """ Helper function for #STEP macro evaluation
        """
        if isinstance(param, str):
            # evaluate every #STEP reference inside parameter itself
            macros = re.findall(r'(#STEP\[([\w\-:]+)\]((\[[\w\-\'\"]+\])*))', param)

            if macros:
                for macro in macros:
                    if macro[1] in self._step_result_mapping:
                        key = self._step_result_mapping[macro[1]]
                    else:
                        key = macro[1]
                    # pylint: disable=eval-used
                    tmp_val = str(eval('step_result[{}]{}'.format(key, macro[2])))
                    param = param.replace(macro[0], tmp_val)

            # evaluate references to vsperf configuration options
            macros = re.findall(r'\$(([\w\-]+)(\[[\w\[\]\-\'\"]+\])*)', param)
            if macros:
                for macro in macros:
                    # pylint: disable=eval-used
                    try:
                        tmp_val = str(eval("S.getValue('{}'){}".format(macro[1], macro[2])))
                        param = param.replace('${}'.format(macro[0]), tmp_val)
                    # ignore that required option can't be evaluated
                    except (IndexError, KeyError, AttributeError):
                        self._logger.debug("Skipping %s as it isn't a configuration "
                                           "parameter.", '${}'.format(macro[0]))
            return param
        elif isinstance(param, (list, tuple)):
            tmp_list = []
            for item in param:
                tmp_list.append(self.step_eval_param(item, step_result))
            return tmp_list
        elif isinstance(param, dict):
            tmp_dict = {}
            for (key, value) in param.items():
                tmp_dict[key] = self.step_eval_param(value, step_result)
            return tmp_dict
        else:
            return param

    def step_eval_params(self, params, step_result):
        """ Evaluates referrences to results from previous steps
        """
        eval_params = []
        # evaluate all parameters if needed
        for param in params:
            eval_params.append(self.step_eval_param(param, step_result))
        return eval_params

    # pylint: disable=too-many-locals, too-many-branches, too-many-statements
    def step_run(self):
        """ Execute actions specified by TestSteps list

        :return: False if any error was detected
                 True otherwise
        """
        # anything to do?
        if not self.test:
            return True

        # required for VNFs initialization
        loader = Loader()
        # initialize list with results
        self._step_result = [None] * len(self.test)

        # run test step by step...
        for i, step in enumerate(self.test):
            step_ok = not self._step_check
            step_check = self._step_check
            regex = None
            # configure step result mapping if step alias/label is detected
            if step[0].startswith('#'):
                key = step[0][1:]
                if key.isdigit():
                    raise RuntimeError('Step alias can\'t be an integer value {}'.format(key))
                if key in self._step_result_mapping:
                    raise RuntimeError('Step alias {} has been used already for step '
                                       '{}'.format(key, self._step_result_mapping[key]))
                self._step_result_mapping[step[0][1:]] = i
                step = step[1:]

            # store regex filter if it is specified
            if isinstance(step[-1], str) and step[-1].startswith('|'):
                # evalute macros and variables used in regex
                regex = self.step_eval_params([step[-1][1:]], self._step_result[:i])[0]
                step = step[:-1]

            # check if step verification should be suppressed
            if step[0].startswith('!'):
                step_check = False
                step_ok = True
                step[0] = step[0][1:]
            if step[0] == 'vswitch':
                test_object = self._vswitch_ctl.get_vswitch()
            elif step[0] == 'namespace':
                test_object = namespace
            elif step[0] == 'veth':
                test_object = veth
            elif step[0] == 'settings':
                test_object = S
            elif step[0] == 'tools':
                test_object = TestStepsTools()
                step[1] = step[1].title()
            elif step[0] == 'trafficgen':
                test_object = self._traffic_ctl
                # in case of send_traffic or send_traffic_async methods, ensure
                # that specified traffic values are merged with existing self._traffic
                if step[1].startswith('send_traffic'):
                    tmp_traffic = copy.deepcopy(self._traffic)
                    tmp_traffic.update(step[2])
                    step[2] = tmp_traffic
                    # store indication that traffic has been sent
                    # so it is not sent again after the execution of teststeps
                    self._step_send_traffic = True
            elif step[0].startswith('vnf'):
                # use vnf started within TestSteps
                if not self._step_vnf_list[step[0]]:
                    # initialize new VM
                    self._step_vnf_list[step[0]] = loader.get_vnf_class()()
                test_object = self._step_vnf_list[step[0]]
            elif step[0].startswith('testpmd'):
                test_object = self._vswitch_pkt
                step_check = False
                step_ok = True
            elif step[0].startswith('VNF'):
                if step[1] in ('start', 'stop'):
                    raise RuntimeError("Cannot execute start() or stop() method of "
                                       "VNF deployed automatically by scenario.")
                # use vnf started by scenario deployment (e.g. pvp)
                vnf_index = int(step[0][3:])
                try:
                    test_object = self._vnf_list[vnf_index]
                except IndexError:
                    raise RuntimeError("VNF with index {} is not running.".format(vnf_index))
            elif step[0] == 'wait':
                input(os.linesep + "Step {}: Press Enter to continue with "
                      "the next step...".format(i) + os.linesep + os.linesep)
                continue
            elif step[0] == 'sleep':
                self._logger.debug("Sleep %s seconds", step[1])
                time.sleep(int(step[1]))
                continue
            elif step[0] == 'log':
                test_object = self._logger
                # there isn't a need for validation of log entry
                step_check = False
                step_ok = True
            elif step[0] == 'pdb':
                import pdb
                pdb.set_trace()
                continue
            else:
                self._logger.error("Unsupported test object %s", step[0])
                self._step_status = {'status' : False, 'details' : ' '.join(step)}
                self.step_report_status("Step '{}'".format(' '.join(step)),
                                        self._step_status['status'])
                return False

            test_method = getattr(test_object, step[1])
            if step_check:
                test_method_check = getattr(test_object, CHECK_PREFIX + step[1])
            else:
                test_method_check = None

            step_params = []
            try:
                # eval parameters, but use only valid step_results
                # to support negative indexes
                step_params = self.step_eval_params(step[2:], self._step_result[:i])
                step_log = '{} {}'.format(' '.join(step[:2]), step_params)
                step_log += ' filter "{}"'.format(regex) if regex else ''
                self._logger.debug("Step %s '%s' start", i, step_log)
                self._step_result[i] = test_method(*step_params)
                if regex:
                    # apply regex to step output
                    self._step_result[i] = functions.filter_output(
                        self._step_result[i], regex)

                self._logger.debug("Step %s '%s' results '%s'", i,
                                   step_log, self._step_result[i])
                time.sleep(S.getValue('TEST_STEP_DELAY'))
                if step_check:
                    step_ok = test_method_check(self._step_result[i], *step_params)
            except (AssertionError, AttributeError, IndexError) as ex:
                step_ok = False
                self._logger.error("Step %s raised %s", i, type(ex).__name__)

            if step_check:
                self.step_report_status("Step {} - '{}'".format(i, step_log), step_ok)

            if not step_ok:
                self._step_status = {'status' : False, 'details' : step_log}
                # Stop all VNFs started by TestSteps
                self.step_stop_vnfs()
                return False

        # all steps processed without any issue
        return True

    #
    # get methods for TestCase members, which needs to be publicly available
    #
    def get_output_file(self):
        """Return content of self._output_file member
        """
        return self._output_file

    def get_desc(self):
        """Return content of self.desc member
        """
        return self.desc

    def get_versions(self):
        """Return content of self.versions member
        """
        return self._versions

    def get_traffic(self):
        """Return content of self._traffic member
        """
        return self._traffic

    def get_tc_results(self):
        """Return content of self._tc_results member
        """
        return self._tc_results

    def get_collector(self):
        """Return content of self._collector member
        """
        return self._collector
