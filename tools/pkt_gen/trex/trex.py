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
import time
import os
from collections import OrderedDict
# pylint: disable=unused-import
import netaddr
import zmq
from conf import settings
from conf import merge_spec
from core.results.results_constants import ResultsConstants
from tools.pkt_gen.trafficgen.trafficgen import ITrafficGenerator
try:
    # pylint: disable=wrong-import-position, import-error
    sys.path.append(settings.getValue('PATHS')['trafficgen']['Trex']['src']['path'])
    from trex_stl_lib.api import *
    from trex_stl_lib import trex_stl_exceptions
except ImportError:
    # VSPERF performs detection of T-Rex api during testcase initialization. So if
    # T-Rex is requsted and API is not available it will fail before this code
    # is reached.
    # This code can be reached in case that --list-trafficgens is called, but T-Rex
    # api is not installed. In this case we can ignore an exception, becuase T-Rex
    # import won't be used.
    pass

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
        self._verification_params = None
        self._show_packet_data = False

    def show_packet_info(self, packet_a, packet_b):
        """
        Log packet layers to screen
        :param packet_a: Scapy.layers packet
        :param packet_b: Scapy.layers packet
        :return: None
        """
        # we only want to show packet data once per test
        if self._show_packet_data:
            self._show_packet_data = False
            self._logger.info(packet_a.show())
            self._logger.info(packet_b.show())

    def connect(self):
        '''Connect to Trex traffic generator

        Verify that Trex is on the system indicated by
        the configuration file
        '''
        self._stlclient = STLClient()
        self._logger.info("T-Rex:  In Trex connect method...")
        if self._trex_host_ip_addr:
            cmd_ping = "ping -c1 " + self._trex_host_ip_addr
        else:
            raise RuntimeError('T-Rex: Trex host not defined')

        ping = subprocess.Popen(cmd_ping, shell=True, stderr=subprocess.PIPE)
        output, error = ping.communicate()

        if ping.returncode:
            self._logger.error(error)
            self._logger.error(output)
            raise RuntimeError('T-Rex: Cannot ping Trex host at ' + \
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
                'T-Rex: Cannot locate Trex program at %s within %s' \
                % (self._trex_host_ip_addr, self._trex_base_dir))

        try:
            self._stlclient = STLClient(username=self._trex_user, server=self._trex_host_ip_addr,
                                        verbose_level=0)
            self._stlclient.connect()
        except STLError:
            raise RuntimeError('T-Rex: Cannot connect to T-Rex server. Please check if it is '
                               'running and that firewall allows connection to TCP port 4501.')

        self._logger.info("T-Rex: Trex host successfully found...")

    def disconnect(self):
        """Disconnect from the traffic generator.

        As with :func:`connect`, this function is optional.

        Where implemented, this function should raise an exception on
        failure.

        :returns: None
        """
        self._logger.info("T-Rex: In trex disconnect method")
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
        if traffic['multistream'] > 1:
            if traffic['stream_type'].upper() == 'L2':
                for _ in [base_pkt_a, base_pkt_b]:
                    ms_mod += [STLVmFlowVar(name="mac_start", min_value=0,
                                            max_value=traffic['multistream'] - 1, size=4, op="inc"),
                               STLVmWrFlowVar(fv_name="mac_start", pkt_offset=7)]
            elif traffic['stream_type'].upper() == 'L3':
                ip_src = {"start": int(netaddr.IPAddress(traffic['l3']['srcip'])),
                          "end": int(netaddr.IPAddress(traffic['l3']['srcip'])) + traffic['multistream'] - 1}
                ip_dst = {"start": int(netaddr.IPAddress(traffic['l3']['dstip'])),
                          "end": int(netaddr.IPAddress(traffic['l3']['dstip'])) + traffic['multistream'] - 1}
                for ip_address in [ip_src, ip_dst]:
                    ms_mod += [STLVmFlowVar(name="ip_src", min_value=ip_address['start'],
                                            max_value=ip_address['end'], size=4, op="inc"),
                               STLVmWrFlowVar(fv_name="ip_src", pkt_offset="IP.src")]
            elif traffic['stream_type'].upper() == 'L4':
                for udpport in [traffic['l4']['srcport'], traffic['l4']['dstport']]:
                    if udpport + (traffic['multistream'] - 1) > 65535:
                        start_port = udpport
                        # find the max/min port number based on the loop around of 65535 to 0 if needed
                        minimum_value = 65535 - (traffic['multistream'] -1)
                        maximum_value = 65535
                    else:
                        start_port, minimum_value = udpport, udpport
                        maximum_value = start_port + (traffic['multistream'] - 1)
                    ms_mod += [STLVmFlowVar(name="port_src", init_value=start_port,
                                            min_value=minimum_value, max_value=maximum_value,
                                            size=2, op="inc"),
                               STLVmWrFlowVar(fv_name="port_src", pkt_offset="UDP.sport"),]

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

    def generate_traffic(self, traffic, duration, disable_capture=False):
        """The method that generate a stream
        """
        my_ports = [0, 1]

        # initialize ports
        self._stlclient.reset(my_ports)
        self._stlclient.remove_all_captures()
        self._stlclient.set_service_mode(ports=my_ports, enabled=False)

        ports_info = self._stlclient.get_port_info(my_ports)

        # get max support speed
        max_speed = 0
        if settings.getValue('TRAFFICGEN_TREX_FORCE_PORT_SPEED'):
            max_speed = settings.getValue('TRAFFICGEN_TREX_PORT_SPEED')
        elif ports_info[0]['supp_speeds']:
            max_speed_1 = max(ports_info[0]['supp_speeds'])
            max_speed_2 = max(ports_info[1]['supp_speeds'])
        else:
            # if max supported speed not in port info or set manually, just assume 10G
            max_speed = 10000
        if not max_speed:
            # since we can only control both ports at once take the lower of the two
            max_speed = min(max_speed_1, max_speed_2)
        gbps_speed = (max_speed / 1000) * (float(traffic['frame_rate']) / 100.0)
        self._logger.debug('Starting traffic at %s Gpbs speed', gbps_speed)

        # for SR-IOV
        if settings.getValue('TRAFFICGEN_TREX_PROMISCUOUS'):
            self._stlclient.set_port_attr(my_ports, promiscuous=True)

        packet_1, packet_2 = Trex.create_packets(traffic, ports_info)
        self.show_packet_info(packet_1, packet_2)
        stream_1, stream_2, stream_1_lat, stream_2_lat = Trex.create_streams(packet_1, packet_2, traffic)
        self._stlclient.add_streams(stream_1, ports=[0])
        self._stlclient.add_streams(stream_2, ports=[1])

        if stream_1_lat is not None:
            self._stlclient.add_streams(stream_1_lat, ports=[0])
            self._stlclient.add_streams(stream_2_lat, ports=[1])

        # enable traffic capture if requested
        pcap_id = {}
        if traffic['capture']['enabled'] and not disable_capture:
            for ports in ['tx_ports', 'rx_ports']:
                if traffic['capture'][ports]:
                    pcap_dir = ports[:2]
                    self._logger.info("T-Rex starting %s traffic capture", pcap_dir.upper())
                    capture = {ports : traffic['capture'][ports],
                               'limit' : traffic['capture']['count'],
                               'bpf_filter' : traffic['capture']['filter']}
                    self._stlclient.set_service_mode(ports=traffic['capture'][ports], enabled=True)
                    pcap_id[pcap_dir] = self._stlclient.start_capture(**capture)

        self._stlclient.clear_stats()
        # if the user did not start up T-Rex server with more than default cores, use default mask.
        # Otherwise use mask to take advantage of multiple cores.
        try:
            self._stlclient.start(ports=my_ports, force=True, duration=duration, mult="{}gbps".format(gbps_speed),
                                  core_mask=self._stlclient.CORE_MASK_PIN)
        except STLError:
            self._stlclient.start(ports=my_ports, force=True, duration=duration, mult="{}gbps".format(gbps_speed))
        self._stlclient.wait_on_traffic(ports=my_ports)
        stats = self._stlclient.get_stats(sync_now=True)

        # export captured data into pcap file if possible
        if pcap_id:
            for pcap_dir in pcap_id:
                pcap_file = 'capture_{}.pcap'.format(pcap_dir)
                self._stlclient.stop_capture(pcap_id[pcap_dir]['id'],
                                             os.path.join(settings.getValue('RESULTS_PATH'), pcap_file))
                stats['capture_{}'.format(pcap_dir)] = pcap_file
                self._logger.info("T-Rex writing %s traffic capture into %s", pcap_dir.upper(), pcap_file)
            # disable service mode for all ports used by Trex
            self._stlclient.set_service_mode(ports=my_ports, enabled=False)

        return stats

    @staticmethod
    def calculate_results(stats):
        """Calculate results from Trex statistic
        """
        result = OrderedDict()
        result[ResultsConstants.TX_FRAMES] = (
            stats["total"]["opackets"])
        result[ResultsConstants.RX_FRAMES] = (
            stats["total"]["ipackets"])
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

        if 'capture_tx' in stats:
            result[ResultsConstants.CAPTURE_TX] = stats['capture_tx']
        if 'capture_rx' in stats:
            result[ResultsConstants.CAPTURE_RX] = stats['capture_rx']
        return result

    def learning_packets(self, traffic):
        """
        Send learning packets before testing
        :param traffic: traffic structure as per send_cont_traffic guidelines
        :return: None
        """
        self._logger.info("T-Rex sending learning packets")
        learning_thresh_traffic = copy.deepcopy(traffic)
        learning_thresh_traffic["frame_rate"] = 1
        self.generate_traffic(learning_thresh_traffic,
                              settings.getValue("TRAFFICGEN_TREX_LEARNING_DURATION"),
                              disable_capture=True)
        self._logger.info("T-Rex finished learning packets")
        time.sleep(3)  # allow packets to complete before starting test traffic

    def run_trials(self, traffic, boundaries, duration, lossrate):
        """
        Run rfc2544 trial loop
        :param traffic: traffic profile dictionary
        :param boundaries: A dictionary of three keys left, right, center to dictate
                          the highest, lowest, and starting point of the binary search.
                          Values are percentages of line rates for each key.
        :param duration: length in seconds for trials
        :param lossrate: loweset loss rate percentage calculated from
                         comparision between received and sent packets
        :return: passing stats as dictionary
        """
        threshold = settings.getValue('TRAFFICGEN_TREX_RFC2544_TPUT_THRESHOLD')
        stats_ok = _EMPTY_STATS
        new_params = copy.deepcopy(traffic)
        iteration = 1
        left = boundaries['left']
        right = boundaries['right']
        center = boundaries['center']
        self._logger.info('Starting RFC2544 trials')
        while (right - left) > threshold:
            stats = self.generate_traffic(new_params, duration)
            test_lossrate = ((stats["total"]["opackets"] - stats[
                "total"]["ipackets"]) * 100) / stats["total"]["opackets"]
            if stats["total"]["ipackets"] == 0:
                self._logger.error('No packets recieved. Test failed')
                return _EMPTY_STATS
            if settings.getValue('TRAFFICGEN_TREX_VERIFICATION_MODE'):
                if test_lossrate <= lossrate:
                    # save the last passing trial for verification
                    self._verification_params = copy.deepcopy(new_params)
            packets_lost = stats['total']['opackets'] - stats['total']['ipackets']
            self._logger.debug('Packets lost: %s', packets_lost)
            self._logger.debug("Iteration: %s, frame rate: %s, throughput_rx_fps: %s, frame_loss_percent: %s",
                               iteration, "{:.3f}".format(new_params['frame_rate']), stats['total']['rx_pps'],
                               "{:.3f}".format(test_lossrate))
            if test_lossrate == 0.0 and new_params['frame_rate'] == traffic['frame_rate']:
                return copy.deepcopy(stats)
            elif test_lossrate > lossrate:
                right = center
                center = (left + right) / 2
                new_params = copy.deepcopy(traffic)
                new_params['frame_rate'] = center
            else:
                stats_ok = copy.deepcopy(stats)
                left = center
                center = (left + right) / 2
                new_params = copy.deepcopy(traffic)
                new_params['frame_rate'] = center
            iteration += 1
        return stats_ok

    def send_cont_traffic(self, traffic=None, duration=30):
        """See ITrafficGenerator for description
        """
        self._logger.info("In Trex send_cont_traffic method")
        self._params.clear()

        self._show_packet_data = True

        self._params['traffic'] = self.traffic_defaults.copy()
        if traffic:
            self._params['traffic'] = merge_spec(
                self._params['traffic'], traffic)

        if settings.getValue('TRAFFICGEN_TREX_LEARNING_MODE'):
            self.learning_packets(traffic)
        self._logger.info("T-Rex sending traffic")
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

    def send_rfc2544_throughput(self, traffic=None, tests=1, duration=60,
                                lossrate=0.0):
        """See ITrafficGenerator for description
        """
        self._logger.info("In Trex send_rfc2544_throughput method")
        self._params.clear()
        self._show_packet_data = True
        self._params['traffic'] = self.traffic_defaults.copy()
        if traffic:
            self._params['traffic'] = merge_spec(
                self._params['traffic'], traffic)
        if settings.getValue('TRAFFICGEN_TREX_LEARNING_MODE'):
            self.learning_packets(traffic)
        self._verification_params = copy.deepcopy(traffic)
        traffic['frame_rate'] = settings.getValue('TRAFFICGEN_TREX_RFC2544_START_RATE')

        binary_bounds = {'right' : traffic['frame_rate'],
                         'left'  : 0,
                         'center': traffic['frame_rate'],}

        # Loops until the preconfigured differencde between frame rate
        # of successful and unsuccessful iterations is reached
        stats_ok = self.run_trials(boundaries=binary_bounds, duration=duration,
                                   lossrate=lossrate, traffic=traffic)
        if settings.getValue('TRAFFICGEN_TREX_VERIFICATION_MODE'):
            verification_iterations = 1
            while verification_iterations <= settings.getValue('TRAFFICGEN_TREX_MAXIMUM_VERIFICATION_TRIALS'):
                self._logger.info('Starting Trex Verification trial for %s seconds at frame rate %s',
                                  settings.getValue('TRAFFICGEN_TREX_VERIFICATION_DURATION'),
                                  self._verification_params['frame_rate'])
                stats = self.generate_traffic(self._verification_params,
                                              settings.getValue('TRAFFICGEN_TREX_VERIFICATION_DURATION'))
                verification_lossrate = ((stats["total"]["opackets"] - stats[
                    "total"]["ipackets"]) * 100) / stats["total"]["opackets"]
                if verification_lossrate <= lossrate:
                    self._logger.info('Trex Verification passed, %s packets were lost',
                                      stats["total"]["opackets"] - stats["total"]["ipackets"])
                    stats_ok = copy.deepcopy(stats)
                    break
                else:
                    self._logger.info('Trex Verification failed, %s packets were lost',
                                      stats["total"]["opackets"] - stats["total"]["ipackets"])
                    new_right = self._verification_params['frame_rate'] - settings.getValue(
                        'TRAFFICGEN_TREX_RFC2544_TPUT_THRESHOLD')
                    self._verification_params['frame_rate'] = new_right
                    binary_bounds = {'right': new_right,
                                     'left': 0,
                                     'center': new_right,}
                    stats_ok = self.run_trials(boundaries=binary_bounds, duration=duration,
                                               lossrate=lossrate, traffic=self._verification_params)
                verification_iterations += 1
            else:
                self._logger.error('Could not pass Trex Verification. Test failed')
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
