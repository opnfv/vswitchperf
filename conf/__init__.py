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

"""Settings and configuration handlers.

Settings will be loaded from several .conf files
and any user provided settings file.
"""

# pylint: disable=invalid-name

import os
import re
import pprint

class Settings(object):
    """Holding class for settings.
    """
    def __init__(self):
        pass

    def getValue(self, attr):
        """Return a settings item value
        """
        if attr in self.__dict__:
            return getattr(self, attr)
        else:
            raise AttributeError("%r object has no attribute %r" %
                                 (self.__class__, attr))

    def __setattr__(self, name, value):
        """Set a value
        """
        # skip non-settings. this should exclude built-ins amongst others
        if not name.isupper():
            return

        # we can assume all uppercase keys are valid settings
        super(Settings, self).__setattr__(name, value)

    def setValue(self, name, value):
        """Set a value
        """
        if name is not None and value is not None:
            super(Settings, self).__setattr__(name, value)

    def load_from_file(self, path):
        """Update ``settings`` with values found in module at ``path``.
        """
        import imp

        custom_settings = imp.load_source('custom_settings', path)

        for key in dir(custom_settings):
            if getattr(custom_settings, key) is not None:
                setattr(self, key, getattr(custom_settings, key))

    def load_from_dir(self, dir_path):
        """Update ``settings`` with contents of the .conf files at ``path``.

        Each file must be named Nfilename.conf, where N is a single or
        multi-digit decimal number.  The files are loaded in ascending order of
        N - so if a configuration item exists in more that one file the setting
        in the file with the largest value of N takes precedence.

        :param dir_path: The full path to the dir from which to load the .conf
            files.

        :returns: None
        """
        regex = re.compile("^(?P<digit_part>[0-9]+).*.conf$")

        def get_prefix(filename):
            """
            Provide a suitable function for sort's key arg
            """
            match_object = regex.search(os.path.basename(filename))
            return int(match_object.group('digit_part'))

        # get full file path to all files & dirs in dir_path
        file_paths = os.listdir(dir_path)
        file_paths = [os.path.join(dir_path, x) for x in file_paths]

        # filter to get only those that are a files, with a leading
        # digit and end in '.conf'
        file_paths = [x for x in file_paths if os.path.isfile(x) and
                      regex.search(os.path.basename(x))]

        # sort ascending on the leading digits
        file_paths.sort(key=get_prefix)

        # load settings from each file in turn
        for filepath in file_paths:
            self.load_from_file(filepath)

    def load_from_dict(self, conf):
        """
        Update ``settings`` with values found in ``conf``.

        Unlike the other loaders, this is case insensitive.
        """
        for key in conf:
            if conf[key] is not None:
                setattr(self, key.upper(), conf[key])

    def load_from_env(self):
        """
        Update ``settings`` with values found in the environment.
        """
        for key in os.environ:
            setattr(self, key, os.environ[key])

    def __str__(self):
        """Provide settings as a human-readable string.

        This can be useful for debug.

        Returns:
            A human-readable string.
        """
        return pprint.pformat(self.__dict__)


settings = Settings()


def get_test_param(key, default=None):
    """Retrieve value for test param ``key`` if available.

    :param key: Key to retrieve from test params.
    :param default: Default to return if key not found.

    :returns: Value for ``key`` if found, else ``default``.
    """
    test_params = settings.getValue('TEST_PARAMS')
    return test_params.get(key, default) if test_params else default
