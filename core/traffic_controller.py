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

"""Interface to traffic controllers
"""

class ITrafficController(object):
    """Abstract class which defines a traffic controller object

    Used to setup and control a traffic generator for a particular deployment
    scenario.
    """

    def send_traffic(self, traffic):
        """Triggers traffic to be sent from the traffic generator.

        This is a blocking function.

        :param traffic: A dictionary describing the traffic to send.
        """
        raise NotImplementedError(
            "The TrafficController does not implement",
            "the \"send_traffic\" function.")

    def send_traffic_async(self, traffic, function):
        """Triggers traffic to be sent  asynchronously.

        This is not a blocking function.

        :param traffic: A dictionary describing the traffic to send.
        :param function: A dictionary describing the function to call between
             send and wait in the form:
             function = {
                 'function' : package.module.function,
                 'args' : args
             }
             If this function requires more than one argument, all should be
             should be passed using the args list and appropriately handled.
         """
        raise NotImplementedError(
            "The TrafficController does not implement",
            "the \"send_traffic_async\" function.")

    def stop_traffic(self):
        """Kills traffic being sent from the traffic generator.
        """
        raise NotImplementedError(
            "The TrafficController does not implement",
            "the \"stop_traffic\" function.")
