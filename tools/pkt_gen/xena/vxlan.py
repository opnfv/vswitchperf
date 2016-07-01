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
#   Li Ting, Red Hat Inc.

# RFC 7348 - Virtual eXtensible Local Area Network (VXLAN):
# A Framework for Overlaying Virtualized Layer 2 Networks over Layer 3 Networks

# scapy.contrib.description = VXLAN
# scapy.contrib.status = loads

from scapy.packet import Packet, bind_layers
from scapy.layers.l2 import Ether
from scapy.layers.inet import UDP
from scapy.fields import FlagsField, XByteField, BitField

_VXLAN_FLAGS = ['R' for i in range(0, 24)] + [
    'R', 'R', 'R', 'I', 'R', 'R', 'R', 'R', 'R']


class VXLAN(Packet):
    name = "VXLAN"
    fields_desc = [FlagsField("flags", 0x08000000, 32, _VXLAN_FLAGS),
                   BitField("vni", 0, 24),
                   XByteField("reserved", 0x00)]

    def mysummary(self):
        return self.sprintf("VXLAN (vni=%VXLAN.vni%)")

bind_layers(UDP, VXLAN, dport=4789)
bind_layers(VXLAN, Ether)
