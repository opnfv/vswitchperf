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
"""RFC2544 Traffic Controller implementation.
"""
import logging

from core.traffic_controller import ITrafficController
from core.results.results_constants import ResultsConstants
from core.results.results import IResults
from conf import settings
from conf import get_test_param


class TrafficControllerRFC2544(ITrafficController, IResults):
    """Traffic controller for RFC2544 traffic

    Used to setup and control a traffic generator for an RFC2544 deployment
    traffic scenario.
    """

    def __init__(self, traffic_gen_class):
        """Initialise the trafficgen and store.

        :param traffic_gen_class: The traffic generator class to be used.
        """
        self._logger = logging.getLogger(__name__)
        self._logger.debug("__init__")
        self._traffic_gen_class = traffic_gen_class()
        self._traffic_started = False
        self._traffic_started_call_count = 0
        self._packet_sizes = settings.getValue('TRAFFICGEN_PKT_SIZES')
        self._trials = get_test_param('rfc2544_trials', 1)
        self._results = []

    def __enter__(self):
        """Call initialisation function.
        """
        self._traffic_gen_class.connect()

    def __exit__(self, type_, value, traceback):
        """Stop traffic, clean up.
        """
        if self._traffic_started:
            self.stop_traffic()

    @staticmethod
    def _append_results(result_dict, packet_size):
        """Adds common values to traffic generator results.

        :param result_dict: Dictionary containing results from trafficgen
        :param packet_size: Packet size value.

        :returns: dictionary of results with addictional entries.
        """

        ret_value = result_dict

        #TODO Old TOIT controller had knowledge about scenario beeing
        #executed, should new controller also fill Configuration & ID,
        # or this should be passed to TestCase?
        ret_value[ResultsConstants.TYPE] = 'rfc2544'
        ret_value[ResultsConstants.PACKET_SIZE] = str(packet_size)

        return ret_value

    def send_traffic(self, traffic):
        """See ITrafficController for description
        """
        self._logger.debug('send_traffic with ' +
                           str(self._traffic_gen_class))

        for packet_size in self._packet_sizes:
            traffic['l2'] = {'framesize': packet_size}
            result = self._traffic_gen_class.send_rfc2544_throughput(
                traffic,
                trials=int(self._trials),
                duration=int(get_test_param('rfc2544_duration', 20)))
            result = TrafficControllerRFC2544._append_results(result,
                                                              packet_size)
            self._results.append(result)

    def send_traffic_async(self, traffic, function):
        """See ITrafficController for description
        """
        self._logger.debug('send_traffic_async with ' +
                           str(self._traffic_gen_class))

        for packet_size in self._packet_sizes:
            traffic['l2'] = {'framesize': packet_size}
            self._traffic_gen_class.start_rfc2544_throughput(
                traffic,
                trials=int(self._trials),
                duration=int(get_test_param('rfc2544_duration', 20)))
            self._traffic_started = True
            if len(function['args']) > 0:
                function['function'](function['args'])
            else:
                function['function']()
            result = self._traffic_gen_class.wait_rfc2544_throughput()
            result = TrafficControllerRFC2544._append_results(result,
                                                              packet_size)
            self._results.append(result)

    def stop_traffic(self):
        """Kills traffic being sent from the traffic generator.
        """
        self._logger.debug("stop_traffic()")

    def print_results(self):
        """IResult interface implementation.
        """
        counter = 0
        for item in self._results:
            logging.info("Record: " + str(counter))
            counter += 1
            for(key, value) in list(item.items()):
                logging.info("         Key: " + str(key) +
                             ", Value: " + str(value))


    def get_results(self):
        """IResult interface implementation.
        """
        return self._results
