# Copyright 2016 Red Hat Inc & Xena Networks.
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
#
# Contributors:
#   Rick Alongi, Red Hat Inc.
#   Amit Supugade, Red Hat Inc.
#   Dan Amzulescu, Xena Networks
#   Christian Trautman, Red Hat Inc.

"""
Xena Traffic Generator Model
"""

# python imports
import inspect
import logging
import subprocess
import sys
from time import sleep
import xml.etree.ElementTree as ET
from collections import OrderedDict

# VSPerf imports
from conf import settings
from core.results.results_constants import ResultsConstants
from tools.pkt_gen.trafficgen.trafficgenhelper import (
    TRAFFIC_DEFAULTS,
    merge_spec)
from tools.pkt_gen.trafficgen.trafficgen import ITrafficGenerator

# Xena module imports
from tools.pkt_gen.xena.xena_json import XenaJSON


class Xena(ITrafficGenerator):
    """
    Xena Traffic generator wrapper class
    """
    _traffic_defaults = TRAFFIC_DEFAULTS.copy()
    _logger = logging.getLogger(__name__)

    def __init__(self):
        self.mono_pipe = None
        self._params = {}
        self._duration = None

    @property
    def traffic_defaults(self):
        """Default traffic values.

        These can be expected to be constant across traffic generators,
        so no setter is provided. Changes to the structure or contents
        will likely break traffic generator implementations or tests
        respectively.
        """
        return self._traffic_defaults

    @staticmethod
    def _create_throughput_result(root):
        """
        Create the results based off the output xml file from the Xena2544.exe
        execution
        :param root: root dictionary from xml import
        :return: Results Ordered dictionary based off ResultsConstants
        """
        throughput_test = False
        back2back_test = False
        # get the calling method so we know how to return the stats
        caller = inspect.stack()[1][3]
        if 'throughput' in caller:
            throughput_test = True
        elif 'back2back' in caller:
            back2back_test = True
        else:
            raise NotImplementedError(
                "Unknown implementation for result return")

        if throughput_test:
            results = OrderedDict()
            results[ResultsConstants.THROUGHPUT_RX_FPS] = int(
                root[0][1][0][1].get('PortRxPps'))
            results[ResultsConstants.THROUGHPUT_RX_MBPS] = int(
                root[0][1][0][1].get('PortRxBpsL1')) / 1000000
            results[ResultsConstants.THROUGHPUT_RX_PERCENT] = (
                100 - int(root[0][1][0].get('TotalLossRatioPcnt'))) * float(
                    root[0][1][0].get('TotalTxRatePcnt'))/100
            results[ResultsConstants.TX_RATE_FPS] = root[0][1][0].get(
                'TotalTxRateFps')
            results[ResultsConstants.TX_RATE_MBPS] = float(
                root[0][1][0].get('TotalTxRateBpsL1')) / 1000000
            results[ResultsConstants.TX_RATE_PERCENT] = root[0][1][0].get(
                'TotalTxRatePcnt')
            try:
                results[ResultsConstants.MIN_LATENCY_NS] = float(
                    root[0][1][0][0].get('MinLatency')) * 1000
            except ValueError:
                # Stats for latency returned as N/A so just post them
                results[ResultsConstants.MIN_LATENCY_NS] = root[0][1][0][0].get(
                    'MinLatency')
            try:
                results[ResultsConstants.MAX_LATENCY_NS] = float(
                    root[0][1][0][0].get('MaxLatency')) * 1000
            except ValueError:
                # Stats for latency returned as N/A so just post them
                results[ResultsConstants.MAX_LATENCY_NS] = root[0][1][0][0].get(
                    'MaxLatency')
            try:
                results[ResultsConstants.AVG_LATENCY_NS] = float(
                    root[0][1][0][0].get('AvgLatency')) * 1000
            except ValueError:
                # Stats for latency returned as N/A so just post them
                results[ResultsConstants.AVG_LATENCY_NS] = root[0][1][0][0].get(
                    'AvgLatency')
        elif back2back_test:
            raise NotImplementedError('Back to back results not implemented')

        return results

    def _setup_json_config(self, trials, loss_rate, testtype=None):
        """
        Create a 2bUsed json file that will be used for xena2544.exe execution.
        :param trials: Number of trials
        :param loss_rate: The acceptable loss rate as float
        :param testtype: Either '2544_b2b' or '2544_throughput' as string
        :return: None
        """
        try:
            j_file = XenaJSON('./tools/pkt_gen/xena/profiles/baseconfig.x2544')
            j_file.set_chassis_info(
                settings.getValue('TRAFFICGEN_XENA_IP'),
                settings.getValue('TRAFFICGEN_XENA_PASSWORD')
            )
            j_file.set_port(0, settings.getValue('TRAFFICGEN_XENA_MODULE1'),
                            settings.getValue('TRAFFICGEN_XENA_PORT1')
                            )
            j_file.set_port(1, settings.getValue('TRAFFICGEN_XENA_MODULE2'),
                            settings.getValue('TRAFFICGEN_XENA_PORT2')
                            )
            j_file.set_test_options(
                packet_sizes=self._params['traffic']['l2']['framesize'],
                iterations=trials, loss_rate=loss_rate,
                duration=self._duration, micro_tpld=True if self._params[
                    'traffic']['l2']['framesize'] == 64 else False)
            if testtype == '2544_throughput':
                j_file.enable_throughput_test()
            elif testtype == '2544_b2b':
                j_file.enable_back2back_test()

            j_file.set_header_layer2(
                dst_mac=self._params['traffic']['l2']['dstmac'],
                src_mac=self._params['traffic']['l2']['srcmac'])
            j_file.set_header_layer3(
                src_ip=self._params['traffic']['l3']['srcip'],
                dst_ip=self._params['traffic']['l3']['dstip'],
                protocol=self._params['traffic']['l3']['proto'])
            j_file.set_header_layer4_udp(
                source_port=self._params['traffic']['l4']['srcport'],
                destination_port=self._params['traffic']['l4']['dstport'])
            if self._params['traffic']['vlan']['enabled']:
                j_file.set_header_vlan(
                    vlan_id=self._params['traffic']['vlan']['id'],
                    id=self._params['traffic']['vlan']['cfi'],
                    prio=self._params['traffic']['vlan']['priority'])
            j_file.add_header_segments(
                flows=self._params['traffic']['multistream'],
                multistream_layer=self._params['traffic']['stream_type'])
            # set duplex mode
            if self._params['traffic']['bidir']:
                j_file.set_topology_mesh()
            else:
                j_file.set_topology_blocks()

            j_file.write_config('./tools/pkt_gen/xena/profiles/2bUsed.x2544')
        except Exception as exc:
            self._logger.exception("Error during Xena JSON setup: %s", exc)
            raise

    def connect(self):
        """Connect to the traffic generator.

        This is an optional function, designed for traffic generators
        which must be "connected to" (i.e. via SSH or an API) before
        they can be used. If not required, simply do nothing here.

        Where implemented, this function should raise an exception on
        failure.

        :returns: None
        """
        pass

    def disconnect(self):
        """Disconnect from the traffic generator.

        As with :func:`connect`, this function is optional.

        Where implemented, this function should raise an exception on
        failure.

        :returns: None
        """
        pass

    def send_burst_traffic(self, traffic=None, numpkts=100, duration=20):
        """Send a burst of traffic.

        Send a ``numpkts`` packets of traffic, using ``traffic``
        configuration, with a timeout of ``time``.

        Attributes:
        :param traffic: Detailed "traffic" spec, i.e. IP address, VLAN tags
        :param numpkts: Number of packets to send
        :param duration: Time to wait to receive packets

        :returns: dictionary of strings with following data:
            - List of Tx Frames,
            - List of Rx Frames,
            - List of Tx Bytes,
            - List of List of Rx Bytes,
            - Payload Errors and Sequence Errors.
        """
        raise NotImplementedError('Xena burst traffic not implemented')

    def send_cont_traffic(self, traffic=None, duration=20):
        """Send a continuous flow of traffic.r

        Send packets at ``framerate``, using ``traffic`` configuration,
        until timeout ``time`` occurs.

        :param traffic: Detailed "traffic" spec, i.e. IP address, VLAN tags
        :param duration: Time to wait to receive packets (secs)
        :returns: dictionary of strings with following data:
            - Tx Throughput (fps),
            - Rx Throughput (fps),
            - Tx Throughput (mbps),
            - Rx Throughput (mbps),
            - Tx Throughput (% linerate),
            - Rx Throughput (% linerate),
            - Min Latency (ns),
            - Max Latency (ns),
            - Avg Latency (ns)
        """
        raise NotImplementedError('Xena continuous traffic not implemented')

    def start_cont_traffic(self, traffic=None, duration=20):
        """Non-blocking version of 'send_cont_traffic'.

        Start transmission and immediately return. Do not wait for
        results.
        :param traffic: Detailed "traffic" spec, i.e. IP address, VLAN tags
        :param duration: Time to wait to receive packets (secs)
        """
        raise NotImplementedError('Xena continuous traffic not implemented')

    def stop_cont_traffic(self):
        """Stop continuous transmission and return results.
        """
        raise NotImplementedError('Xena continuous traffic not implemented')

    def send_rfc2544_throughput(self, traffic=None, trials=3, duration=20,
                                lossrate=0.0):
        """Send traffic per RFC2544 throughput test specifications.

        See ITrafficGenerator for description
        """
        self._duration = duration

        self._params.clear()
        self._params['traffic'] = self.traffic_defaults.copy()
        if traffic:
            self._params['traffic'] = merge_spec(self._params['traffic'],
                                                 traffic)

        self._setup_json_config(trials, lossrate, '2544_throughput')

        args = ["mono", "./tools/pkt_gen/xena/Xena2544.exe", "-c",
                "./tools/pkt_gen/xena/profiles/2bUsed.x2544", "-e", "-r",
                "./tools/pkt_gen/xena", "-u",
                settings.getValue('TRAFFICGEN_XENA_USER')]
        self.mono_pipe = subprocess.Popen(args, stdout=sys.stdout)
        self.mono_pipe.communicate()
        root = ET.parse(r'./tools/pkt_gen/xena/xena2544-report.xml').getroot()
        return Xena._create_throughput_result(root)

    def start_rfc2544_throughput(self, traffic=None, trials=3, duration=20,
                                 lossrate=0.0):
        """Non-blocking version of 'send_rfc2544_throughput'.

        See ITrafficGenerator for description
        """
        self._duration = duration
        self._params.clear()
        self._params['traffic'] = self.traffic_defaults.copy()
        if traffic:
            self._params['traffic'] = merge_spec(self._params['traffic'],
                                                 traffic)

        self._setup_json_config(trials, lossrate, '2544_throughput')

        args = ["mono", "./tools/pkt_gen/xena/Xena2544.exe", "-c",
                "./tools/pkt_gen/xena/profiles/2bUsed.x2544", "-e", "-r",
                "./tools/pkt_gen/xena", "-u",
                settings.getValue('TRAFFICGEN_XENA_USER')]
        self.mono_pipe = subprocess.Popen(args, stdout=sys.stdout)

    def wait_rfc2544_throughput(self):
        """Wait for and return results of RFC2544 test.

        See ITrafficGenerator for description
        """
        self.mono_pipe.communicate()
        sleep(2)
        root = ET.parse(r'./tools/pkt_gen/xena/xena2544-report.xml').getroot()
        return Xena._create_throughput_result(root)

    def send_rfc2544_back2back(self, traffic=None, trials=1, duration=20,
                               lossrate=0.0):
        """Send traffic per RFC2544 back2back test specifications.

        Send packets at a fixed rate, using ``traffic``
        configuration, until minimum time at which no packet loss is
        detected is found.

        :param traffic: Detailed "traffic" spec, i.e. IP address, VLAN
            tags
        :param trials: Number of trials to execute
        :param duration: Per iteration duration
        :param lossrate: Acceptable loss percentage

        :returns: Named tuple of Rx Throughput (fps), Rx Throughput (mbps),
            Tx Rate (% linerate), Rx Rate (% linerate), Tx Count (frames),
            Back to Back Count (frames), Frame Loss (frames), Frame Loss (%)
        :rtype: :class:`Back2BackResult`
        """
        raise NotImplementedError('Xena back2back not implemented')

    def start_rfc2544_back2back(self, traffic=None, trials=1, duration=20,
                                lossrate=0.0):
        """Non-blocking version of 'send_rfc2544_back2back'.

        Start transmission and immediately return. Do not wait for
        results.
        """
        raise NotImplementedError('Xena back2back not implemented')

    def wait_rfc2544_back2back(self):
        """Wait and set results of RFC2544 test.
        """
        raise NotImplementedError('Xena back2back not implemented')


if __name__ == "__main__":
    pass

