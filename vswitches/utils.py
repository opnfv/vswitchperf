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

"""Utility functions for working with vSwitches and flows
"""

import copy

def add_ports_to_flow(flow, in_port, out_port):
    """Creates a new flow based on the given flow and adds in port and out port
    to it.

    The flow dictionary structure is described in IVswitch

    :param flow: Description of the flow as a dictionary
    :param in_port: OpenFlow number of the ingress port for the rule
    :param out_port: OpenFlow number of the eggress port for the rule

    :returns: A new dictionary describing a flow combining the parameters
    """
    new_flow = copy.deepcopy(flow)
    new_flow['in_port'] = in_port

    if 'actions' in new_flow:
        new_flow['actions'].append('output:' + str(out_port))
    else:
        new_flow['actions'] = ['output:' + str(out_port)]

    return new_flow
