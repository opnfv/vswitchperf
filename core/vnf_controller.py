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
""" VNF Controller interface
"""

class IVnfController(object):
    """Abstract class which defines a VNF controller

    Used to set-up and control a VNF provider for a particular
    deployment scenario.
    """

    def get_vnfs(self):
        """Returns a list of vnfs controlled by this controller.
        """
        raise NotImplementedError(
            "The VnfController does not implement",
            "the \"get_vnfs\" function.")

    #TODO: Decide on contextmanager or __enter/exit__ strategy <MH 2015-05-01>
    def start(self):
        """Boots all VNFs set-up by __init__.

        This is a blocking function.
        """
        raise NotImplementedError(
            "The VnfController does not implement",
            "the \"start\" function.")

    def stop(self):
        """Stops all VNFs set-up by __init__.

        This is a blocking function.
        """
        raise NotImplementedError(
            "The VnfController does not implement",
            "the \"stop\" function.")
