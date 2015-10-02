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
"""Interface for deployment specific vSwitch controllers
"""

class IVswitchController(object):
    """Abstract class which defines a vSwitch controller object

    This interface is used to setup and control a vSwitch provider for a
    particular deployment scenario.
    """
    def __enter__(self):
        """Sets up the switch for the particular deployment scenario
        """
        raise NotImplementedError(
            "The VswitchController does not implement the \"setup\" function.")

    def __exit__(self, type_, value, traceback):
        """Tears down the switch created in setup()
        """
        raise NotImplementedError(
            "The VswitchController does not implement the \"stop\" function.")

    def get_vswitch(self):
        """Get the controlled vSwitch

        :return: The controlled IVswitch
        """
        raise NotImplementedError(
            "The VswitchController does not implement the \"get_vswitch\" "
            "function.")

    def get_ports_info(self):
        """Returns a dictionary describing all ports on the vSwitch.

        See IVswitch for dictionary structure details
        """
        raise NotImplementedError(
            "The VswitchController does not implement the \"get_ports_info\" "
            "function.")

    def dump_vswitch_flows(self):
        """ Dumps flows from vswitch
        """
        raise NotImplementedError(
            "The VswitchController does not implement the "
            "\"dump_vswitch_flows\" function.")
