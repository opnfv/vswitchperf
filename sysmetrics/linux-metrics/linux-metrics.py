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
linux-metrics system statistics model.

Provides linux-metrics system statistics generic "helper" functions.

This requires the following setting in your config file:

* SYSMETRICS_LINUX_METRICS_CPU_SAMPLES_INTERVAL
    Number of seconds in between samples to take for CPU percentages

If this doesn't exist, the application will raise an exception
(EAFP).

Part of 'toit' - The OVS Integration Testsuite.
"""

import logging
import os
from toit.conf import settings
from toit.sysmetrics import sysmetrics
from linux_metrics import cpu_stat, mem_stat

_ROOT_DIR = os.path.dirname(os.path.realpath(__file__))


class LinuxMetrics(sysmetrics.SystemMetrics):
    """
    A logger based on the linux-metrics module.
    """
    _logger = logging.getLogger(__name__)
    _num_samples = getattr(settings, 'SYSMETRICS_LINUX_METRICS_CPU_SAMPLES_INTERVAL')

    def log_mem_stats(self):
        _mem_stats = mem_stat.mem_stats()
        mem_active, mem_total, mem_cached, mem_free, swap_total, swap_free = _mem_stats
        self._logger.info('%s mem_active: %s, mem_total: %s, mem_cached: %s, '
                          'mem_free: %s, swap_total: %s, swap_free: %s',
                          sysmetrics.CMD_PREFIX,
                          mem_active, mem_total, mem_cached, mem_free,
                          swap_total, swap_free)

    def log_cpu_stats(self):
        _cpu_stats = cpu_stat.cpu_percents(self._num_samples)
        self._logger.info('%s user: %.2f%%, nice: %.2f%%, system: %.2f%%, '
                          'idle: %.2f%%, iowait: %.2f%%, irq: %.2f%%, '
                          'softirq: %.2f%%',
                          sysmetrics.CMD_PREFIX,
                          _cpu_stats['user'],
                          _cpu_stats['nice'],
                          _cpu_stats['system'],
                          _cpu_stats['idle'],
                          _cpu_stats['iowait'],
                          _cpu_stats['irq'],
                          _cpu_stats['softirq'])

if __name__ == '__main__':
    # demonstrate stats gathering
    dev = LinuxMetrics()
    dev.logCpuStats()
    dev.logMemStats()
