# Copyright 2016 Spirent Communications, Intel Corporation.
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
"""RFC2889 Traffic Controller implementation.
"""
from core.traffic_controller import ITrafficController
from core.results.results import IResults
from conf import get_test_param


class TrafficControllerRFC2889(ITrafficController, IResults):
    """Traffic controller for RFC2889 traffic

    Used to setup and control a traffic generator for an RFC2889 deployment
    traffic scenario.
    """

    def __init__(self, traffic_gen_class):
        """Initialise the trafficgen and store.

        :param traffic_gen_class: The traffic generator class to be used.
        """
        super(TrafficControllerRFC2889, self).__init__(traffic_gen_class)
        self._type = 'rfc2889'
        self._trials = int(get_test_param('rfc2889_trials', 1))

    def send_traffic(self, traffic):
        """See ITrafficController for description
        """
        if not self.traffic_required():
            return
        self._logger.debug('send_traffic with ' +
                           str(self._traffic_gen_class))

        for packet_size in self._packet_sizes:
            # Merge framesize with the default traffic definition
            if 'l2' in traffic:
                traffic['l2'] = dict(traffic['l2'],
                                     **{'framesize': packet_size})
            else:
                traffic['l2'] = {'framesize': packet_size}

            if traffic['traffic_type'] == 'caching':
                result = self._traffic_gen_class.send_rfc2889_caching(
                    traffic, trials=self._trials, duration=self._duration)
            elif traffic['traffic_type'] == 'congestion':
                result = self._traffic_gen_class.send_rfc2889_congestion(
                    traffic, duration=self._duration)
            else:
                result = self._traffic_gen_class.send_rfc2889_forwarding(
                    traffic, tests=self._trials, duration=self._duration)

            result = self._append_results(result, packet_size)
            self._results.append(result)

    def send_traffic_async(self, traffic, function):
        """See ITrafficController for description
        """
        if not self.traffic_required():
            return
        self._logger.debug('send_traffic_async with ' +
                           str(self._traffic_gen_class))

        for packet_size in self._packet_sizes:
            traffic['l2'] = {'framesize': packet_size}
            self._traffic_gen_class.start_rfc2889_forwarding(
                traffic,
                trials=self._trials,
                duration=self._duration)
            self._traffic_started = True
            if len(function['args']) > 0:
                function['function'](function['args'])
            else:
                function['function']()
            result = self._traffic_gen_class.wait_rfc2889_forwarding(
                        traffic, trials=self._trials, duration=self._duration)
            result = self._append_results(result, packet_size)
            self._results.append(result)

