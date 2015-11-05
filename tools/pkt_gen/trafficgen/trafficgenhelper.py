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
"""Helper methods collection.

Collection of helper methods used by traffic generators
implementation.
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
        'proto': 'udp',
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

#TODO remove namedtuples and implement results through IResult interface found
#in core/results

BurstResult = namedtuple(
    'BurstResult',
    'frames_tx frames_rx bytes_tx bytes_rx payload_err seq_err')
Back2BackResult = namedtuple(
    'Back2BackResult',
    'rx_fps rx_mbps tx_percent rx_percent tx_count b2b_frames '
    'frame_loss_frames frame_loss_percent')


def merge_spec(orig, new):
    """Merges ``new`` dict with ``orig`` dict, and return orig.

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

        # Not allowing derived dictionary types for now
        # pylint: disable=unidiomatic-typecheck
        if type(orig[key]) == dict:
            orig[key] = merge_spec(orig[key], new[key])
        else:
            orig[key] = new[key]

    for key in new:
        if key not in orig:
            orig[key] = new[key]

    return orig

