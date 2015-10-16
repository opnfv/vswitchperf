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

"""Simple kernel module manager implementation.
"""

import subprocess
import logging
from tools import tasks

class ModuleManager(object):
    """Simple module manager which acts as system wrapper for Kernel Modules.
    """

    _logger = logging.getLogger(__name__)

    def __init__(self):
        """Initializes data
        """
        self._modules = None

    def insert_modules(self, modules):
        """Method inserts list of modules. In case that module name ends
        with .ko suffix then insmod will be used for its insertion. Otherwise
        modprobe will be called.

        :returns: None
        """
        self._modules = modules
        for module in modules:
            if ModuleManager.is_module_inserted(module):
                continue

            try:
                if module.endswith('.ko'):
                    tasks.run_task(['sudo', 'insmod', module], self._logger,
                                   'Insmod module \'%s\'...' % module, True)
                else:
                    tasks.run_task(['sudo', 'modprobe', module], self._logger,
                                   'Modprobe module \'%s\'...' % module, True)

            except subprocess.CalledProcessError:
                self._logger.error('Unable to insert module \'%s\'.', module)
                raise  # fail catastrophically

    def remove_modules(self):
        """Removes all modules that have been previously instereted.
        """
        for module in self._modules:
            # first check if module is loaded
            if not ModuleManager.is_module_inserted(module):
                continue

            try:
                # rmmod supports both simple module name and full module path
                # with .ko suffix
                tasks.run_task(['sudo', 'rmmod', module], self._logger,
                               'Removing module \'%s\'...' % module, True)
            except subprocess.CalledProcessError:
                self._logger.error('Unable to remove module \'%s\'.', module)
                continue

    @staticmethod
    def is_module_inserted(module):
        """Check if a module is inserted on system.
        """
        # get module base name, i.e strip path and .ko suffix if possible
        module_base_name = module.split('.')[0].split('/').pop()

        # get list of modules from kernel
        with open('/proc/modules') as mod_file:
            loaded_mods = mod_file.readlines()

        # first check if module is loaded
        for line in loaded_mods:
            if line.startswith(module_base_name):
                return True
        return False
