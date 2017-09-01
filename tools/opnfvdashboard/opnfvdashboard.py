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
import copy
import logging
from datetime import datetime as dt
import requests

_DETAILS = {"64": '', "128": '', "512": '', "1024": '', "1518": ''}

def results2opnfv_dashboard(tc_names, results_path, int_data):
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
            tc_data = _prepare_results(reader, int_data)
            _push_results(tc_data)
            tc_names.remove(tc_data['id'])

    # report TCs without results as FAIL
    if tc_names:
        tc_fail = copy.deepcopy(int_data)
        tc_fail['start_time'] = dt.now().strftime('%Y-%m-%d %H:%M:%S')
        tc_fail['stop_time'] = tc_fail['start_time']
        tc_fail['criteria'] = 'FAIL'
        tc_fail['version'] = 'N/A'
        tc_fail['details'] = copy.deepcopy(_DETAILS)
        for tc_name in tc_names:
            tc_fail['dashboard_id'] = "{}_{}".format(tc_name, tc_fail['vswitch'])
            _push_results(tc_fail)

def _prepare_results(reader, int_data):
    """
    the method prepares dashboard details for passed testcases
    """
    version_vswitch = ""
    version_dpdk = ""
    allowed_pkt = ["64", "128", "512", "1024", "1518"]
    vswitch = None
    details = copy.deepcopy(_DETAILS)
    tc_data = copy.deepcopy(int_data)
    tc_data['criteria'] = 'PASS'

    for row_reader in reader:
        if allowed_pkt.count(row_reader['packet_size']) == 0:
            logging.error("The framesize is not supported in opnfv dashboard")
            continue

        # test execution time includes all frame sizes, so start & stop time
        # is the same (repeated) for every framesize in CSV file
        if not 'test_start' in tc_data:
            tc_data['start_time'] = row_reader['start_time']
            tc_data['stop_time'] = row_reader['stop_time']
            tc_data['id'] = row_reader['id']
            # CI job executes/reports TCs per vswitch type
            vswitch = row_reader['vswitch']

        tc_data['dashboard_id'] = "{}_{}".format(row_reader['id'], row_reader['vswitch'].lower())
        if "back2back" in row_reader['id']:
            # 0 B2B frames is quite common, so we can't mark such TC as FAIL
            details[row_reader['packet_size']] = row_reader['b2b_frames']
        else:
            details[row_reader['packet_size']] = row_reader['throughput_rx_fps']
            # 0 PPS is definitelly a failure
            if float(row_reader['throughput_rx_fps']) == 0:
                tc_data['criteria'] = 'FAIL'

    # Create version field
    with open(tc_data['pkg_list'], 'r') as pkg_file:
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

    tc_data['details'] = details
    tc_data['version'] = version_vswitch.replace('\n', '') + version_dpdk.replace('\n', '')

    return tc_data

def _push_results(int_data):
    """
    the method sends testcase details into dashboard database
    """
    url = int_data['db_url'] + "/results"

    # Build body
    body = {"project_name": "vsperf",
            "scenario": "vsperf",
            "start_date": int_data['start_time'],
            "stop_date": int_data['stop_time'],
            "case_name": int_data['dashboard_id'],
            "pod_name": int_data['pod'],
            "installer": int_data['installer'],
            "version": int_data['version'],
            "build_tag": int_data['build_tag'],
            "criteria": int_data['criteria'],
            "details": int_data['details']}

    my_data = requests.post(url, json=body)
    logging.info("Results for %s sent to opnfv, http response: %s", int_data['dashboard_id'], my_data)
    logging.debug("opnfv url: %s", int_data['db_url'])
    logging.debug("the body sent to opnfv")
    logging.debug(body)
