# Copyright 2017 Spirent Communications.
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
Collects samples from collectd through collectd_bucky.
Depending on the policy - decides to keep the sample or discard.
Plot the values of the stored samples once the test is completed
"""

import copy
import csv
import multiprocessing
import os
from collections import OrderedDict
import queue as queue

import matplotlib.pyplot as plt
import numpy as np
import tools.collectors.collectd.collectd_bucky as cb
from tools.collectors.collector import collector
from conf import settings

# The y-lables. Keys in this dictionary are used a y-labels.
YLABELS = {'No/Of Packets': ['dropped', 'packets', 'if_octets', 'errors',
                             'if_rx_octets', 'if_tx_octets'],
           'Jiffies': ['cputime'],
           'Bandwidth b/s': ['memory_bandwidth'],
           'Bytes': ['bytes.llc']}


def get_label(sample):
    """
    Returns the y-label for the plot.
    """
    for label in YLABELS:
        if any(r in sample for r in YLABELS[label]):
            return label


def plot_graphs(dict_of_arrays):
    """
    Plot the values
    Store the data used for plotting.
    """
    i = 1
    results_dir = settings.getValue('RESULTS_PATH')
    for key in dict_of_arrays:
        tup_list = dict_of_arrays[key]
        two_lists = list(map(list, zip(*tup_list)))
        y_axis_list = two_lists[0]
        x_axis_list = two_lists[1]
        if np.count_nonzero(y_axis_list) > 0:
            with open(os.path.join(results_dir,
                                   str(key) + '.data'), "w") as pfile:
                writer = csv.writer(pfile, delimiter='\t')
                writer.writerows(zip(x_axis_list, y_axis_list))
            plt.figure(i)
            plt.plot(x_axis_list, y_axis_list)
            plt.xlabel("Time (Ticks)")
            plt.ylabel(get_label(key))
            plt.savefig(os.path.join(results_dir, str(key) + '.png'))
            plt.cla()
            plt.clf()
            plt.close()
            i = i + 1


def get_results_to_print(dict_of_arrays):
    """
    Return a results dictionary for report tool to
    print the process-statistics.
    """
    presults = OrderedDict()
    results = OrderedDict()
    for key in dict_of_arrays:
        if ('processes' in key and
                any(proc in key for proc in ['ovs', 'vpp', 'qemu'])):
            reskey = '.'.join(key.split('.')[2:])
            preskey = key.split('.')[1] + '_collectd'
            tup_list = dict_of_arrays[key]
            two_lists = list(map(list, zip(*tup_list)))
            y_axis_list = two_lists[0]
            mean = 0.0
            if np.count_nonzero(y_axis_list) > 0:
                mean = np.mean(y_axis_list)
            results[reskey] = mean
            presults[preskey] = results
    return presults


class Receiver(multiprocessing.Process):
    """
    Wrapper Receiver (of samples) class
    """
    def __init__(self, pd_dict, control):
        """
        Initialize.
        A queue will be shared with collectd_bucky
        """
        super(Receiver, self).__init__()
        self.daemon = False
        self.q_of_samples = multiprocessing.Queue()
        self.server = cb.get_collectd_server(self.q_of_samples)
        self.control = control
        self.pd_dict = pd_dict
        self.collectd_cpu_keys = settings.getValue('COLLECTD_CPU_KEYS')
        self.collectd_processes_keys = settings.getValue(
            'COLLECTD_PROCESSES_KEYS')
        self.collectd_iface_keys = settings.getValue(
            'COLLECTD_INTERFACE_KEYS')
        self.collectd_iface_xkeys = settings.getValue(
            'COLLECTD_INTERFACE_XKEYS')
        self.collectd_intelrdt_keys = settings.getValue(
            'COLLECTD_INTELRDT_KEYS')
        self.collectd_ovsstats_keys = settings.getValue(
            'COLLECTD_OVSSTAT_KEYS')
        self.collectd_dpdkstats_keys = settings.getValue(
            'COLLECTD_DPDKSTAT_KEYS')
        self.collectd_intelrdt_xkeys = settings.getValue(
            'COLLECTD_INTELRDT_XKEYS')
        self.exclude_coreids = []
        # Expand the ranges in the intelrdt-xkeys
        for xkey in self.collectd_intelrdt_xkeys:
            if '-' not in xkey:
                self.exclude_coreids.append(int(xkey))
            else:
                left, right = map(int, xkey.split('-'))
                self.exclude_coreids += range(left, right + 1)

    def run(self):
        """
        Start receiving the samples.
        """
        while not self.control.value:
            try:
                sample = self.q_of_samples.get(True, 1)
                if not sample:
                    break
                self.handle(sample)
            except queue.Empty:
                pass
            except IOError:
                continue
            except (ValueError, IndexError, KeyError, MemoryError):
                self.stop()
                break

    # pylint: disable=too-many-boolean-expressions
    def handle(self, sample):
        ''' Store values and names if names matches following:
            1. cpu + keys
            2. processes + keys
            3. interface + keys +  !xkeys
            4. ovs_stats + keys
            5. dpdkstat + keys
            6. intel_rdt + keys + !xkeys
            sample[1] is the name of the sample, which is . separated strings.
            The first field in sample[1] is the type - cpu, proceesses, etc.
            For intel_rdt, the second field contains the core-id, which is
            used to make the decision on 'exclusions'
            '''
        if (('cpu' in sample[1] and
             any(c in sample[1] for c in self.collectd_cpu_keys)) or
                ('processes' in sample[1] and
                 any(p in sample[1] for p in self.collectd_processes_keys)) or
                ('interface' in sample[1] and
                 (any(i in sample[1] for i in self.collectd_iface_keys) and
                  any(x not in sample[1]
                      for x in self.collectd_iface_xkeys))) or
                ('ovs_stats' in sample[1] and
                 any(o in sample[1] for o in self.collectd_ovsstats_keys)) or
                ('dpdkstat' in sample[1] and
                 any(d in sample[1] for d in self.collectd_dpdkstats_keys)) or
                ('intel_rdt' in sample[1] and
                 any(r in sample[1] for r in self.collectd_intelrdt_keys) and
                 (int(sample[1].split('.')[1]) not in self.exclude_coreids))):
            if sample[1] not in self.pd_dict:
                self.pd_dict[sample[1]] = list()
            val = self.pd_dict[sample[1]]
            val.append((sample[2], sample[3]))
            self.pd_dict[sample[1]] = val

    def stop(self):
        """
        Stop receiving the samples.
        """
        self.server.close()
        self.q_of_samples.put(None)
        self.control.value = True


# inherit from collector.Icollector.
class Collectd(collector.ICollector):
    """A collector of system statistics based on collectd

    It starts a UDP server, receives metrics from collectd
    and plot the results.
    """

    def __init__(self, results_dir, test_name):
        """
        Initialize collection of statistics
        """
        self._log = os.path.join(results_dir,
                                 settings.getValue('LOG_FILE_COLLECTD') +
                                 '_' + test_name + '.log')
        self.results = {}
        self.sample_dict = multiprocessing.Manager().dict()
        self.control = multiprocessing.Value('b', False)
        self.receiver = Receiver(self.sample_dict, self.control)

    def start(self):
        """
        Start receiving samples
        """
        self.receiver.server.start()
        self.receiver.start()

    def stop(self):
        """
        Stop receiving samples
        """
        self.control.value = True
        self.receiver.stop()
        self.receiver.server.join(5)
        self.receiver.join(5)
        if self.receiver.server.is_alive():
            self.receiver.server.terminate()
        if self.receiver.is_alive():
            self.receiver.terminate()
        self.results = copy.deepcopy(self.sample_dict)

    def get_results(self):
        """
        Return the results.
        """
        return get_results_to_print(self.results)

    def print_results(self):
        """
        Print - Plot and save raw-data.
        """
        plot_graphs(self.results)
