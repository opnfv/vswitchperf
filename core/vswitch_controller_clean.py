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

"""VSwitch controller for basic initialization of vswitch
"""
from core.vswitch_controller import IVswitchController

class VswitchControllerClean(IVswitchController):
    """VSwitch controller for Clean deployment scenario.

    Attributes:
        _vswitch_class: The vSwitch class to be used.
        _vswitch: The vSwitch object controlled by this controller
        _deployment_scenario: A string describing the scenario to set-up in the
            constructor.
    """
    def setup(self):
        """Sets up the switch for Clean.
        """
        self._logger.debug('Setup using %s', str(self._vswitch_class))

        try:
            self._vswitch.start()
        except:
            self._vswitch.stop()
            raise

    def stop(self):
        """Tears down the switch created in setup().
        """
        self._logger.debug('Stop using %s', str(self._vswitch_class))
        self._vswitch.stop()

    def get_ports_info(self):
        """See IVswitchController for description
        """
        pass

    def dump_vswitch_connections(self):
        """See IVswitchController for description
        """
        pass
