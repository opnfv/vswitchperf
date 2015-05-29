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
"""Abstract "traffic generator" model.

This is an abstract class for traffic generators.
"""

#TODO update Back2Back method description when Result implementation will
#be ready.

from tools.pkt_gen.trafficgen.trafficgenhelper import TRAFFIC_DEFAULTS

class ITrafficGenerator(object):
    """Model of a traffic generator device.
    """
    _traffic_defaults = TRAFFIC_DEFAULTS.copy()

    @property
    def traffic_defaults(self):
        """Default traffic values.

        These can be expected to be constant across traffic generators,
        so no setter is provided. Changes to the structure or contents
        will likely break traffic generator implementations or tests
        respectively.
        """
        return self._traffic_defaults

    def __enter__(self):
        """Connect to the traffic generator.

        Provide a context manager interface to the traffic generators.
        This simply calls the :func:`connect` function.
        """
        return self.connect()

    def __exit__(self, type_, value, traceback):
        """Disconnect from the traffic generator.

        Provide a context manager interface to the traffic generators.
        This simply calls the :func:`disconnect` function.
        """
        self.disconnect()

    def connect(self):
        """Connect to the traffic generator.

        This is an optional function, designed for traffic generators
        which must be "connected to" (i.e. via SSH or an API) before
        they can be used. If not required, simply do nothing here.

        Where implemented, this function should raise an exception on
        failure.

        :returns: None
        """
        raise NotImplementedError('Please call an implementation.')

    def disconnect(self):
        """Disconnect from the traffic generator.

        As with :func:`connect`, this function is optional.

        Where implemented, this function should raise an exception on
        failure.

        :returns: None
        """
        raise NotImplementedError('Please call an implementation.')

    def send_burst_traffic(self, traffic=None, numpkts=100,
                           time=20, framerate=100):
        """Send a burst of traffic.

        Send a ``numpkts`` packets of traffic, using ``traffic``
        configuration, with a timeout of ``time``.

        Attributes:
        :param traffic: Detailed "traffic" spec, i.e. IP address, VLAN tags
        :param numpkts: Number of packets to send
        :param framerate: Expected framerate
        :param time: Time to wait to receive packets

        :returns: dictionary of strings with following data:
            - List of Tx Frames,
            - List of Rx Frames,
            - List of Tx Bytes,
            - List of List of Rx Bytes,
            - Payload Errors and Sequence Errors.
        """
        raise NotImplementedError('Please call an implementation.')

    def send_cont_traffic(self, traffic=None, time=20, framerate=0,
                          multistream=False):
        """Send a continuous flow of traffic.

        Send packets at ``framerate``, using ``traffic`` configuration,
        until timeout ``time`` occurs.

        :param traffic: Detailed "traffic" spec, i.e. IP address, VLAN tags
        :param time: Time to wait to receive packets (secs)
        :param framerate: Expected framerate
        :param multistream: Enable multistream output by overriding the
                        UDP port number in ``traffic`` with values
                        from 1 to 64,000
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
        raise NotImplementedError('Please call an implementation.')

    def start_cont_traffic(self, traffic=None, time=20, framerate=0,
                           multistream=False):
        """Non-blocking version of 'send_cont_traffic'.

        Start transmission and immediately return. Do not wait for
        results.
        """
        raise NotImplementedError('Please call an implementation.')

    def stop_cont_traffic(self):
        """Stop continuous transmission and return results.
        """
        raise NotImplementedError('Please call an implementation.')

    def send_rfc2544_throughput(self, traffic=None, trials=3, duration=20,
                                lossrate=0.0, multistream=False):
        """Send traffic per RFC2544 throughput test specifications.

        Send packets at a variable rate, using ``traffic``
        configuration, until minimum rate at which no packet loss is
        detected is found.

        :param traffic: Detailed "traffic" spec, i.e. IP address, VLAN tags
        :param trials: Number of trials to execute
        :param duration: Per iteration duration
        :param lossrate: Acceptable lossrate percentage
        :param multistream: Enable multistream output by overriding the
                        UDP port number in ``traffic`` with values
                        from 1 to 64,000
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
        raise NotImplementedError('Please call an implementation.')

    def start_rfc2544_throughput(self, traffic=None, trials=3, duration=20,
                                 lossrate=0.0, multistream=False):
        """Non-blocking version of 'send_rfc2544_throughput'.

        Start transmission and immediately return. Do not wait for
        results.
        """
        raise NotImplementedError('Please call an implementation.')

    def wait_rfc2544_throughput(self):
        """Wait for and return results of RFC2544 test.
        """
        raise NotImplementedError('Please call an implementation.')

    def send_rfc2544_back2back(self, traffic=None, trials=1, duration=20,
                               lossrate=0.0, multistream=False):
        """Send traffic per RFC2544 back2back test specifications.

        Send packets at a fixed rate, using ``traffic``
        configuration, until minimum time at which no packet loss is
        detected is found.

        :param traffic: Detailed "traffic" spec, i.e. IP address, VLAN
            tags
        :param trials: Number of trials to execute
        :param duration: Per iteration duration
        :param lossrate: Acceptable loss percentage
        :param multistream: Enable multistream output by overriding the
            UDP port number in ``traffic`` with values from 1 to 64,000

        :returns: Named tuple of Rx Throughput (fps), Rx Throughput (mbps),
            Tx Rate (% linerate), Rx Rate (% linerate), Tx Count (frames),
            Back to Back Count (frames), Frame Loss (frames), Frame Loss (%)
        :rtype: :class:`Back2BackResult`
        """
        raise NotImplementedError('Please call an implementation.')

    def start_rfc2544_back2back(self, traffic=None, trials=1, duration=20,
                                lossrate=0.0, multistream=False):
        """Non-blocking version of 'send_rfc2544_back2back'.

        Start transmission and immediately return. Do not wait for
        results.
        """
        raise NotImplementedError('Please call an implementation.')

    def wait_rfc2544_back2back(self):
        """Wait and set results of RFC2544 test.
        """
        raise NotImplementedError('Please call an implementation.')
