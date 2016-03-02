# Copyright 2015-2016 Intel Corporation.
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
import os
import subprocess
import logging

from tools import tasks

_LOGGER = logging.getLogger(__name__)
class ModuleManager(object):
    """Simple module manager which acts as system wrapper for Kernel Modules.
    """

    _logger = logging.getLogger(__name__)

    def __init__(self):
        """Initializes data
        """
        self._modules = []

    def insert_modules(self, modules):
        """Method inserts list of modules. In case that module name ends
        with .ko suffix then insmod will be used for its insertion. Otherwise
        modprobe will be called.

        :returns: None
        """

        for module in modules:
            if self.is_module_inserted(module):
                continue

            try:
                if module.endswith('.ko'):
                    tasks.run_task(['sudo', 'insmod', module], self._logger,
                                   'Insmod module \'%s\'...' % module, True)
                else:
                    tasks.run_task(['sudo', 'modprobe', module], self._logger,
                                   'Modprobe module \'%s\'...' % module, True)
                _LOGGER.info("Inserted Module %s", module)
                self._modules.append(module)
            except subprocess.CalledProcessError:
                self._logger.error('Unable to insert module \'%s\'.', module)
                raise  # fail catastrophically

    def insert_module_group(self, module_group, group_path_prefix):
        """Ensure all modules in a group are inserted into the system.

        :param module_group: A name of configuration item containing a list
        of module names
        """
        for module in module_group:
            # first check if module is loaded
            if self.is_module_inserted(module[1]):
                continue

            try:
                mod_path = os.path.join(group_path_prefix, module[0],
                                        '%s.ko' % module[1])
                tasks.run_task(['sudo', 'insmod', mod_path], _LOGGER,
                               'Inserting module \'%s\'...' % module[1], True)
                self._modules.append(module)
            except subprocess.CalledProcessError:
                _LOGGER.error('Unable to insert module \'%s\'.', module[1])
                raise  # fail catastrophically

    def remove_modules(self):
        """Removes all modules that have been previously inserted.
        """
        for module in self._modules:
            # first check if module is loaded
            if not self.is_module_inserted(module):
                continue

            try:
                # rmmod supports both simple module name and full module path
                # with .ko suffix
                tasks.run_task(['sudo', 'rmmod', module], self._logger,
                               'Removing module \'%s\'...' % module, True)
                self._modules.remove(module)
            except subprocess.CalledProcessError:
                self._logger.error('Unable to remove module \'%s\'.', module)
                continue

    def is_module_inserted(self, module):
        """Check if a module is inserted on system.
        """
        if module.endswith('.ko'):
        # get module base name, i.e strip path and .ko suffix if possible
            module_base_name = module.split('.')[0].split('/').pop()
        else:
            module_base_name = module

        # get list of modules from kernel
        with open('/proc/modules') as mod_file:
            loaded_mods = mod_file.readlines()

        # first check if module is loaded
        for line in loaded_mods:
            if line.startswith(module_base_name):
                return True
        return False

    def remove_module(self, module):
        """Removes a single module.
        """
        if self.is_module_inserted(module):
            # get module base name, i.e strip path and .ko suffix if possible
            module_base_name = module.split('.')[0].split('/').pop()

            try:
                # rmmod supports both simple module name and full module path
                # with .ko suffix
                tasks.run_task(['sudo', 'rmmod', module_base_name], self._logger,
                               'Removing module \'%s\'...' % module, True)
                self._modules.remove(module)
            except subprocess.CalledProcessError:
                self._logger.error('Unable to remove module \'%s\'.', module_base_name)

    def remove_module_group(self, module_group):
        """Removes all modules in the modules group.
        """
        for module in module_group:
            if not self.is_module_inserted(module[1]):
                continue
            # get module base name, i.e strip path and .ko suffix if possible
            module_base_name = module.split('.')[0].split('/').pop()

            try:
                # rmmod supports both simple module name and full module path
                # with .ko suffix
                tasks.run_task(['sudo', 'rmmod', module_base_name], self._logger,
                               'Removing module \'%s\'...' % module, True)
                self._modules.remove(module)
            except subprocess.CalledProcessError:
                self._logger.error('Unable to remove module \'%s\'.', module_base_name)
