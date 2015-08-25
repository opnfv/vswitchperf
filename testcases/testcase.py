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
"""TestCase base class
"""

import csv
import os
import logging
from collections import OrderedDict

from core.results.results_constants import ResultsConstants
import core.component_factory as component_factory
from core.loader import Loader

class TestCase(object):
    """TestCase base class

    In this basic form runs RFC2544 throughput test
    """
    def __init__(self, cfg, results_dir):
        """Pull out fields from test config

        :param cfg: A dictionary of string-value pairs describing the test
            configuration. Both the key and values strings use well-known
            values.
        :param results_dir: Where the csv formatted results are written.
        """
        self._logger = logging.getLogger(__name__)
        self.name = cfg['Name']
        self.desc = cfg.get('Description', 'No description given.')
        self._traffic_type = cfg['Traffic Type']
        self.deployment = cfg['Deployment']
        self._collector = cfg['Collector']
        self._bidir = cfg['biDirectional']
        self._frame_mod = cfg.get('Frame Modification', None)

        # check if test requires background load and which generator it uses
        self._load_cfg = cfg.get('Load', None)
        if self._load_cfg and 'tool' in self._load_cfg:
            self._loadgen = self._load_cfg['tool']
        else:
            # background load is not requested, so use dummy implementation
            self._loadgen = "Dummy"

        if self._frame_mod:
            self._frame_mod = self._frame_mod.lower()
        self._results_dir = results_dir
        self._multistream = cfg.get('MultiStream', 0)

    def run(self):
        """Run the test

        All setup and teardown through controllers is included.
        """
        self._logger.debug(self.name)

        self._logger.debug("Controllers:")
        loader = Loader()
        traffic_ctl = component_factory.create_traffic(
            self._traffic_type,
            loader.get_trafficgen_class())
        vnf_ctl = component_factory.create_vnf(
            self.deployment,
            loader.get_vnf_class())
        vswitch_ctl = component_factory.create_vswitch(
            self.deployment,
            loader.get_vswitch_class(),
            self._bidir)
        collector_ctl = component_factory.create_collector(
            self._collector,
            loader.get_collector_class())
        loadgen = component_factory.create_loadgen(
            self._loadgen,
            self._load_cfg)

        self._logger.debug("Setup:")
        collector_ctl.log_cpu_stats()
        with vswitch_ctl, loadgen:
            with vnf_ctl:
                traffic = {'traffic_type': self._traffic_type,
                           'bidir': self._bidir,
                           'multistream': self._multistream}

                vswitch = vswitch_ctl.get_vswitch()
                # TODO BOM 15-08-07 the frame mod code assumes that the
                # physical ports are ports 1 & 2. The actual numbers
                # need to be retrived from the vSwitch and the metadata value
                # updated accordingly.
                if self._frame_mod == "vlan":
                    # 0x8100 => VLAN ethertype
                    self._logger.debug(" ****   VLAN   ***** ")
                    flow = {'table':'2', 'priority':'1000', 'metadata':'2',
                            'actions': ['push_vlan:0x8100', 'goto_table:3']}
                    vswitch.add_flow('br0', flow)
                    flow = {'table':'2', 'priority':'1000', 'metadata':'1',
                            'actions': ['push_vlan:0x8100', 'goto_table:3']}
                    vswitch.add_flow('br0', flow)
                elif self._frame_mod == "mpls":
                    # 0x8847 => MPLS unicast ethertype
                    self._logger.debug(" ****   MPLS  ***** ")
                    flow = {'table':'2', 'priority':'1000', 'metadata':'2',
                            'actions': ['push_mpls:0x8847', 'goto_table:3']}
                    vswitch.add_flow('br0', flow)
                    flow = {'table':'2', 'priority':'1000', 'metadata':'1',
                            'actions': ['push_mpls:0x8847', 'goto_table:3']}
                    vswitch.add_flow('br0', flow)
                elif self._frame_mod == "mac":
                    flow = {'table':'2', 'priority':'1000', 'metadata':'2',
                            'actions': ['mod_dl_src:22:22:22:22:22:22', 'goto_table:3']}
                    vswitch.add_flow('br0', flow)
                    flow = {'table':'2', 'priority':'1000', 'metadata':'1',
                            'actions': ['mod_dl_src:11:11:11:11:11:11', 'goto_table:3']}
                    vswitch.add_flow('br0', flow)
                elif self._frame_mod == "dscp":
                    # DSCP 184d == 0x4E<<2 => 'Expedited Forwarding'
                    flow = {'table':'2', 'priority':'1000', 'metadata':'2',
                            'dl_type':'0x0800',
                            'actions': ['mod_nw_tos:184', 'goto_table:3']}
                    vswitch.add_flow('br0', flow)
                    flow = {'table':'2', 'priority':'1000', 'metadata':'1',
                            'dl_type':'0x0800',
                            'actions': ['mod_nw_tos:184', 'goto_table:3']}
                    vswitch.add_flow('br0', flow)
                elif self._frame_mod == "ttl":
                    # 251 and 241 are the highest prime numbers < 255
                    flow = {'table':'2', 'priority':'1000', 'metadata':'2',
                            'dl_type':'0x0800',
                            'actions': ['mod_nw_ttl:251', 'goto_table:3']}
                    vswitch.add_flow('br0', flow)
                    flow = {'table':'2', 'priority':'1000', 'metadata':'1',
                            'dl_type':'0x0800',
                            'actions': ['mod_nw_ttl:241', 'goto_table:3']}
                    vswitch.add_flow('br0', flow)
                elif self._frame_mod == "ip_addr":
                    flow = {'table':'2', 'priority':'1000', 'metadata':'2',
                            'dl_type':'0x0800',
                            'actions': ['mod_nw_src:10.10.10.10',
                            'mod_nw_dst:20.20.20.20', 'goto_table:3']}
                    vswitch.add_flow('br0', flow)
                    flow = {'table':'2', 'priority':'1000', 'metadata':'1',
                            'dl_type':'0x0800',
                            'actions': ['mod_nw_src:20.20.20.20',
                            'mod_nw_dst:10.10.10.10', 'goto_table:3']}
                    vswitch.add_flow('br0', flow)
                elif self._frame_mod == "ip_port":
                    # TODO BOM 15-08-27 The traffic generated is assumed
                    # to be UDP (nw_proto 17d) which is the default case but
                    # we will need to pick up the actual traffic params in use.
                    flow = {'table':'2', 'priority':'1000', 'metadata':'2',
                            'dl_type':'0x0800', 'nw_proto':'17',
                            'actions': ['mod_tp_src:44444',
                            'mod_tp_dst:44444', 'goto_table:3']}
                    vswitch.add_flow('br0', flow)
                    flow = {'table':'2', 'priority':'1000', 'metadata':'1',
                            'dl_type':'0x0800', 'nw_proto':'17',
                            'actions': ['mod_tp_src:44444',
                            'mod_tp_dst:44444', 'goto_table:3']}
                    vswitch.add_flow('br0', flow)
                else:
                    pass

                with traffic_ctl:
                    traffic_ctl.send_traffic(traffic)

        self._logger.debug("Traffic Results:")
        traffic_ctl.print_results()

        self._logger.debug("Collector Results:")
        self._logger.debug(collector_ctl.get_results())

        output_file = "result_" + self.name + "_" + self.deployment +".csv"

        TestCase._write_result_to_file(
            self._append_results(traffic_ctl.get_results()),
            os.path.join(self._results_dir, output_file))

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

        return results


    @staticmethod
    def _write_result_to_file(results, output):
        """Write list of dictionaries to a CSV file.

        Each element on list will create separate row in output file.
        If output file already exists, data will be appended at the end,
        otherwise it will be created.

        :param results: list of dictionaries.
        :param output: path to output file.
        """
        with open(output, 'a') as csvfile:

            logging.info("Write results to file: " + output)
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
