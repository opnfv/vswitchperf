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

# Contributors:
#   Dan Amzulescu, Xena Networks
#   Christian Trautman, Red Hat Inc.
#
# Usage can be seen below in unit test. This implementation is designed for one
# module two port Xena chassis runs only.

"""
Xena JSON module
"""

import base64
from collections import OrderedDict
import json
import locale
import logging
import uuid

import scapy.layers.inet as inet

_LOGGER = logging.getLogger(__name__)
_LOCALE = locale.getlocale()[1]


class XenaJSON(object):
    """
    Class to modify and read Xena JSON configuration files.
    """
    def __init__(self, json_path='./profiles/baseconfig.x2544'):
        """
        Constructor
        :param json_path: path to JSON file to read. Expected files must have
         two module ports with each port having its own stream config profile.
        :return: XenaJSON object
        """
        self.json_data = read_json_file(json_path)

        self.packet_data = OrderedDict()
        self.packet_data['layer2'] = None
        self.packet_data['vlan'] = None
        self.packet_data['layer3'] = None
        self.packet_data['layer4'] = None

    def _add_multistream_layer(self, entity, seg_uuid, stop_value, layer):
        """
        Add the multi stream layers to the json file based on the layer provided
        :param entity: Entity to append the segment to in entity list
        :param seg_uuid: The UUID to attach the multistream layer to
        :param stop_value: The number of flows to configure
        :param layer: the layer that the multistream will be attached to
        :return: None
        """
        field_name = {
            2: ('Dst MAC addr', 'Src MAC addr'),
            3: ('Dest IP Addr', 'Src IP Addr'),
            4: ('Dest Port', 'Src Port')
        }
        segments = [
            {
                "Offset": 0,
                "Mask": "//8=",  # mask of 255/255
                "Action": "INC",
                "StartValue": 0,
                "StopValue": stop_value,
                "StepValue": 1,
                "RepeatCount": 1,
                "SegmentId": seg_uuid,
                "FieldName": field_name[int(layer)][0]
            },
            {
                "Offset": 0,
                "Mask": "//8=",  # mask of 255/255
                "Action": "INC",
                "StartValue": 0,
                "StopValue": stop_value,
                "StepValue": 1,
                "RepeatCount": 1,
                "SegmentId": seg_uuid,
                "FieldName": field_name[int(layer)][1]
            }
        ]

        self.json_data['StreamProfileHandler']['EntityList'][entity][
            'StreamConfig']['HwModifiers'].append(segments)

    def _create_packet_header(self):
        """
        Create the scapy packet header based on what has been built in this
        instance using the set header methods. Return tuple of the two byte
        arrays, one for each port.
        :return: Scapy packet headers as bytearrays
        """
        if not self.packet_data['layer2']:
            _LOGGER.warning('Using dummy info for layer 2 in Xena JSON file')
            self.set_header_layer2()
        packet1, packet2 = (self.packet_data['layer2'][0],
                            self.packet_data['layer2'][1])
        for packet_header in list(self.packet_data.copy().values())[1:]:
            if packet_header:
                packet1 /= packet_header[0]
                packet2 /= packet_header[1]
        ret = (bytes(packet1), bytes(packet2))
        return ret

    def add_header_segments(self, flows=0, multistream_layer=None):
        """
        Build the header segments to write to the JSON file.
        :param flows: Number of flows to configure for multistream if enabled
        :param multistream_layer: layer to set multistream flows as string.
        Acceptable values are L2, L3 or L4
        :return: None
        """
        packet = self._create_packet_header()
        segment1 = list()
        segment2 = list()
        header_pos = 0
        if self.packet_data['layer2']:
            # slice out the layer 2 bytes from the packet header byte array
            layer2 = packet[0][header_pos: len(self.packet_data['layer2'][0])]
            seg = create_segment(
                "ETHERNET", encode_byte_array(layer2).decode(_LOCALE))
            if multistream_layer == 'L2' and flows > 0:
                self._add_multistream_layer(entity=0, seg_uuid=seg['ItemID'],
                                            stop_value=flows, layer=2)
            segment1.append(seg)
            # now do the other port data with reversed src, dst info
            layer2 = packet[1][header_pos: len(self.packet_data['layer2'][1])]
            seg = create_segment(
                "ETHERNET", encode_byte_array(layer2).decode(_LOCALE))
            segment2.append(seg)
            if multistream_layer == 'L2' and flows > 0:
                self._add_multistream_layer(entity=1, seg_uuid=seg['ItemID'],
                                            stop_value=flows, layer=2)
            header_pos = len(layer2)
        if self.packet_data['vlan']:
            # slice out the vlan bytes from the packet header byte array
            vlan = packet[0][header_pos: len(
                self.packet_data['vlan'][0]) + header_pos]
            segment1.append(create_segment(
                "VLAN", encode_byte_array(vlan).decode(_LOCALE)))
            segment2.append(create_segment(
                "VLAN", encode_byte_array(vlan).decode(_LOCALE)))
            header_pos += len(vlan)
        if self.packet_data['layer3']:
            # slice out the layer 3 bytes from the packet header byte array
            layer3 = packet[0][header_pos: len(
                self.packet_data['layer3'][0]) + header_pos]
            seg = create_segment(
                "IP", encode_byte_array(layer3).decode(_LOCALE))
            segment1.append(seg)
            if multistream_layer == 'L3' and flows > 0:
                self._add_multistream_layer(entity=0, seg_uuid=seg['ItemID'],
                                            stop_value=flows, layer=3)
            # now do the other port data with reversed src, dst info
            layer3 = packet[1][header_pos: len(
                self.packet_data['layer3'][1]) + header_pos]
            seg = create_segment(
                "IP", encode_byte_array(layer3).decode(_LOCALE))
            segment2.append(seg)
            if multistream_layer == 'L3' and flows > 0:
                self._add_multistream_layer(entity=1, seg_uuid=seg['ItemID'],
                                            stop_value=flows, layer=3)
            header_pos += len(layer3)
        if self.packet_data['layer4']:
            # slice out the layer 4 bytes from the packet header byte array
            layer4 = packet[0][header_pos: len(
                self.packet_data['layer4'][0]) + header_pos]
            seg = create_segment(
                "UDP", encode_byte_array(layer4).decode(_LOCALE))
            segment1.append(seg)
            if multistream_layer == 'L4' and flows > 0:
                self._add_multistream_layer(entity=0, seg_uuid=seg['ItemID'],
                                            stop_value=flows, layer=4)
            # now do the other port data with reversed src, dst info
            layer4 = packet[1][header_pos: len(
                self.packet_data['layer4'][1]) + header_pos]
            seg = create_segment(
                "UDP", encode_byte_array(layer4).decode(_LOCALE))
            segment2.append(seg)
            if multistream_layer == 'L4' and flows > 0:
                self._add_multistream_layer(entity=1, seg_uuid=seg['ItemID'],
                                            stop_value=flows, layer=4)
            header_pos += len(layer4)

        self.json_data['StreamProfileHandler']['EntityList'][0][
            'StreamConfig']['HeaderSegments'] = segment1
        self.json_data['StreamProfileHandler']['EntityList'][1][
            'StreamConfig']['HeaderSegments'] = segment2

    def disable_back2back_test(self):
        """
        Disable the rfc2544 back to back test
        :return: None
        """
        self.json_data['TestOptions']['TestTypeOptionMap']['Back2Back'][
            'Enabled'] = 'false'

    def disable_throughput_test(self):
        """
        Disable the rfc2544 throughput test
        :return: None
        """
        self.json_data['TestOptions']['TestTypeOptionMap']['Throughput'][
            'Enabled'] = 'false'

    def enable_back2back_test(self):
        """
        Enable the rfc2544 back to back test
        :return: None
        """
        self.json_data['TestOptions']['TestTypeOptionMap']['Back2Back'][
            'Enabled'] = 'true'

    def enable_throughput_test(self):
        """
        Enable the rfc2544 throughput test
        :return: None
        """
        self.json_data['TestOptions']['TestTypeOptionMap']['Throughput'][
            'Enabled'] = 'true'

    def set_chassis_info(self, hostname, pwd):
        """
        Set the chassis info
        :param hostname: hostname as string of ip
        :param pwd: password to chassis as string
        :return: None
        """
        self.json_data['ChassisManager']['ChassisList'][0][
            'HostName'] = hostname
        self.json_data['ChassisManager']['ChassisList'][0][
            'Password'] = pwd

    def set_header_layer2(self, dst_mac='cc:cc:cc:cc:cc:cc',
                          src_mac='bb:bb:bb:bb:bb:bb', **kwargs):
        """
        Build a scapy Ethernet L2 objects inside instance packet_data structure
        :param dst_mac: destination mac as string. Example "aa:aa:aa:aa:aa:aa"
        :param src_mac: source mac as string. Example "bb:bb:bb:bb:bb:bb"
        :param kwargs: Extra params per scapy usage.
        :return: None
        """
        self.packet_data['layer2'] = [
            inet.Ether(dst=dst_mac, src=src_mac, **kwargs),
            inet.Ether(dst=src_mac, src=dst_mac, **kwargs)]

    def set_header_layer3(self, src_ip='192.168.0.2', dst_ip='192.168.0.3',
                          protocol='UDP', **kwargs):
        """
        Build scapy IPV4 L3 objects inside instance packet_data structure
        :param src_ip: source IP as string in dot notation format
        :param dst_ip: destination IP as string in dot notation format
        :param protocol: protocol for l4
        :param kwargs: Extra params per scapy usage
        :return: None
        """
        self.packet_data['layer3'] = [
            inet.IP(src=src_ip, dst=dst_ip, proto=protocol.lower(), **kwargs),
            inet.IP(src=dst_ip, dst=src_ip, proto=protocol.lower(), **kwargs)]

    def set_header_layer4_udp(self, source_port, destination_port, **kwargs):
        """
        Build scapy UDP L4 objects inside instance packet_data structure
        :param source_port: Source port as int
        :param destination_port: Destination port as int
        :param kwargs: Extra params per scapy usage
        :return: None
        """
        self.packet_data['layer4'] = [
            inet.UDP(sport=source_port, dport=destination_port, **kwargs),
            inet.UDP(sport=source_port, dport=destination_port, **kwargs)]

    def set_header_vlan(self, vlan_id=1, **kwargs):
        """
        Build a Dot1Q scapy object inside instance packet_data structure
        :param vlan_id: The VLAN ID
        :param kwargs: Extra params per scapy usage
        :return: None
        """
        self.packet_data['vlan'] = [
            inet.Dot1Q(vlan=vlan_id, **kwargs),
            inet.Dot1Q(vlan=vlan_id, **kwargs)]

    def set_port(self, index, module, port):
        """
        Set the module and port for the 0 index port to use with the test
        :param index: Index of port to set, 0 = port1, 1=port2, etc..
        :param module: module location as int
        :param port: port location in module as int
        :return: None
        """
        self.json_data['PortHandler']['EntityList'][index]['PortRef'][
            'ModuleIndex'] = module
        self.json_data['PortHandler']['EntityList'][index]['PortRef'][
            'PortIndex'] = port

    def set_port_ip_v4(self, port, ip_addr, netmask, gateway):
        """
        Set the port IP info
        :param port: port number as int of port to set ip info
        :param ip_addr: ip address in dot notation format as string
        :param netmask: cidr number for netmask (ie 24/16/8) as int
        :param gateway: gateway address in dot notation format
        :return: None
        """
        available_ports = range(len(
            self.json_data['PortHandler']['EntityList']))
        if port not in available_ports:
            raise ValueError("{}{}{}".format(
                'Port assignment must be an available port ',
                'number in baseconfig file. Port=', port))
        self.json_data['PortHandler']['EntityList'][
            port]["IpV4Address"] = ip_addr
        self.json_data['PortHandler']['EntityList'][
            port]["IpV4Gateway"] = gateway
        self.json_data['PortHandler']['EntityList'][
            port]["IpV4RoutingPrefix"] = int(netmask)

    def set_port_ip_v6(self, port, ip_addr, netmask, gateway):
        """
        Set the port IP info
        :param port: port number as int of port to set ip info
        :param ip_addr: ip address as 8 groups of 4 hexadecimal groups separated
         by a colon.
        :param netmask: cidr number for netmask (ie 24/16/8) as int
        :param gateway: gateway address as string in 8 group of 4 hexadecimal
                        groups separated by a colon.
        :return: None
        """
        available_ports = range(len(
            self.json_data['PortHandler']['EntityList']))
        if port not in available_ports:
            raise ValueError("{}{}{}".format(
                'Port assignment must be an available port ',
                'number in baseconfig file. Port=', port))
        self.json_data['PortHandler']['EntityList'][
            port]["IpV6Address"] = ip_addr
        self.json_data['PortHandler']['EntityList'][
            port]["IpV6Gateway"] = gateway
        self.json_data['PortHandler']['EntityList'][
            port]["IpV6RoutingPrefix"] = int(netmask)

    def set_test_options(self, packet_sizes, duration, iterations, loss_rate,
                         micro_tpld=False):
        """
        Set the test options
        :param packet_sizes: List of packet sizes to test, single int entry is
         acceptable for one packet size testing
        :param duration: time for each test in seconds as int
        :param iterations: number of iterations of testing as int
        :param loss_rate: acceptable loss rate as float
        :param micro_tpld: boolean if micro_tpld should be enabled or disabled
        :return: None
        """
        if isinstance(packet_sizes, int):
            packet_sizes = [packet_sizes]
        self.json_data['TestOptions']['PacketSizes'][
            'CustomPacketSizes'] = packet_sizes
        self.json_data['TestOptions']['TestTypeOptionMap']['Throughput'][
            'Duration'] = duration
        self.json_data['TestOptions']['TestTypeOptionMap']['Throughput'][
            'RateIterationOptions']['AcceptableLoss'] = loss_rate
        self.json_data['TestOptions']['FlowCreationOptions'][
            'UseMicroTpldOnDemand'] = 'true' if micro_tpld else 'false'
        self.json_data['TestOptions']['TestTypeOptionMap']['Throughput'][
            'Iterations'] = iterations

    def set_topology_blocks(self):
        """
        Set the test topology to a West to East config for half duplex flow with
        port 0 as the sender and port 1 as the receiver.
        :return: None
        """
        self.json_data['TestOptions']['TopologyConfig']['Topology'] = 'BLOCKS'
        self.json_data['TestOptions']['TopologyConfig'][
            'Direction'] = 'WEST_EAST'
        self.json_data['PortHandler']['EntityList'][0][
            'PortGroup'] = "WEST"
        self.json_data['PortHandler']['EntityList'][1][
            'PortGroup'] = "EAST"

    def set_topology_mesh(self):
        """
        Set the test topology to Mesh for bi directional full duplex flow
        :return: None
        """
        self.json_data['TestOptions']['TopologyConfig']['Topology'] = 'MESH'
        self.json_data['TestOptions']['TopologyConfig']['Direction'] = 'BIDIR'
        self.json_data['PortHandler']['EntityList'][0][
            'PortGroup'] = "UNDEFINED"
        self.json_data['PortHandler']['EntityList'][1][
            'PortGroup'] = "UNDEFINED"

    def write_config(self, path='./2bUsed.x2544'):
        """
        Write the config to out as file
        :param path: Output file to export the json data to
        :return: None
        """
        if not write_json_file(self.json_data, path):
            raise RuntimeError("Could not write out file, please check config")


def create_segment(header_type, encode_64_string):
    """
    Create segment for JSON file
    :param header_type: Type of header as string
    :param encode_64_string: 64 byte encoded string value of the hex bytes
    :return: segment as dictionary
    """
    return {
        "SegmentType": header_type.upper(),
        "SegmentValue": encode_64_string,
        "ItemID": str(uuid.uuid4()),
        "ParentID": "",
        "Label": ""}


def decode_byte_array(enc_str):
    """ Decodes the base64-encoded string to a byte array
    :param enc_str: The base64-encoded string representing a byte array
    :return: The decoded byte array
    """
    dec_string = base64.b64decode(enc_str)
    barray = bytearray()
    barray.extend(dec_string)
    return barray


def encode_byte_array(byte_arr):
    """ Encodes the byte array as a base64-encoded string
    :param byte_arr: A bytearray containing the bytes to convert
    :return: A base64 encoded string
    """
    enc_string = base64.b64encode(bytes(byte_arr))
    return enc_string


def print_json_report(json_data):
    """
    Print out info from the json data for testing purposes only.
    :param json_data: json loaded data from json.loads
    :return: None
    """
    print("<<Xena JSON Config Report>>\n")
    try:
        print("### Chassis Info ###")
        print("Chassis IP: {}".format(json_data['ChassisManager'][
            'ChassisList'][0]['HostName']))
        print("Chassis Password: {}".format(json_data['ChassisManager'][
            'ChassisList'][0]['Password']))
        print("### Port Configuration ###")
        print("Port 1 IPv4:{}/{} gateway:{}".format(
            json_data['PortHandler']['EntityList'][0]["IpV4Address"],
            json_data['PortHandler']['EntityList'][0]["IpV4RoutingPrefix"],
            json_data['PortHandler']['EntityList'][0]["IpV4Gateway"]))
        print("Port 1 IPv6:{}/{} gateway:{}".format(
            json_data['PortHandler']['EntityList'][0]["IpV6Address"],
            json_data['PortHandler']['EntityList'][0]["IpV6RoutingPrefix"],
            json_data['PortHandler']['EntityList'][0]["IpV6Gateway"]))
        print("Port 2 IPv4:{}/{} gateway:{}".format(
            json_data['PortHandler']['EntityList'][1]["IpV4Address"],
            json_data['PortHandler']['EntityList'][1]["IpV4RoutingPrefix"],
            json_data['PortHandler']['EntityList'][1]["IpV4Gateway"]))
        print("Port 2 IPv6:{}/{} gateway:{}".format(
            json_data['PortHandler']['EntityList'][1]["IpV6Address"],
            json_data['PortHandler']['EntityList'][1]["IpV6RoutingPrefix"],
            json_data['PortHandler']['EntityList'][1]["IpV6Gateway"]))
        print("Port 1: {}/{} group: {}".format(
            json_data['PortHandler']['EntityList'][0]['PortRef']['ModuleIndex'],
            json_data['PortHandler']['EntityList'][0]['PortRef']['PortIndex'],
            json_data['PortHandler']['EntityList'][0]['PortGroup']))
        print("Port 2: {}/{} group: {}".format(
            json_data['PortHandler']['EntityList'][1]['PortRef']['ModuleIndex'],
            json_data['PortHandler']['EntityList'][1]['PortRef']['PortIndex'],
            json_data['PortHandler']['EntityList'][1]['PortGroup']))
        print("### Tests Enabled ###")
        print("Back2Back Enabled: {}".format(json_data['TestOptions'][
            'TestTypeOptionMap']['Back2Back']['Enabled']))
        print("Throughput Enabled: {}".format(json_data['TestOptions'][
            'TestTypeOptionMap']['Throughput']['Enabled']))
        print("### Test Options ###")
        print("Test topology: {}/{}".format(
            json_data['TestOptions']['TopologyConfig']['Topology'],
            json_data['TestOptions']['TopologyConfig']['Direction']))
        print("Packet Sizes: {}".format(json_data['TestOptions'][
            'PacketSizes']['CustomPacketSizes']))
        print("Test duration: {}".format(json_data['TestOptions'][
            'TestTypeOptionMap']['Throughput']['Duration']))
        print("Acceptable loss rate: {}".format(json_data['TestOptions'][
            'TestTypeOptionMap']['Throughput']['RateIterationOptions'][
                'AcceptableLoss']))
        print("Micro TPLD enabled: {}".format(json_data['TestOptions'][
            'FlowCreationOptions']['UseMicroTpldOnDemand']))
        print("Test iterations: {}".format(json_data['TestOptions'][
            'TestTypeOptionMap']['Throughput']['Iterations']))
        if 'StreamConfig' in json_data['StreamProfileHandler']['EntityList'][0]:
            print("### Header segments ###")
            for seg in json_data['StreamProfileHandler']['EntityList']:
                for header in seg['StreamConfig']['HeaderSegments']:
                    print("Type: {}".format(
                        header['SegmentType']))
                    print("Value: {}".format(decode_byte_array(
                        header['SegmentValue'])))
            print("### Multi Stream config ###")
            for seg in json_data['StreamProfileHandler']['EntityList']:
                for header in seg['StreamConfig']['HwModifiers']:
                    print(header)
    except KeyError as exc:
        print("Error setting not found in JSON data: {}".format(exc))


def read_json_file(json_file):
    """
    Read the json file path and return a dictionary of the data
    :param json_file: path to json file
    :return: dictionary of json data
    """
    try:
        with open(json_file, 'r', encoding=_LOCALE) as data_file:
            file_data = json.loads(data_file.read())
    except ValueError as exc:
        # general json exception, Python 3.5 adds new exception type
        _LOGGER.exception("Exception with json read: %s", exc)
        raise
    except IOError as exc:
        _LOGGER.exception(
            'Exception during file open: %s file=%s', exc, json_file)
        raise
    return file_data


def write_json_file(json_data, output_path):
    """
    Write out the dictionary of data to a json file
    :param json_data: dictionary of json data
    :param output_path: file path to write output
    :return: Boolean if success
    """
    try:
        with open(output_path, 'w', encoding=_LOCALE) as fileh:
            json.dump(json_data, fileh, indent=2, sort_keys=True,
                      ensure_ascii=True)
        return True
    except ValueError as exc:
        # general json exception, Python 3.5 adds new exception type
        _LOGGER.exception(
            "Exception with json write: %s", exc)
        return False
    except IOError as exc:
        _LOGGER.exception(
            'Exception during file write: %s file=%s', exc, output_path)
        return False


if __name__ == "__main__":
    print("Running UnitTest for XenaJSON")
    JSON = XenaJSON()
    print_json_report(JSON.json_data)
    JSON.set_chassis_info('192.168.0.5', 'vsperf')
    JSON.set_port(0, 1, 0)
    JSON.set_port(1, 1, 1)
    JSON.set_port_ip_v4(0, '192.168.240.10', 32, '192.168.240.1')
    JSON.set_port_ip_v4(1, '192.168.240.11', 32, '192.168.240.1')
    JSON.set_port_ip_v6(0, 'a1a1:a2a2:a3a3:a4a4:a5a5:a6a6:a7a7:a8a8', 128,
                        'a1a1:a2a2:a3a3:a4a4:a5a5:a6a6:a7a7:1111')
    JSON.set_port_ip_v6(1, 'b1b1:b2b2:b3b3:b4b4:b5b5:b6b6:b7b7:b8b8', 128,
                        'b1b1:b2b2:b3b3:b4b4:b5b5:b6b6:b7b7:1111')
    JSON.set_header_layer2(dst_mac='dd:dd:dd:dd:dd:dd',
                           src_mac='ee:ee:ee:ee:ee:ee')
    JSON.set_header_vlan(vlan_id=5)
    JSON.set_header_layer3(src_ip='192.168.100.2', dst_ip='192.168.100.3',
                           protocol='udp')
    JSON.set_header_layer4_udp(source_port=3000, destination_port=3001)
    JSON.set_test_options(packet_sizes=[64], duration=10, iterations=1,
                          loss_rate=0.0, micro_tpld=True)
    JSON.add_header_segments(flows=4000, multistream_layer='L4')
    JSON.set_topology_blocks()
    write_json_file(JSON.json_data, './testthis.x2544')
    JSON = XenaJSON('./testthis.x2544')
    print_json_report(JSON.json_data)

