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

class KernelModuleInsertMode(object):
    """Module manager type of insert definition.
    """
    MODPROBE = 1
    INSMOD = 2 #NOT IMPLEMENTED

class ModuleManager(object):
    """Simple module manager which acts as system wrapper for Kernel Modules.
    """

    _logger = logging.getLogger(__name__)

    def __init__(self, insert_mode=KernelModuleInsertMode.MODPROBE):
        """Initializes data and sets insert mode.

        :param insert_mode: insert mode defines how modules are going to
                            be inserted in system.
        """
        self._modules = None
        self._insert_mode = insert_mode

    def insert_modules(self, modules):
        """Method inserts list of modules using defined insert mode.

        :param modules: list of modules to be inserted. Each element on
                        list should represent format which is expected
                        by KernelModuleInsertMode (e.g. for MODPROBE it
                        would be module name).

        :returns: None
        """
        self._modules = modules
        for module in modules:
            if ModuleManager.is_module_inserted(module):
                continue

            try:
                if self._insert_mode == KernelModuleInsertMode.MODPROBE:
                    tasks.run_task(['sudo', 'modprobe', module], self._logger,
                                   'Inserting module \'%s\'...' % module, True)
                else:
                    self._logger.error(
                        "Kernel module insert mode NOT IMPLEMENTED.")
                    raise

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
                tasks.run_task(['sudo', 'rmmod', module], self._logger,
                               'Removing module \'%s\'...' % module, True)
            except subprocess.CalledProcessError:
                self._logger.error('Unable to remove module \'%s\'.', module)
                continue

    @staticmethod
    def is_module_inserted(module):
        """Check if a module is inserted on system.
        """
        with open('/proc/modules') as mod_file:
            loaded_mods = mod_file.readlines()

        # first check if module is loaded
        for line in loaded_mods:
            if line.startswith(module):
                return True
        return False
