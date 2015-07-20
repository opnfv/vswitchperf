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

"""Functions for creating controller objects based on deployment or traffic
"""

from core.traffic_controller_rfc2544 import TrafficControllerRFC2544
from core.vswitch_controller_p2p import VswitchControllerP2P
from core.vswitch_controller_pvp import VswitchControllerPVP
from core.vnf_controller_p2p import VnfControllerP2P
from core.vnf_controller_pvp import VnfControllerPVP
from core.collector_controller import CollectorController


def __init__():
    """Finds and loads all the modules required.

    Very similar code to load_trafficgens().
    """
    pass

def create_traffic(traffic_type, trafficgen_class):
    """Return a new IVSwitchController for the traffic type.

    The returned traffic controller has the given traffic type and traffic
    generator class.

    traffic_types: 'rfc2544_throughput'

    :param traffic_type: Name of traffic type
    :param trafficgen_class: Reference to traffic generator class to be used.
    :return: A new ITrafficController
    """
    return TrafficControllerRFC2544(trafficgen_class)


def create_vswitch(deployment_scenario, vswitch_class):
    """Return a new IVSwitchController for the deployment_scenario.

    The returned controller is configured with the given vSwitch class.

    Deployment scenarios: 'p2p', 'pvp'

    :param deployment_scenario: The deployment scenario name
    :param vswitch_class: Reference to vSwitch class to be used.
    :return: IVSwitchController for the deployment_scenario
    """
    #TODO - full mapping from all deployment_scenarios to
    #correct controller class
    deployment_scenario = deployment_scenario.lower()
    if deployment_scenario.find("p2p") >= 0:
        return VswitchControllerP2P(vswitch_class)
    elif deployment_scenario.find("pvp") >= 0:
        return VswitchControllerPVP(vswitch_class)

def create_vnf(deployment_scenario, vnf_class):
    """Return a new IVnfController for the deployment_scenario.

    The returned controller is configured with the given VNF class.

    Deployment scenarios: 'p2p', 'pvp'

    :param deployment_scenario: The deployment scenario name
    :param vswitch_class: Reference to vSwitch class to be used.
    :return: IVnfController for the deployment_scenario
    """
    #TODO - full mapping from all deployment_scenarios to
    #correct controller class
    deployment_scenario = deployment_scenario.lower()
    if deployment_scenario.find("p2p") >= 0:
        return VnfControllerP2P(vnf_class)
    elif deployment_scenario.find("pvp") >= 0:
        return VnfControllerPVP(vnf_class)

def create_collector(collector, collector_class):
    """Return a new CollectorController of the given class

    Supported collector type strings:
    'cpu'
    'memory':

    :param collector: Collector type string
    :param collector_class: The collector class to be used.
    :return: A new CollectorController.
    """
    collector = collector.lower()
    if "cpu" in collector or "memory" in collector:
        return CollectorController(collector_class)

