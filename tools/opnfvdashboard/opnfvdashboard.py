"""
vsperf2dashboard
"""
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

import os
import csv
import logging
import requests

def results2opnfv_dashboard(results_path, int_data):
    """
    the method open the csv file with results and calls json encoder
    """
    testcases = os.listdir(results_path)
    for test in testcases:
        if not ".csv" in test:
            continue
        resfile = results_path + '/' + test
        with open(resfile, 'r') as in_file:
            reader = csv.DictReader(in_file)
            _push_results(reader, int_data)

def _push_results(reader, int_data):
    """
    the method encodes results and sends them into opnfv dashboard
    """
    db_url = int_data['db_url']
    url = db_url + "/results"
    casename = ""
    version_vswitch = ""
    version_dpdk = ""
    version = ""
    allowed_pkt = ["64", "128", "512", "1024", "1518"]
    details = {"64": '', "128": '', "512": '', "1024": '', "1518": ''}
    test_start = None
    test_stop = None
    vswitch = None

    for row_reader in reader:
        if allowed_pkt.count(row_reader['packet_size']) == 0:
            logging.error("The framesize is not supported in opnfv dashboard")
            continue

        # test execution time includes all frame sizes, so start & stop time
        # is the same (repeated) for every framesize in CSV file
        if test_start is None:
            test_start = row_reader['start_time']
            test_stop = row_reader['stop_time']
            # CI job executes/reports TCs per vswitch type
            vswitch = row_reader['vswitch']

        casename = "{}_{}".format(row_reader['id'], row_reader['vswitch'].lower())
        if "back2back" in row_reader['id']:
            details[row_reader['packet_size']] = row_reader['b2b_frames']
        else:
            details[row_reader['packet_size']] = row_reader['throughput_rx_fps']

    # Create version field
    with open(int_data['pkg_list'], 'r') as pkg_file:
        for line in pkg_file:
            if "OVS_TAG" in line and vswitch.startswith('Ovs'):
                version_vswitch = line.replace(' ', '')
                version_vswitch = "OVS " + version_vswitch.replace('OVS_TAG?=', '')
            if "VPP_TAG" in line and vswitch.startswith('Vpp'):
                version_vswitch = line.replace(' ', '')
                version_vswitch = "VPP " + version_vswitch.replace('VPP_TAG?=', '')
            if "DPDK_TAG" in line:
                # DPDK_TAG is not used by VPP, it downloads its onw DPDK version
                if vswitch == "OvsDpdkVhost":
                    version_dpdk = line.replace(' ', '')
                    version_dpdk = " DPDK {}".format(
                        version_dpdk.replace('DPDK_TAG?=', ''))
    version = version_vswitch.replace('\n', '') + version_dpdk.replace('\n', '')

    # Build body
    body = {"project_name": "vsperf",
            "scenario": "vsperf",
            "start_date": test_start,
            "stop_date": test_stop,
            "case_name": casename,
            "pod_name": int_data['pod'],
            "installer": int_data['installer'],
            "version": version,
            "build_tag": int_data['build_tag'],
            "criteria": int_data['criteria'],
            "details": details}

    my_data = requests.post(url, json=body)
    logging.info("Results for %s sent to opnfv, http response: %s", casename, my_data)
    logging.debug("opnfv url: %s", db_url)
    logging.debug("the body sent to opnfv")
    logging.debug(body)
