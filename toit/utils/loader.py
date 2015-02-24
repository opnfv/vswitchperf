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
Generic "loader" for Python modules.

Part of 'toit' - The OVS Integration Testsuite.
"""

import os
import sys
import imp
import fnmatch
import logging


def load_modules(path):
    """
    Load all modules from ``path`` directory.

    This is based on the design used by OFTest:
        https://github.com/floodlight/oftest/blob/master/oft

    :param path: Path to a folder of modules.

    :returns: List of modules in a folder.
    :rtype: [(modname, modref), ...]
    """
    mods = []

    for root, _, filenames in os.walk(path):
        # Iterate over each python file
        for filename in fnmatch.filter(filenames, '[!.]*.py'):
            modname = os.path.splitext(os.path.basename(filename))[0]

            try:
                if modname in sys.modules:
                    mod = sys.modules[modname]
                else:
                    mod = imp.load_module(
                        modname, *imp.find_module(modname, [root]))
            except ImportError:
                logging.error('Could not import file ' + filename)
                raise

            mods.append((modname, mod))

    return mods
