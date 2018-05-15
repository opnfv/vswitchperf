# Copyright 2015-2018 Intel Corporation., Tieto
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
"""Interface for deployment specific vSwitch controllers
"""
import logging

class IVswitchController(object):
    """Interface class for a vSwitch controller object

    This interface is used to setup and control a vSwitch provider for a
    particular deployment scenario.
    """
    def __init__(self, deployment, vswitch_class, traffic):
        """Initializes up the generic prerequisites for deployment scenario.

        :deployment: the deployment scenario to configure
        :vswitch_class: the vSwitch class to be used.
        :traffic: dictionary with detailed traffic definition
        """
        self._logger = logging.getLogger(__name__)
        self._vswitch_class = vswitch_class
        self._vswitch = vswitch_class()
        self._deployment_scenario = deployment
        self._logger.debug('Creation using %s', str(self._vswitch_class))
        self._traffic = traffic.copy()
        self._bridge = None

    def setup(self):
        """Sets up the switch for the particular deployment scenario
        """
        raise NotImplementedError(
            "The VswitchController does not implement the \"setup\" function.")

    def stop(self):
        """Tears down the switch created in setup()
        """
        raise NotImplementedError(
            "The VswitchController does not implement the \"stop\" function.")

    def __enter__(self):
        """Sets up the switch for the particular deployment scenario
        """
        self.setup()

    def __exit__(self, type_, value, traceback):
        """Tears down the switch created in setup()
        """
        self.stop()

    def get_vswitch(self):
        """Get the controlled vSwitch

        :return: The controlled IVswitch
        """
        return self._vswitch

    def get_ports_info(self):
        """Returns a dictionary describing all ports on the vSwitch.

        See IVswitch for dictionary structure details
        """
        raise NotImplementedError(
            "The VswitchController does not implement the \"get_ports_info\" "
            "function.")

    def dump_vswitch_connections(self):
        """ Dumps connections from vswitch
        """
        raise NotImplementedError(
            "The VswitchController does not implement the "
            "\"dump_vswitch_connections\" function.")
