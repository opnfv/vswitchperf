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

#  Geneve Draft(GENEVE)
# http://tools.ietf.org/html/draft-gross-geneve-01

# scapy.contrib.description = GENEVE
# scapy.contrib.status = loads

"""
Scapy packet emulation for Xena encap/decap testing
"""

from scapy.packet import Packet, bind_layers
from scapy.layers.l2 import Ether
from scapy.layers.inet import UDP
from scapy.fields import XShortField, XByteField, BitField


class GENEVE(Packet):
    """
    Geneve packet class for scapy
    """
    name = "GENEVE"
    fields_desc = [BitField("version", 0, 2),
                   BitField("optionlen", 0, 6),
                   BitField("oam", 0, 1),
                   BitField("critical", 0, 1),
                   BitField("reserved", 0, 6),
                   XShortField("proto", 0x6558),
                   BitField("vni", 0, 24),
                   XByteField("reserved2", 0x00)]

    def mysummary(self):
        """
        Return scapy packet string
        :return: geneve packet string
        """
        return self.sprintf("GENEVE (vni=%GENEVE.vni%)")

bind_layers(UDP, GENEVE, dport=6081)
bind_layers(GENEVE, Ether)
