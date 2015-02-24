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

"""
Abstract "system metrics logger" model.

This is an abstract class for system metrics loggers.

Part of 'toit' - The OVS Integration Testsuite.
"""

CMD_PREFIX = 'metricscmd : '


class SystemMetrics(object):

    """Model of a system metrics logger."""

    def log_mem_stats(self):
        """
        Log memory statistics.

        Where implemented, this function should raise an exception on
        failure.

        """
        raise NotImplementedError('Please call an implementation.')

    def log_cpu_stats(self):
        """
        Log cpu statistics.

        Where implemented, this function should raise an exception on
        failure.

        """
        raise NotImplementedError('Please call an implementation.')
