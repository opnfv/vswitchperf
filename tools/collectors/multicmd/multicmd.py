# Copyright 2019 Spirent Communications.
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
Collects information using various command line tools.
"""

#from tools.collectors.collector import collector
import glob
import logging
import os
from collections import OrderedDict
from tools import tasks
from tools.collectors.collector import collector
from conf import settings

class MultiCmd(collector.ICollector):
    """ Multiple command-line controllers
        collectd, prox, crond, filebeat
    """
    def __init__(self, results_dir, test_name):
        """
        initialize collectrs
        """
        self.prox_home = settings.getValue('MC_PROX_HOME')
        self.collectd_cmd = settings.getValue('MC_COLLECTD_CMD')
        self.collectd_csv = settings.getValue('MC_COLLECTD_CSV')
        self.prox_out = settings.getValue('MC_PROX_OUT')
        self.prox_cmd = settings.getValue('MC_PROX_CMD')
        self.cron_out = settings.getValue('MC_CRON_OUT')
        self.logger = logging.getLogger(__name__)
        self.results_dir = results_dir
        self.collectd_pid = 0
        self.prox_pid = 0
        self.cleanup_collectd_metrics()
        self.logger.debug('%s', 'Multicmd data for '+ str(test_name))
        # There should not be a file by name stop in prox_home folder
        filename = os.path.join(self.prox_home, 'stop')
        if os.path.exists(filename):
            tasks.run_task(['sudo', 'rm', filename],
                           self.logger, 'deleting stop')
        self.results = OrderedDict()

    def cleanup_collectd_metrics(self):
        """
        Cleaup the old or archived metrics
        """
        for name in glob.glob(os.path.join(self.collectd_csv, '*')):
            tasks.run_task(['sudo', 'rm', '-rf', name], self.logger,
                           'Cleaning up Metrics', True)

    def start(self):
        # Command-1: Start Collectd
        self.collectd_pid = tasks.run_background_task(
            ['sudo', self.collectd_cmd],
            self.logger, 'Staring Collectd')

        # Command-2: Start PROX
        working_dir = os.getcwd()
        if os.path.exists(self.prox_home):
            os.chdir(self.prox_home)
            self.prox_pid = tasks.run_background_task(['sudo', self.prox_cmd,
                                                       '--test', 'irq',
                                                       '--env', 'irq'],
                                                       self.logger,
                                                      'Start PROX')
        os.chdir(working_dir)
        # Command-3: Start CROND
        tasks.run_task(['sudo', 'systemctl', 'start', 'crond'],
                       self.logger, 'Staring CROND', True)

        # command-4: BEATS
        tasks.run_task(['sudo', 'systemctl', 'start', 'filebeat'],
                       self.logger, 'Starting BEATS', True)

    def stop(self):
        """
        Stop All commands
        """
        # Command-1: COLLECTD
        tasks.terminate_task_subtree(self.collectd_pid, logger=self.logger)
        tasks.run_task(['sudo', 'pkill', '--signal', '2', 'collectd'],
                       self.logger, 'Stopping Collectd', True)

        # Backup the collectd-metrics for this test into a results folder
        # results_dir = os.path.join(settings.getValue('RESULTS_PATH'), '/')
        tasks.run_task(['sudo', 'cp', '-r', self.collectd_csv,
                        self.results_dir], self.logger,
                       'Copying Collectd Results File', True)
        self.cleanup_metrics()

        # Command-2: PROX
        filename = os.path.join(self.prox_home, 'stop')
        if os.path.exists(self.prox_home):
            tasks.run_task(['sudo', 'touch', filename],
                           self.logger, 'Stopping PROX', True)

        outfile = os.path.join(self.prox_home, self.prox_out)
        if os.path.exists(outfile):
            tasks.run_task(['sudo', 'mv', outfile, self.results_dir],
                           self.logger, 'Moving PROX-OUT file', True)

        # Command-3: CROND
        tasks.run_task(['sudo', 'systemctl', 'stop', 'crond'],
                       self.logger, 'Stopping CROND', True)
        if os.path.exists(self.cron_out):
            tasks.run_task(['sudo', 'mv', self.cron_out, self.results_dir],
                           self.logger, 'Move Cron Logs', True)

        # Command-4: BEATS
        tasks.run_task(['sudo', 'systemctl', 'stop', 'filebeat'],
                       self.logger, 'Stopping BEATS', True)

    def get_results(self):
        """
        Return results
        """
        return self.results

    def print_results(self):
        """
        Print results
        """
