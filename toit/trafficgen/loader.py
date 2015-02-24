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
Handlers for 'TrafficGenerator' plugins.

Part of 'toit' - The OVS Integration Testsuite.
"""

from toit.conf import settings
from toit.trafficgen.trafficgen import TrafficGenerator
from toit.utils import loader


def load_trafficgens(path=getattr(settings, 'TRAFFICGEN_DIR')):
    """
    Load all traffic generators from ``path`` directory.

    :param path: Path to a folder of trafficgens

    :returns: List of test case functions
    """
    result = {}

    for _, mod in loader.load_modules(path):
        # find all traffic generators defined in the module
        gens = dict((k, v) for (k, v) in mod.__dict__.items()
                    if type(v) == type and
                    issubclass(v, TrafficGenerator))

        if gens:
            for (genname, gen) in gens.items():
                result[genname] = gen

    return result


def get_trafficgen():
    """
    Get the currently used TrafficGenerator.
    """
    return load_trafficgens()[getattr(settings, 'TRAFFICGEN')]()


def list_trafficgens():
    """
    Get a list of all traffic generators from ``trafficgens`` folder.

    :returns: List of (name, description) of traffic generators found.
    :rtype: [(genname, gendesc), ...]
    """
    trafficgens = load_trafficgens()
    results = []

    for (name, mod) in trafficgens.items():
        desc = (mod.__doc__ or 'No description').strip().split('\n')[0]
        results.append((name, desc))

    return results


def print_trafficgens():
    """
    Get a string representation of gens in the ``trafficgens`` folder.
    """
    trafficgens = list_trafficgens()

    output = ['Traffic Generators:\n======\n']

    for (name, desc) in trafficgens:
        output.append('* %-18s%s' % ('%s:' % name, desc))

        output.append('')

    output.append('')

    return '\n'.join(output)
