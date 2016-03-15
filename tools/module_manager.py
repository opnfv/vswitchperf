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
        module_base_name = os.path.basename(os.path.splitext(module)[0])

        if self.is_module_inserted(module):
            self._logger.info('Module already loaded \'%s\'.', module_base_name)
            # add it to internal list, so we can try to remove it at the end
            self._modules.append(module)
            return

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

            try:
                self._logger.info('Removing module \'%s\'...', module_base_name)
                subprocess.check_call('sudo rmmod {}'.format(module_base_name),
                                      shell=True, stderr=subprocess.DEVNULL)
                # in case that module was loaded automatically by modprobe
                # to solve dependecies, then it is not in internal list of modules
                if module in self._modules:
                    self._modules.remove(module)
            except subprocess.CalledProcessError:
                # in case of error, show full module name...
                self._logger.info('Unable to remove module \'%s\'.', module)
                # ...and list of dependend modules, if there are any
                module_details = self.get_module_details(module_base_name)
                if module_details:
                    mod_dep = module_details.split(' ')[3].rstrip(',')
                    if mod_dep[0] != '-':
                        self._logger.debug('Module \'%s\' is used by module(s) \'%s\'.',
                                           module_base_name, mod_dep)

    def remove_modules(self):
        """Removes all modules that have been previously inserted.
        """
        # remove modules in reverse order to respect their dependencies
        for module in reversed(self._modules):
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
            # underscores '_' and dashes '-' in module names are interchangeable, so we
            # have to normalize module names before comparision
            if line.split(' ')[0].replace('-', '_') == module.replace('-', '_'):
                return line

        return None
