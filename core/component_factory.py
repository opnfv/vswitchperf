# Copyright 2015-2016 Intel Corporation.
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
from core.vswitch_controller_pvvp import VswitchControllerPVVP
from core.vswitch_controller_op2p import VswitchControllerOP2P
from core.vnf_controller import VnfController
from tools.load_gen.stress.stress import Stress
from tools.load_gen.stress_ng.stress_ng import StressNg
from tools.load_gen.dummy.dummy import DummyLoadGen


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


def create_vswitch(deployment_scenario, vswitch_class, traffic):
    """Return a new IVSwitchController for the deployment_scenario.

    The returned controller is configured with the given vSwitch class.

    Deployment scenarios: 'p2p', 'pvp'

    :param deployment_scenario: The deployment scenario name
    :param vswitch_class: Reference to vSwitch class to be used.
    :param traffic: Dictionary with traffic specific details
    :return: IVSwitchController for the deployment_scenario
    """
    deployment_scenario = deployment_scenario.lower()
    if deployment_scenario.find("p2p") == 0:
        return VswitchControllerP2P(vswitch_class, traffic)
    elif deployment_scenario.find("pvp") >= 0:
        return VswitchControllerPVP(vswitch_class, traffic)
    elif deployment_scenario.find("pvvp") >= 0:
        return VswitchControllerPVVP(vswitch_class, traffic)
    elif deployment_scenario.find("op2p") >= 0:
        return VswitchControllerOP2P(vswitch_class, traffic)

def create_vnf(deployment_scenario, vnf_class):
    """Return a new VnfController for the deployment_scenario.

    The returned controller is configured with the given VNF class.

    Deployment scenarios: 'p2p', 'pvp'

    :param deployment_scenario: The deployment scenario name
    :param vswitch_class: Reference to vSwitch class to be used.
    :return: VnfController for the deployment_scenario
    """
    return VnfController(deployment_scenario, vnf_class)

def create_collector(collector_class, result_dir, test_name):
    """Return a new Collector of the given class

    :param collector_class: The collector class to be used.
    :param result_dir: Directory with test results
    :param test_name: Test to be run
    :return: A new CollectorController.
    """
    return collector_class(result_dir, test_name)

def create_loadgen(loadgen_type, loadgen_cfg):
    """Return a new ILoadGenerator for the loadgen type.

    The returned load generator has the given loadgen type and loadgen
    generator class.

    :param loadgen_type: Name of loadgen type
    :param loadgen_class: Reference to load generator class to be used.
    :return: A new ILoadGenerator class
    """
    loadgen_type = loadgen_type.lower()
    if loadgen_type.find("dummy") >= 0:
        return DummyLoadGen(loadgen_cfg)
    elif loadgen_type.find("stress-ng") >= 0:
        return StressNg(loadgen_cfg)
    elif loadgen_type.find("stress") >= 0:
        return Stress(loadgen_cfg)


