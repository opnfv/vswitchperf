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

class ModuleManager(object):
    """Simple module manager which acts as system wrapper for Kernel Modules.
    """

    _logger = logging.getLogger(__name__)

    def __init__(self):
        """Initializes data
        """
        self._modules = []

    def insert_module(self, module):
        """Method inserts given module.

        In case that module name ends with .ko suffix then insmod will
        be used for its insertion. Otherwise modprobe will be called.

        :param module: a name of kernel module
        """
        if self.is_module_inserted(module):
            # add it to internal list, so we can remove it at the end
            self._modules.append(module)
            return

        module_base_name = os.path.basename(os.path.splitext(module)[0])

        try:
            if module.endswith('.ko'):
                tasks.run_task(['sudo', 'insmod', module], self._logger,
                               'Insmod module \'%s\'...' % module_base_name, True)
            else:
                tasks.run_task(['sudo', 'modprobe', module], self._logger,
                               'Modprobe module \'%s\'...' % module_base_name, True)
            self._modules.append(module)
        except subprocess.CalledProcessError:
            # in case of error, show full module name
            self._logger.error('Unable to insert module \'%s\'.', module)
            raise  # fail catastrophically

    def insert_modules(self, modules):
        """Method inserts list of modules.

        :param modules: a list of modules to be inserted
        """
        for module in modules:
            self.insert_module(module)

    def insert_module_group(self, module_group, path_prefix):
        """Ensure all modules in a group are inserted into the system.

        :param module_group: A name of configuration item containing a list
            of module names
        :param path_prefix: A name of directory which contains given
            group of modules
        """
        for (path_suffix, module) in module_group:
            self.insert_module(os.path.join(path_prefix, path_suffix, '%s.ko' % module))

    def remove_module(self, module):
        """Removes a single module.

        :param module: a name of kernel module
        """
        if self.is_module_inserted(module):
            # get module base name, i.e strip path and .ko suffix if possible
            module_base_name = os.path.basename(os.path.splitext(module)[0])

            # check and remove all dependecies of this module
            self.remove_module_dependencies(module_base_name)

            try:
                tasks.run_task(['sudo', 'rmmod', module_base_name], self._logger,
                               'Removing module \'%s\'...' % module_base_name, True)
                # in case that module was loaded automatically by modprobe
                # to solve dependecies, then it is not in internal list of modules
                if module in self._modules:
                    self._modules.remove(module)
            except subprocess.CalledProcessError:
                # in case of error, show full module name
                self._logger.error('Unable to remove module \'%s\'.', module)

    def remove_modules(self):
        """Removes all modules that have been previously inserted.
        """
        # remove modules in reverse order to respect their dependencies
        for module in reversed(self._modules):
            self.remove_module(module)

    def remove_module_dependencies(self, module):
        """Removes all modules, which are depended on given module

        :param module: a name of kernel module
        """
        module_details = self.get_module_details(module)
        if module_details:
            # get list of modules, which depend on us
            mod_dep = module_details.split(' ')[3].rstrip(',').split(',')
            if mod_dep[0] != '-':
                # remove all modules from dependency list
                for module in mod_dep:
                    self.remove_module(module)

    def is_module_inserted(self, module):
        """Check if a module is inserted on system.

        :param module: a name of kernel module
        """
        module_base_name = os.path.basename(os.path.splitext(module)[0])

        return self.get_module_details(module_base_name) != None

    @staticmethod
    def get_module_details(module):
        """Return details about given module

        :param module: a name of kernel module
        :returns: In case that module is loaded in OS, then corresponding
            line from /proc/modules will be returned. Otherwise it returns None.
        """
        # get list of modules from kernel
        with open('/proc/modules') as mod_file:
            loaded_mods = mod_file.readlines()

        # check if module is loaded
        for line in loaded_mods:
            # ensure that whole module name is used for comparison
            if line.startswith(module + ' '):
                return line

        return None
