# Copyright 2015-2017 Intel Corporation.
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
from core.traffic_controller_rfc2889 import TrafficControllerRFC2889
from core.vswitch_controller_clean import VswitchControllerClean
from core.vswitch_controller_p2p import VswitchControllerP2P
from core.vswitch_controller_pxp import VswitchControllerPXP
from core.vswitch_controller_op2p import VswitchControllerOP2P
from core.vswitch_controller_ptunp import VswitchControllerPtunP
from core.vnf_controller import VnfController
from core.pktfwd_controller import PktFwdController


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
    :return: A new TrafficController
    """
    if traffic_type.lower().startswith('rfc2889'):
        return TrafficControllerRFC2889(trafficgen_class)
    else:
        return TrafficControllerRFC2544(trafficgen_class)


def create_vswitch(deployment_scenario, vswitch_class, traffic,
                   tunnel_operation=None):
    """Return a new IVSwitchController for the deployment_scenario.

    The returned controller is configured with the given vSwitch class.

    Deployment scenarios: e.g. 'p2p', 'pvp', 'pvpv12', etc.

    :param deployment_scenario: The deployment scenario name
    :param vswitch_class: Reference to vSwitch class to be used.
    :param traffic: Dictionary with traffic specific details
    :param tunnel_operation encapsulation/decapsulation or None
    :return: IVSwitchController for the deployment_scenario
    """
    # pylint: disable=too-many-return-statements
    deployment_scenario = deployment_scenario.lower()
    if deployment_scenario.startswith("p2p"):
        return VswitchControllerP2P(vswitch_class, traffic)
    elif deployment_scenario.startswith("pvp"):
        return VswitchControllerPXP(deployment_scenario, vswitch_class, traffic)
    elif deployment_scenario.startswith("pvvp"):
        return VswitchControllerPXP(deployment_scenario, vswitch_class, traffic)
    elif deployment_scenario.startswith("pvpv"):
        return VswitchControllerPXP(deployment_scenario, vswitch_class, traffic)
    elif deployment_scenario.startswith("op2p"):
        return VswitchControllerOP2P(vswitch_class, traffic, tunnel_operation)
    elif deployment_scenario.startswith("ptunp"):
        return VswitchControllerPtunP(vswitch_class, traffic)
    elif deployment_scenario.startswith("clean"):
        return VswitchControllerClean(vswitch_class, traffic)
    else:
        raise RuntimeError("Unknown deployment scenario '{}'.".format(deployment_scenario))


def create_vnf(deployment_scenario, vnf_class, extra_vnfs):
    """Return a new VnfController for the deployment_scenario.

    The returned controller is configured with the given VNF class.

    Deployment scenarios: 'p2p', 'pvp'

    :param deployment_scenario: The deployment scenario name
    :param vswitch_class: Reference to vSwitch class to be used.
    :param extra_vnfs: The number of VNFs not involved in given
        deployment scenario. It will be used to correctly expand
        configuration values and initialize shared dirs. This parameter
        is used in case, that additional VNFs are executed by TestSteps.
    :return: VnfController for the deployment_scenario
    """
    return VnfController(deployment_scenario, vnf_class, extra_vnfs)

def create_collector(collector_class, result_dir, test_name):
    """Return a new Collector of the given class

    :param collector_class: The collector class to be used.
    :param result_dir: Directory with test results
    :param test_name: Test to be run
    :return: A new CollectorController.
    """
    return collector_class(result_dir, test_name)

def create_loadgen(loadgen_class, loadgen_cfg):
   """Return a new ILoadGenerator for the loadgen class.

   The returned load generator is of given loadgen generator class.

   :param loadgen_class: Name to load generator class to be used.
   :param loadgen_cfg: Configuration for the loadgen
   :return: A new ILoadGenerator class
   """
   # pylint: disable=too-many-function-args
   return loadgen_class(loadgen_cfg)

def create_pktfwd(deployment, pktfwd_class):
    """Return a new packet forwarder controller

    The returned controller is configured with the given
    packet forwarder class.

    :param pktfwd_class: Reference to packet forwarder class to be used.
    :param deployment: The deployment scenario name
    :return: packet forwarder controller
    """
    return PktFwdController(deployment, pktfwd_class)
