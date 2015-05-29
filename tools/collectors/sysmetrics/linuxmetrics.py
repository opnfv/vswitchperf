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

"""linux-metrics system statistics model.

Provides linux-metrics system statistics generic "helper" functions.

This requires the following setting in your config:

* SYSMETRICS_LINUX_METRICS_CPU_SAMPLES_INTERVAL
    Number of seconds in between samples to take for CPU percentages

If this doesn't exist, the application will raise an exception
(EAFP).
"""


import logging
import os
from conf import settings
from tools.collectors.collector import collector
from linux_metrics import cpu_stat, mem_stat

_ROOT_DIR = os.path.dirname(os.path.realpath(__file__))

class LinuxMetrics(collector.ICollector):
    """A logger based on the linux-metrics module.

    Currently it supports the logging of memory and CPU statistics
    """
    def __init__(self):
        self._logger = logging.getLogger(__name__)
        self._num_samples = settings.getValue(
            'SYSMETRICS_LINUX_METRICS_CPU_SAMPLES_INTERVAL')
        self._mem_stats = []
        self._cpu_stats = []

    def log_mem_stats(self):
        """See ICollector for descripion
        """
        self._mem_stats = mem_stat.mem_stats()
        # pylint: disable=unbalanced-tuple-unpacking
        mem_active, mem_total, mem_cached, mem_free, swap_total, swap_free = \
            self._mem_stats
        self._logger.info('%s mem_active: %s, mem_total: %s, mem_cached: %s, '
                          'mem_free: %s, swap_total: %s, swap_free: %s',
                          collector.CMD_PREFIX,
                          mem_active, mem_total, mem_cached, mem_free,
                          swap_total, swap_free)
        return self._mem_stats

    def log_cpu_stats(self):
        """See ICollector for descripion
        """
        self._cpu_stats = cpu_stat.cpu_percents(self._num_samples)
        self._logger.info('%s user: %.2f%%, nice: %.2f%%, system: %.2f%%, '
                          'idle: %.2f%%, iowait: %.2f%%, irq: %.2f%%, '
                          'softirq: %.2f%%',
                          collector.CMD_PREFIX,
                          self._cpu_stats['user'],
                          self._cpu_stats['nice'],
                          self._cpu_stats['system'],
                          self._cpu_stats['idle'],
                          self._cpu_stats['iowait'],
                          self._cpu_stats['irq'],
                          self._cpu_stats['softirq'])
        return self._cpu_stats

