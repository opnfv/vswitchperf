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
# pylint: disable=undefined-variable
import logging
import subprocess
import sys
from collections import OrderedDict
# pylint: disable=unused-import
import zmq
from conf import settings
from conf import merge_spec
from core.results.results_constants import ResultsConstants
from tools.functions import ip_to_int
from tools.pkt_gen.trafficgen.trafficgen import ITrafficGenerator
# pylint: disable=wrong-import-position, import-error
sys.path.append(settings.getValue('PATHS')['trafficgen']['trex']['src']['path'])
from trex_stl_lib.api import *

_EMPTY_STATS = {
    'global': {'bw_per_core': 0.0,
               'cpu_util': 0.0,
               'queue_full': 0.0,
               'rx_bps': 0.0,
               'rx_cpu_util': 0.0,
               'rx_drop_bps': 0.0,
               'rx_pps': 0.0,
               'tx_bps': 0.0,
               'tx_pps': 0.0,},
    'latency': {},
    'total': {'ibytes': 0.0,
              'ierrors': 0.0,
              'ipackets': 0.0,
              'obytes': 0.0,
              'oerrors': 0.0,
              'opackets': 0.0,
              'rx_bps': 0.0,
              'rx_bps_L1': 0.0,
              'rx_pps': 0.0,
              'rx_util': 0.0,
              'tx_bps': 0.0,
              'tx_bps_L1': 0.0,
              'tx_pps': 0.0,
              'tx_util': 0.0,}}

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
        self._stlclient = None

    def connect(self):
        '''Connect to Trex traffic generator

        Verify that Trex is on the system indicated by
        the configuration file
        '''
        self._stlclient = STLClient()
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

        self._stlclient = STLClient(username=self._trex_user, server=self._trex_host_ip_addr,
                                    verbose_level=0)
        self._stlclient.connect()
        self._logger.info("TREX: Trex host successfully found...")

    def disconnect(self):
        """Disconnect from the traffic generator.

        As with :func:`connect`, this function is optional.

        Where implemented, this function should raise an exception on
        failure.

        :returns: None
        """
        self._logger.info("TREX: In trex disconnect method")
        self._stlclient.disconnect(stop_traffic=True, release_ports=True)

    @staticmethod
    def create_packets(traffic, ports_info):
        """Create base packet according to traffic specification.
           If traffic haven't specified srcmac and dstmac fields
           packet will be create with mac address of trex server.
        """
        mac_add = [li['hw_mac'] for li in ports_info]

        if traffic and traffic['l2']['framesize'] > 0:
            if traffic['l2']['dstmac'] == '00:00:00:00:00:00' and \
               traffic['l2']['srcmac'] == '00:00:00:00:00:00':
                base_pkt_a = Ether(src=mac_add[0], dst=mac_add[1])/ \
                             IP(proto=traffic['l3']['proto'], src=traffic['l3']['srcip'],
                                dst=traffic['l3']['dstip'])/ \
                             UDP(dport=traffic['l4']['dstport'], sport=traffic['l4']['srcport'])
                base_pkt_b = Ether(src=mac_add[1], dst=mac_add[0])/ \
                             IP(proto=traffic['l3']['proto'], src=traffic['l3']['dstip'],
                                dst=traffic['l3']['srcip'])/ \
                             UDP(dport=traffic['l4']['srcport'], sport=traffic['l4']['dstport'])
            else:
                base_pkt_a = Ether(src=traffic['l2']['srcmac'], dst=traffic['l2']['dstmac'])/ \
                             IP(proto=traffic['l3']['proto'], src=traffic['l3']['dstip'],
                                dst=traffic['l3']['srcip'])/ \
                             UDP(dport=traffic['l4']['dstport'], sport=traffic['l4']['srcport'])

                base_pkt_b = Ether(src=traffic['l2']['dstmac'], dst=traffic['l2']['srcmac'])/ \
                             IP(proto=traffic['l3']['proto'], src=traffic['l3']['dstip'],
                                dst=traffic['l3']['srcip'])/ \
                             UDP(dport=traffic['l4']['srcport'], sport=traffic['l4']['dstport'])

        return (base_pkt_a, base_pkt_b)

    @staticmethod
    def create_streams(base_pkt_a, base_pkt_b, traffic):
        """Add the base packet to the streams. Erase FCS and add payload
           according to traffic specification
        """
        stream_1_lat = None
        stream_2_lat = None
        frame_size = int(traffic['l2']['framesize'])
        fsize_no_fcs = frame_size - 4
        payload_a = max(0, fsize_no_fcs - len(base_pkt_a)) * 'x'
        payload_b = max(0, fsize_no_fcs - len(base_pkt_b)) * 'x'

        # Multistream configuration, increments source values only
        ms_mod = list() # mod list for incrementing values to be populated based on layer
        if traffic['multistream']:
            if traffic['stream_type'].upper() == 'L2':
                for _ in [base_pkt_a, base_pkt_b]:
                    ms_mod += [ STLVmFlowVar(name="mac_start", min_value=0,
                                             max_value=traffic['multistream'], size=4, op="inc"),
                                STLVmWrFlowVar(fv_name="mac_start", pkt_offset=7) ]
            elif traffic['stream_type'].upper() == 'L3':
                ip_src = {"start": ip_to_int(traffic['l3']['srcip']),
                          "end": ip_to_int(traffic['l3']['srcip']) + traffic['multistream']}
                ip_dst = {"start": ip_to_int(traffic['l3']['dstip']),
                          "end": ip_to_int(traffic['l3']['dstip']) + traffic['multistream']}
                for ip in [ip_src, ip_dst]:
                    ms_mod += [ STLVmFlowVar(name="ip_src", min_value=ip['start'],
                                            max_value=ip['end'], size=4,op="inc"),
                               STLVmWrFlowVar(fv_name="ip_src", pkt_offset= "IP.src") ]
            elif traffic['stream_type'].upper() == 'L4':
                stream_count = 65535 if traffic['multistream'] > 65535 else traffic['multistream']
                for udpport in [traffic['l4']['srcport'], traffic['l4']['dstport']]:
                    if udpport + stream_count > 65535:
                        start_port = udpport
                        # find the max/min port number based on the loop around of 65535 to 0 if needed
                        minimum_value = 65535 - stream_count
                        maximum_value = 65535
                    else:
                        start_port, minimum_value = udpport, udpport
                        maximum_value = start_port + stream_count
                    ms_mod += [ STLVmFlowVar(name = "port_src", init_value = start_port,
                                             min_value = minimum_value, max_value = maximum_value,
                                             size = 2, op = "inc"),
                                STLVmWrFlowVar(fv_name = "port_src", pkt_offset = "UDP" + ".sport"), ]

        if ms_mod: # multistream detected
            pkt_a = STLPktBuilder(pkt=base_pkt_a/payload_a, vm=[ms_mod[0], ms_mod[1]])
            pkt_b = STLPktBuilder(pkt=base_pkt_b/payload_b, vm=[ms_mod[2], ms_mod[3]])
        else:
            pkt_a = STLPktBuilder(pkt=base_pkt_a / payload_a)
            pkt_b = STLPktBuilder(pkt=base_pkt_b / payload_b)

        stream_1 = STLStream(packet=pkt_a,
                             name='stream_1',
                             mode=STLTXCont(percentage=traffic['frame_rate']))
        stream_2 = STLStream(packet=pkt_b,
                             name='stream_2',
                             mode=STLTXCont(percentage=traffic['frame_rate']))
        lat_pps = settings.getValue('TRAFFICGEN_TREX_LATENCY_PPS')
        if lat_pps > 0:
            stream_1_lat = STLStream(packet=pkt_a,
                                     flow_stats=STLFlowLatencyStats(pg_id=0),
                                     name='stream_1_lat',
                                     mode=STLTXCont(pps=lat_pps))
            stream_2_lat = STLStream(packet=pkt_b,
                                     flow_stats=STLFlowLatencyStats(pg_id=1),
                                     name='stream_2_lat',
                                     mode=STLTXCont(pps=lat_pps))

        return (stream_1, stream_2, stream_1_lat, stream_2_lat)

    def generate_traffic(self, traffic, duration):
        """The method that generate a stream
        """
        my_ports = [0, 1]
        self._stlclient.reset(my_ports)
        ports_info = self._stlclient.get_port_info(my_ports)
        # for SR-IOV
        if settings.getValue('TRAFFICGEN_TREX_PROMISCUOUS'):
            self._stlclient.set_port_attr(my_ports, promiscuous=True)

        packet_1, packet_2 = Trex.create_packets(traffic, ports_info)
        stream_1, stream_2, stream_1_lat, stream_2_lat = Trex.create_streams(packet_1, packet_2, traffic)
        self._stlclient.add_streams(stream_1, ports=[0])
        self._stlclient.add_streams(stream_2, ports=[1])

        if stream_1_lat is not None:
            self._stlclient.add_streams(stream_1_lat, ports=[0])
            self._stlclient.add_streams(stream_2_lat, ports=[1])

        self._stlclient.clear_stats()
        self._stlclient.start(ports=[0, 1], force=True, duration=duration)
        self._stlclient.wait_on_traffic(ports=[0, 1])
        stats = self._stlclient.get_stats(sync_now=True)
        return stats

    @staticmethod
    def calculate_results(stats):
        """Calculate results from Trex statistic
        """
        result = OrderedDict()
        result[ResultsConstants.TX_RATE_FPS] = (
            '{:.3f}'.format(
                float(stats["total"]["tx_pps"])))

        result[ResultsConstants.THROUGHPUT_RX_FPS] = (
            '{:.3f}'.format(
                float(stats["total"]["rx_pps"])))

        result[ResultsConstants.TX_RATE_MBPS] = (
            '{:.3f}'.format(
                float(stats["total"]["tx_bps"] / 1000000)))
        result[ResultsConstants.THROUGHPUT_RX_MBPS] = (
            '{:.3f}'.format(
                float(stats["total"]["rx_bps"] / 1000000)))

        result[ResultsConstants.TX_RATE_PERCENT] = 'Unknown'

        result[ResultsConstants.THROUGHPUT_RX_PERCENT] = 'Unknown'
        if stats["total"]["opackets"]:
            result[ResultsConstants.FRAME_LOSS_PERCENT] = (
                '{:.3f}'.format(
                    float((stats["total"]["opackets"] - stats["total"]["ipackets"]) * 100 /
                          stats["total"]["opackets"])))
        else:
            result[ResultsConstants.FRAME_LOSS_PERCENT] = 100

        if settings.getValue('TRAFFICGEN_TREX_LATENCY_PPS') > 0 and stats['latency']:
            result[ResultsConstants.MIN_LATENCY_NS] = (
                '{:.3f}'.format(
                    (float(min(stats["latency"][0]["latency"]["total_min"],
                               stats["latency"][1]["latency"]["total_min"])))))

            result[ResultsConstants.MAX_LATENCY_NS] = (
                '{:.3f}'.format(
                    (float(max(stats["latency"][0]["latency"]["total_max"],
                               stats["latency"][1]["latency"]["total_max"])))))

            result[ResultsConstants.AVG_LATENCY_NS] = (
                '{:.3f}'.format(
                    float((stats["latency"][0]["latency"]["average"]+
                           stats["latency"][1]["latency"]["average"])/2)))

        else:
            result[ResultsConstants.MIN_LATENCY_NS] = 'Unknown'
            result[ResultsConstants.MAX_LATENCY_NS] = 'Unknown'
            result[ResultsConstants.AVG_LATENCY_NS] = 'Unknown'
        return result

    def send_cont_traffic(self, traffic=None, duration=30):
        """See ITrafficGenerator for description
        """
        self._logger.info("In Trex send_cont_traffic method")
        self._params.clear()

        self._params['traffic'] = self.traffic_defaults.copy()
        if traffic:
            self._params['traffic'] = merge_spec(
                self._params['traffic'], traffic)

        stats = self.generate_traffic(traffic, duration)

        return self.calculate_results(stats)

    def start_cont_traffic(self, traffic=None, duration=30):
        raise NotImplementedError(
            'Trex start cont traffic not implemented')

    def stop_cont_traffic(self):
        """See ITrafficGenerator for description
        """
        raise NotImplementedError(
            'Trex stop_cont_traffic method not implemented')

    def send_rfc2544_throughput(self, traffic=None, duration=60,
                                lossrate=0.0, tests=10):
        """See ITrafficGenerator for description
        """
        self._logger.info("In Trex send_rfc2544_throughput method")
        self._params.clear()
        threshold = settings.getValue('TRAFFICGEN_TREX_RFC2544_TPUT_THRESHOLD')
        test_lossrate = 0
        left = 0
        iteration = 1
        stats_ok = _EMPTY_STATS
        self._params['traffic'] = self.traffic_defaults.copy()
        if traffic:
            self._params['traffic'] = merge_spec(
                self._params['traffic'], traffic)
        new_params = copy.deepcopy(traffic)
        stats = self.generate_traffic(traffic, duration)
        right = traffic['frame_rate']
        center = traffic['frame_rate']

        # Loops until the preconfigured difference between frame rate
        # of successful and unsuccessful iterations is reached
        while (right - left) > threshold:
            test_lossrate = ((stats["total"]["opackets"] - stats["total"]
                              ["ipackets"]) * 100) / stats["total"]["opackets"]
            self._logger.debug("Iteration: %s, frame rate: %s, throughput_rx_fps: %s, frame_loss_percent: %s",
                               iteration, "{:.3f}".format(new_params['frame_rate']), stats['total']['rx_pps'],
                               "{:.3f}".format(test_lossrate))
            if test_lossrate == 0.0 and new_params['frame_rate'] == traffic['frame_rate']:
                stats_ok = copy.deepcopy(stats)
                break
            elif test_lossrate > lossrate:
                right = center
                center = (left+right) / 2
                new_params = copy.deepcopy(traffic)
                new_params['frame_rate'] = center
                stats = self.generate_traffic(new_params, duration)
            else:
                stats_ok = copy.deepcopy(stats)
                left = center
                center = (left+right) / 2
                new_params = copy.deepcopy(traffic)
                new_params['frame_rate'] = center
                stats = self.generate_traffic(new_params, duration)
            iteration += 1
        return self.calculate_results(stats_ok)

    def start_rfc2544_throughput(self, traffic=None, tests=1, duration=60,
                                 lossrate=0.0):
        raise NotImplementedError(
            'Trex start rfc2544 throughput not implemented')

    def wait_rfc2544_throughput(self):
        raise NotImplementedError(
            'Trex wait rfc2544 throughput not implemented')

    def send_burst_traffic(self, traffic=None, numpkts=100, duration=5):
        raise NotImplementedError(
            'Trex send burst traffic not implemented')

    def send_rfc2544_back2back(self, traffic=None, tests=1, duration=30,
                               lossrate=0.0):
        raise NotImplementedError(
            'Trex send rfc2544 back2back not implemented')

    def start_rfc2544_back2back(self, traffic=None, tests=1, duration=30,
                                lossrate=0.0):
        raise NotImplementedError(
            'Trex start rfc2544 back2back not implemented')

    def wait_rfc2544_back2back(self):
        raise NotImplementedError(
            'Trex wait rfc2544 back2back not implemented')

if __name__ == "__main__":
    pass
