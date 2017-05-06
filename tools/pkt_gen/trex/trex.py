# Copyright 2017 Martin Goldammer, OPNFV, Red Hat Inc.
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
"""
Trex Traffic Generator Model
"""

from collections import OrderedDict
import logging
import re
import subprocess
from conf import settings
from conf import merge_spec
from core.results.results_constants import ResultsConstants
from tools.pkt_gen.trafficgen.trafficgen import ITrafficGenerator

class Trex(ITrafficGenerator):
    """Trex Traffic generator wrapper."""
    _logger = logging.getLogger(__name__)

    def __init__(self):
        """Trex class constructor."""
        super().__init__()
        self._logger.info("In trex __init__ method")
        self._params = {}
        self._trex_host_ip_addr = (
            settings.getValue('TRAFFICGEN_TREX_HOST_IP_ADDR'))
        self._trex_base_dir = (
            settings.getValue('TRAFFICGEN_TREX_BASE_DIR'))
        self._trex_user = settings.getValue('TRAFFICGEN_TREX_USER')


    def connect(self):
        """Connect to Trex traffic generator

        Verify that Trex is on the system indicated by
        the configuration file
        """
        self._logger.info("TREX:  In Trex connect method...")

        if self._trex_host_ip_addr:
            cmd_ping = "ping -c1 " + self._trex_host_ip_addr
        else:
            raise RuntimeError('TREX: Trex host not defined')

        ping = subprocess.Popen(cmd_ping, shell=True, stderr=subprocess.PIPE)
        output, error = ping.communicate()

        if ping.returncode:
            self._logger.error(error)
            self._logger.error(output)
            raise RuntimeError('TREX: Cannot ping Trex host at ' + \
                               self._trex_host_ip_addr)

        connect_trex = "ssh " + self._trex_user + \
                          "@" + self._trex_host_ip_addr

        cmd_find_trex = connect_trex + " ls " + \
                           self._trex_base_dir + "t-rex-64"

        find_trex = subprocess.Popen(cmd_find_trex,
                                     shell=True,
                                     stderr=subprocess.PIPE)

        output, error = find_trex.communicate()

        if find_trex.returncode:
            self._logger.error(error)
            self._logger.error(output)
            raise RuntimeError(
                'TREX: Cannot locate Trex program at %s within %s' \
                % (self._trex_host_ip_addr, self._trex_base_dir))

        self._logger.info("TREX: Trex host successfully found...")

    def disconnect(self):
        """Disconnect from the traffic generator.

        As with :func:`connect`, this function is optional.

        Where implemented, this function should raise an exception on
        failure.

        :returns: None
        """
        self._logger.info("TREX: In trex disconnect method")

    def send_cont_traffic(self, traffic=None, duration=5):
        """See ITrafficGenerator for description
        """
        self._logger.info("In Trex send_cont_traffic method")
        self._params.clear()
        self._params['traffic'] = self.traffic_defaults.copy()
        results = {}
        if traffic:
            self._params['traffic'] = merge_spec(self._params['traffic'],
                                                 traffic)

        collected_results = Trex.run_trex_and_collect_results(self, duration=duration, test_run=1)

        results[ResultsConstants.MAX_LATENCY_NS] = (
            '{:.3f}'.format(
                float(collected_results[ResultsConstants.MAX_LATENCY_NS])))

        results[ResultsConstants.AVG_LATENCY_NS] = (
            '{:.3f}'.format(
                float(collected_results[ResultsConstants.AVG_LATENCY_NS])))

        results[ResultsConstants.FRAME_LOSS_PERCENT] = (
            '{:.3f}'.format(
                float(collected_results[ResultsConstants.FRAME_LOSS_PERCENT])))

        results[ResultsConstants.THROUGHPUT_RX_FPS] = (
            '{:.3f}'.format(
                float(collected_results[ResultsConstants.THROUGHPUT_RX_FPS])))

        results[ResultsConstants.THROUGHPUT_RX_MBPS] = (
            '{:.3f}'.format(
                float(collected_results[ResultsConstants.THROUGHPUT_RX_MBPS])))

        results[ResultsConstants.TX_RATE_MBPS] = (
            '{:.3f}'.format(
                float(collected_results[ResultsConstants.TX_RATE_MBPS])))

        results[ResultsConstants.TX_RATE_FPS] = (
            '{:.3f}'.format(
                float(collected_results[ResultsConstants.TX_RATE_FPS])))

        results[ResultsConstants.MIN_LATENCY_NS] = (
            collected_results[ResultsConstants.MIN_LATENCY_NS])

        results[ResultsConstants.TX_RATE_PERCENT] = (
            collected_results[ResultsConstants.TX_RATE_PERCENT])

        return results

    def stop_cont_traffic(self):
        """See ITrafficGenerator for description
        """
        self._logger.info("In Trex stop_cont_traffic method")

    def run_trex_and_collect_results(self, duration, test_run=1):
        """Execute Trex and transform results into VSPERF format
        :param test_run: The number of tests to run
        :param duration: The number of seconds which test will go
        """

        connect_trex = "ssh " + self._trex_user + "@" + \
            self._trex_host_ip_addr

        cmd_trex = " 'cd " + self._trex_base_dir + \
            "; ./t-rex-64 -f cap2/imix.yaml -c 1 -m 1 -d " + str(duration) + " -l 1000 | tee trex.log'"
        cmd_start_trex = connect_trex + cmd_trex

        start_trex = subprocess.Popen(cmd_start_trex,
                                      shell=True, stderr=subprocess.PIPE)

        output, error = start_trex.communicate()
        if start_trex.returncode:
            logging.debug(error)
            logging.debug(output)
            raise RuntimeError(
                'TREX: Error starting Trex program at %s within %s' \
                % (self._trex_host_ip_addr, self._trex_base_dir))

        cmd_trex = "mkdir -p /tmp/trex/" + str(test_run)

        trex_create_log_dir = subprocess.Popen(cmd_trex,
                                               shell=True,
                                               stderr=subprocess.PIPE)

        output, error = trex_create_log_dir.communicate()

        if trex_create_log_dir.returncode:
            logging.debug(error)
            logging.debug(output)
            raise RuntimeError(
                'TREX: Error obtaining Trex log from %s within %s' \
                % (self._trex_host_ip_addr, self._trex_base_dir))

        cmd_trex = " scp " + self._trex_user + "@" + \
            self._trex_host_ip_addr + ":" + \
            self._trex_base_dir + "trex.log /tmp/trex/" + \
            str(test_run) + "/trex-run.log"

        copy_trex_log = subprocess.Popen(cmd_trex,
                                         shell=True,
                                         stderr=subprocess.PIPE)

        output, error = copy_trex_log.communicate()

        if copy_trex_log.returncode:
            logging.debug(error)
            logging.debug(output)
            raise RuntimeError(
                'TREX: Error obtaining Trex log from %s within %s' \
                % (self._trex_host_ip_addr, self._trex_base_dir))

        log_file = "/tmp/trex/" + str(test_run) + "/trex-run.log"

        with open(log_file, 'r') as logfile_handle:
            mytext = logfile_handle.read()

             # summary stats results line
             # match.group(1) = Total-tx-bytes
             # match.group(2) = Total-tx-sw-bytes
             # match.group(3) = Total-rx-bytes
             # match.group(4) = Total-tx-pkt
             # match.group(5) = Total-rx-pkt
             # match.group(6) = Total-sw-tx-pkt
             # match.group(7) = Total-sw-err
             # match.group(8) = Total ARP sent
             # match.group(9) = Total ARP received
             # match.group(10) = maximum-latency
             # match.group(11) = average-latency
             # r'maximum-latency\s+\:\s+(\d+)\s+',
            search_pattern = re.compile(r'summary\s+stats\s+'
                                        r'\-+\s+.+\s+'
                                        r'Total-tx-bytes\s+\:\s+(\d+)\s+.+\s+'
                                        r'Total-tx-sw-bytes\s+\:\s+(\d+)\s+.+\s+'
                                        r'Total-rx-bytes\s+\:\s+(\d+)\s+.+\s+'
                                        r'Total-tx-pkt\s+\:\s+(\d+)\s+.+\s+'
                                        r'Total-rx-pkt\s+\:\s+(\d+)\s+.+\s+'
                                        r'Total-sw-tx-pkt\s+\:\s+(\d+)\s+.+\s+'
                                        r'Total-sw-err\s+\:\s+(\d+)\s+.+\s+'
                                        r'Total\s+ARP\s+sent\s+\:\s+(\d+)\s+.+\s+'
                                        r'Total\s+ARP\s+received\s+\:\s+(\d+)\s+.+\s+'
                                        r'maximum-latency\s+\:\s+(\d+)\s+.+\s+'
                                        r'average-latency\s+\:\s+(\d+)\s+.+\s+',
                                        re.IGNORECASE)

            results_match = search_pattern.search(mytext)

            if not results_match:
                logging.error('There was a problem parsing ' +
                              'Trex REPORT section of Trex log file')

            trex_results = OrderedDict()
            trex_results[ResultsConstants.THROUGHPUT_RX_FPS] = ResultsConstants.UNKNOWN_VALUE
            trex_results[ResultsConstants.THROUGHPUT_RX_MBPS] = ResultsConstants.UNKNOWN_VALUE
            trex_results[ResultsConstants.THROUGHPUT_RX_PERCENT] = ResultsConstants.UNKNOWN_VALUE
            trex_results[ResultsConstants.TX_RATE_FPS] = ResultsConstants.UNKNOWN_VALUE
            trex_results[ResultsConstants.TX_RATE_MBPS] = ResultsConstants.UNKNOWN_VALUE
            trex_results[ResultsConstants.TX_RATE_PERCENT] = ResultsConstants.UNKNOWN_VALUE
            trex_results[ResultsConstants.MAX_LATENCY_NS] = ResultsConstants.UNKNOWN_VALUE
            trex_results[ResultsConstants.MIN_LATENCY_NS] = ResultsConstants.UNKNOWN_VALUE
            trex_results[ResultsConstants.AVG_LATENCY_NS] = ResultsConstants.UNKNOWN_VALUE
            trex_results[ResultsConstants.FRAME_LOSS_PERCENT] = ResultsConstants.UNKNOWN_VALUE

        if results_match:

            trex_results[ResultsConstants.FRAME_LOSS_PERCENT] = (
                (((float(results_match.group(5)) - float(results_match.group(4))) * 100)
                 / float(results_match.group(5))))

            trex_results[ResultsConstants.THROUGHPUT_RX_FPS] = (
                float(results_match.group(5)) / int(duration))

            trex_results[ResultsConstants.TX_RATE_FPS] = (
                float(results_match.group(4)) / int(duration))

            trex_results[ResultsConstants.THROUGHPUT_RX_MBPS] = (
                ((float(results_match.group(3)) * 8) / 1000000) / int(duration))

            trex_results[ResultsConstants.TX_RATE_MBPS] = (
                ((float(results_match.group(1)) * 8) / 1000000) / int(duration))

            trex_results[ResultsConstants.MAX_LATENCY_NS] = (
                float(results_match.group(10)))

            trex_results[ResultsConstants.AVG_LATENCY_NS] = (
                results_match.group(11))

        return trex_results

    def send_rfc2544_throughput(self, traffic=None, duration=10,
                                lossrate=0.0, tests=1):
        """See ITrafficGenerator for description
        """
        return NotImplementedError(
            'Trex send rfc2544 throughput not implemented')

    def start_rfc2544_throughput(self, traffic=None, tests=1, duration=10,
                                 lossrate=0.0):
        return NotImplementedError(
            'Trex start rfc2544 throughput not implemented')

    def wait_rfc2544_throughput(self):
        return NotImplementedError(
            'Trex wait rfc2544 throughput not implemented')

    def send_burst_traffic(self, traffic=None, numpkts=100, duration=20):
        return NotImplementedError(
            'Trex send burst traffic not implemented')

    def send_rfc2544_back2back(self, traffic=None, tests=1, duration=20,
                               lossrate=0.0):
        return NotImplementedError(
            'Trex send rfc2544 back2back not implemented')

    def start_cont_traffic(self, traffic=None, duration=5):
        return NotImplementedError(
            'Trex start cont traffic not implemented')

    def start_rfc2544_back2back(self, traffic=None, tests=1, duration=20,
                                lossrate=0.0):
        return NotImplementedError(
            'Trex start rfc2544 back2back not implemented')

    def wait_rfc2544_back2back(self):
        return NotImplementedError(
            'Trex wait rfc2544 back2back not implemented')

if __name__ == "__main__":
    pass
