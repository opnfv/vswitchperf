#!/usr/bin/env python3

# Copyright 2020 Spirent Communications.
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

"""VSPERF-Xtesting-Openstack Control script.
"""

import os
import subprocess
import sys
import time

from xtesting.core import testcase


class VsperfOstack(testcase.TestCase):
    """
    Implement Xtesting's testcase class
    """
    def run(self, **kwargs):
        """
        Main Run.
        """
        custom_conffile = '/vswitchperf/conf/99_xtesting.conf'
        try:
            test_params = {}
            for key in kwargs:
                test_params[key] = kwargs[key]
            # Make results directory - Xtesting Requirement
            os.makedirs(self.res_dir, exist_ok=True)
            # Start the timer
            self.start_time = time.time()

            # Get the parameter
            if 'conf_file' in test_params.keys():
                conffile = os.path.join('/', test_params['conf_file'])
            else:
                conffile = '/vsperfostack.conf'

            # Remove customfile if it exists.
            if os.path.exists(custom_conffile):
                os.remove(custom_conffile)

            # Write custom configuration.
            with open(custom_conffile, 'a+') as fil:
                fil.writelines("LOG_DIR='{}'".format(self.res_dir))
            fil.close()
            # Start the vsperf command
            if('deploy_tgen' in test_params.keys() and
               test_params['deploy_tgen']):
                output = subprocess.check_output(['vsperf',
                                                  '--conf-file',
                                                  conffile,
                                                  '--openstack',
                                                  '--load-env',
                                                  '--tests',
                                                  self.case_name])
            else:
                output = subprocess.check_output(['vsperf',
                                                  '--conf-file',
                                                  conffile,
                                                  '--load-env',
                                                  '--mode',
                                                  'trafficgen',
                                                  '--tests',
                                                  self.case_name])
            print(output)
            self.result = 100
            self.stop_time = time.time()
        except Exception:  # pylint: disable=broad-except
            print("Unexpected error:", sys.exc_info()[0])
            self.result = 0
            self.stop_time = time.time()
