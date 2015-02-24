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

"""
Abstract "traffic generator" model.

This is an abstract class for traffic generators.

Part of 'toit' - The OVS Integration Testsuite.
"""

from collections import namedtuple

CMD_PREFIX = 'gencmd : '
TRAFFIC_DEFAULTS = {
    'l2': {
        'framesize': 64,
        'srcmac': '00:00:00:00:00:00',
        'dstmac': '00:00:00:00:00:00',
        'srcport': 3000,
        'dstport': 3001,
    },
    'l3': {
        'proto': 'tcp',
        'srcip': '1.1.1.1',
        'dstip': '90.90.90.90',
    },
    'vlan': {
        'enabled': False,
        'id': 0,
        'priority': 0,
        'cfi': 0,
    },
}

BurstResult = namedtuple(
    'BurstResult',
    'frames_tx frames_rx bytes_tx bytes_rx payload_err seq_err')
ContResult = namedtuple(
    'ContResult',
    'tx_fps rx_fps tx_mbps rx_mbps tx_percent rx_percent min_latency '
    'max_latency avg_latency')
ThroughputResult = namedtuple(
    'ThroughputResult',
    'tx_fps rx_fps tx_mbps rx_mbps tx_percent rx_percent min_latency '
    'max_latency avg_latency')


def merge_spec(orig, new):
    """
    Merges ``new`` dict with ``orig`` dict, and return orig.

    This takes into account nested dictionaries. Example:

        >>> old = {'foo': 1, 'bar': {'foo': 2, 'bar': 3}}
        >>> new = {'foo': 6, 'bar': {'foo': 7}}
        >>> merge_spec(old, new)
        {'foo': 3, 'bar': {'foo': 7, 'bar': 3}}

    You'll notice that ``bar.bar`` is not removed. This is the desired result.
    """
    for key in orig:
        if key not in new:
            continue

        if type(orig[key]) == dict:
            orig[key] = merge_spec(orig[key], new[key])
        else:
            orig[key] = new[key]

    for key in new:
        if key not in orig:
            orig[key] = new[key]

    return orig


class TrafficGenerator(object):
    """Model of a traffic generator device."""
    _traffic_defaults = TRAFFIC_DEFAULTS.copy()

    @property
    def traffic_defaults(self):
        """
        Default traffic values.

        These can be expected to be constant across traffic generators,
        so no setter is provided. Changes to the structure or contents
        will likely break traffic generator implementations or tests
        respectively.
        """
        return self._traffic_defaults

    def __enter__(self):
        """
        Connect to the traffic generator.

        Provide a context manager interface to the traffic generators.
        This simply calls the :func:`connect` function.
        """
        return self.connect()

    def __exit__(self, type_, value, traceback):
        """
        Disconnect from the traffic generator.

        Provide a context manager interface to the traffic generators.
        This simply calls the :func:`disconnect` function.
        """
        self.disconnect()

    def connect(self):
        """
        Connect to the traffic generator.

        This is an optional function, designed for traffic generators
        which must be "connected to" (i.e. via SSH or an API) before
        they can be used. If not required, simply do nothing here.

        Where implemented, this function should raise an exception on
        failure.

        :returns: None
        """
        raise NotImplementedError('Please call an implementation.')

    def disconnect(self):
        """
        Disconnect from the traffic generator.

        As with :func:`connect`, this function is optional.

        Where implemented, this function should raise an exception on
        failure.

        :returns: None
        """
        raise NotImplementedError('Please call an implementation.')

    def send_burst_traffic(self, traffic=None, numpkts=100, time=20):
        """
        Send a burst of traffic.

        Send a ``numpkts`` packets of traffic, using ``traffic``
        configuration, with a timeout of ``time``.

        :param traffic: Detailed "traffic" spec, i.e. IP address, VLAN tags
        :param numpkts: Number of packets to send
        :params time: Time to wait to receive packets

        :returns: List of Tx Frames, Rx Frames, Tx Bytes, Rx Bytes,
            Payload Errors and Sequence Errors.
        :rtype: [int, int, int, int, int, int]
        """
        raise NotImplementedError('Please call an implementation.')

    def send_cont_traffic(self, traffic=None, time=20, framerate=0):
        """
        Send a continuous flow of traffic.

        Send packets at ``framerate``, using ``traffic`` configuration,
        until timeout ``time`` occurs.

        :param traffic: Detailed "traffic" spec, i.e. IP address, VLAN
            tags
        :params time: Time to wait to receive packets (secs)
        :params framerate: Expected framerate

        :returns: Named tuple of Tx Throughput (fps), Rx Throughput
            (fps), Tx Throughput (mbps), Rx Throughput (mbps), Tx
            Throughput (% linerate), Rx Throughput (% linerate), Min
            Latency (ns), Max Latency (ns) and Avg Latency (ns)
        :rtype: :class:`ThroughputResult`
        """
        raise NotImplementedError('Please call an implementation.')

    def start_cont_traffic(self, traffic=None, framerate=0):
        """
        Non-blocking version of 'send_cont_traffic'.

        Start transmission and immediately return. Do not wait for
        results.
        """
        raise NotImplementedError('Please call an implementation.')

    def stop_cont_traffic(self):
        """
        Stop continuous transmission and return results.
        """
        raise NotImplementedError('Please call an implementation.')

    def send_rfc2544_throughput(self, traffic=None, trials=3, duration=20,
                                lossrate=0.0, multistream=False):
        """
        Send traffic per RFC2544 throughput test specifications.

        Send packets at a variable rate, using ``traffic``
        configuration, until minimum rate at which no packet loss is
        detected is found.

        :param traffic: Detailed "traffic" spec, i.e. IP address, VLAN
            tags
        :param trials: Number of trials to execute
        :param duration: Per iteration duration
        :param lossrate: Acceptable lossrate percentage
        :param multistream: Enable multistream output by overriding the
            UDP port number in ``traffic`` with values from 1 to 64,000

        :returns: Named tuple of Tx Throughput (fps), Rx Throughput
            (fps), Tx Throughput (mbps), Rx Throughput (mbps), Tx
            Throughput (% linerate), Rx Throughput (% linerate), Min
            Latency (ns), Max Latency (ns) and Avg Latency (ns)
        :rtype: :class:`ThroughputResult`
        """
        raise NotImplementedError('Please call an implementation.')

    def start_rfc2544_throughput(self, traffic=None, trials=3, duration=20,
                                 lossrate=0.0, multistream=False):
        """
        Non-blocking version of 'send_rfc2544_throughput'.

        Start transmission and immediately return. Do not wait for
        results.
        """
        raise NotImplementedError('Please call an implementation.')

    def wait_rfc2544_throughput(self):
        """
        Wait for and return results of RFC2544 test.
        """
        raise NotImplementedError('Please call an implementation.')
