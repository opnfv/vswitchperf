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
Collects container metrics from cAdvisor.
Sends metrics to influxDB and also stores results locally.
"""

import subprocess
import logging
import os
from collections import OrderedDict

from tools.collectors.collector import collector
from tools import tasks
from conf import settings



# inherit from collector.Icollector.
class Cadvisor(collector.ICollector):
    """A collector of container metrics based on cAdvisor

    It starts cadvisor and collects metrics.
    """

    def __init__(self, results_dir, test_name):
        """
        Initialize collection of statistics
        """
        self._logger = logging.getLogger(__name__)
        self.resultsdir = results_dir
        self.testname = test_name
        self._pid = 0
        self._results = OrderedDict()
        self._log = os.path.join(results_dir,
                                 settings.getValue('LOG_FILE_CADVISOR') +
                                 '_' + test_name + '.log')
        self._logfile = 0


    def start(self):
        """
        Starts collection of statistics by cAdvisor and stores them
        into-
        1. The file in directory with test results
        2. InfluxDB result container
        """

        # CMD options for cAdvisor
        cmd = ['sudo', '/opt/cadvisor/cadvisor',
               '-storage_driver='+settings.getValue('CADVISOR_STORAGE_DRIVER'),
               '-storage_driver_host='+settings.getValue('CADVISOR_STORAGE_HOST'),
               '-storage_driver_db='+settings.getValue('CADVISOR_DRIVER_DB'),
               '-housekeeping_interval=0.5s',
               '-storage_driver_buffer_duration=1s'
              ]

        self._logfile = open(self._log, 'a')

        self._pid = subprocess.Popen(map(os.path.expanduser, cmd), stdout=self._logfile, bufsize=0)
        self._logger.info('Starting cAdvisor')



    def stop(self):
        """
        Stops collection of metrics by cAdvisor and stores statistic
        summary for each monitored container into self._results dictionary
        """
        tasks.run_task(['sudo', 'pkill', '--signal', '2', 'cadvisor'],
                       self._logger, 'Stopping cAdvisor', True)

        self._logfile.close()
        self._logger.info('cAdvisor log available at %s', self._log)

        containers = settings.getValue('CADVISOR_CONTAINERS')
        self._results = cadvisor_log_result(self._log, containers)


    def get_results(self):
        """Returns collected statistics.
        """
        return self._results

    def print_results(self):
        """Logs collected statistics.
        """
        for cnt in self._results:
            logging.info("Container: %s", cnt)
            for (key, value) in self._results[cnt].items():

                postfix = ''

                if key == 'cpu_cumulative_usage':
                    key = 'CPU_usage'
                    value = round(float(value) / 1000000000, 4)
                    postfix = '%'

                if key in ['memory_usage', 'memory_working_set']:
                    value = round(float(value) / 1024 / 1024, 4)
                    postfix = 'MB'

                if key in ['rx_bytes', 'tx_bytes']:
                    value = round(float(value) / 1024 / 1024, 4)
                    postfix = 'mBps'

                logging.info("         Statistic: %s Value: %s %s",
                             str(key), str(value), postfix)


def cadvisor_log_result(filename, containers):
    """
    Processes cAdvisor logfile and returns average results

    :param filename: Name of cadvisor logfile
    :param containers: List of container names

    :returns: Result as average stats of Containers
    """
    result = OrderedDict()
    previous = OrderedDict()
    logfile = open(filename, 'r')
    with logfile:
        # for every line
        for _, line in enumerate(logfile):
            # skip lines having root '/' metrics
            if line[0:7] == 'cName=/':
                continue

            # parse line into OrderedDict
            tmp_res = parse_line(line)

            cnt = tmp_res['cName']

            # skip if cnt is not in container list
            if cnt not in containers:
                continue

            # add metrics to result
            if cnt not in result:
                result[cnt] = tmp_res
                previous[cnt] = tmp_res
                result[cnt]['count'] = 1
            else:
                for field in tmp_res:

                    if field in ['rx_errors', 'tx_errors', 'memory_usage', 'memory_working_set']:
                        val = float(tmp_res[field])
                    elif field in ['cpu_cumulative_usage', 'rx_bytes', 'tx_bytes']:
                        val = float(tmp_res[field]) - float(previous[cnt][field])
                    else:
                        # discard remaining fields
                        try:
                            result[cnt].pop(field)
                        except KeyError:
                            continue
                        continue

                    result[cnt][field] = float(result[cnt][field]) + val

                result[cnt]['count'] += 1
                previous[cnt] = tmp_res

    # calculate average results for containers
    result = calculate_average(result)
    return result


def calculate_average(results):
    """
    Calculates average for container stats
    """
    for cnt in results:
        for field in results[cnt]:
            if field != 'count':
                val = float(results[cnt][field])/results[cnt]['count']
                results[cnt][field] = '{0:.2f}'.format(val)

        results[cnt].pop('count')
        #sort results
        results[cnt] = OrderedDict(sorted(results[cnt].items()))

    return results


def parse_line(line):
    """
    Reads single line from cAdvisor logfile

    :param line: single line as str

    :returns: OrderedDict of line read
    """
    tmp_res = OrderedDict()
    # split line into array of "key=value" metrics
    metrics = line.split()
    for metric in metrics:
        key, value = metric.split('=')
        tmp_res[key] = value

    return tmp_res
