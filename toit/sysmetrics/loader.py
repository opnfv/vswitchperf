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
Handlers for 'SystemMetrics' plugins.

Part of 'toit' - The OVS Integration Testsuite.
"""

from toit.conf import settings
from toit.sysmetrics.sysmetrics import SystemMetrics
from toit.utils import loader


def load_sysmetrics(path=getattr(settings, 'SYSMETRICS_DIR')):
    """
    Load all system metric loggers from ``path`` directory.

    :param path: Path to a folder of system metric loggers

    :returns: List of test case functions
    """
    result = {}

    for _, mod in loader.load_modules(path):
        # find all system metric loggers defined in the module
        gens = dict((k, v) for (k, v) in mod.__dict__.items()
                    if type(v) == type and
                    issubclass(v, SystemMetrics))

        if gens:
            for (genname, gen) in gens.items():
                result[genname] = gen

    return result


def get_sysmetrics():
    """
    Get the currently used SystemMetrics.
    """
    return load_sysmetrics()[getattr(settings, 'SYSMETRICS')]()


def list_sysmetrics():
    """
    Get a list of all system metric loggers from ``sysmetrics`` folder.

    :returns: List of (name, description) of system metrics loggers found.
    :rtype: [(genname, gendesc), ...]
    """
    sysmetrics = load_sysmetrics()
    results = []

    for (name, mod) in sysmetrics.items():
        desc = (mod.__doc__ or 'No description').strip().split('\n')[0]
        results.append((name, desc))

    return results


def print_sysmetrics():
    """
    Get a string representation of loggers in the ``sysmetrics`` folder.
    """
    sysmetrics = list_sysmetrics()

    output = ['System Metrics Loggers:\n======\n']

    for (name, desc) in sysmetrics:
        output.append('* %-18s%s' % ('%s:' % name, desc))

        output.append('')

    output.append('')

    return '\n'.join(output)
