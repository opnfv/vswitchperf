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

"""CollectorController class
"""
from core.results.results import IResults

class CollectorController(IResults):
    """Class which defines a collector controller object.

    Used to set-up and control a collector provider.
    """

    def __init__(self, collector_class):
        """Sets up the prerequisites for the Collector.

        :param collector_class: the Collector class to be used.
        """
        self._collector = collector_class()
        self._results = []

    def log_mem_stats(self):
        """Log memory stats.
        """
        self._results.append(self._collector.log_mem_stats())

    def log_cpu_stats(self):
        """Log CPU stats.
        """
        self._results.append(self._collector.log_cpu_stats())

    def get_results(self):
        """Return collected CPU and memory stats.

        Implements IResults i/f, see IResults for details.
        """
        return self._results

    def print_results(self):
        """Prints collected CPU and memory stats.

        Implements IResults i/f, see IResults for details.
        """
        print(self._results)
