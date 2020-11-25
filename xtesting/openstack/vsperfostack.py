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
        try:
            test_params = {}
            for key in kwargs:
                test_params[key] = kwargs[key]
            os.makedirs(self.res_dir, exist_ok=True)
            os.environ["LOG_DIR"] = self.res_dir
            os.environ['OPNFVPOD'] = 'intel-pod12'
            os.environ['OPNFV_URL'] = 'http://127.0.0.1:8000/test/api/v1'
            self.start_time = time.time()
            if 'conf_file' in test_params.keys():
                conffile = os.path.join('/', test_params['conf_file'])
            else:
                conffile = '/vsperfostack.conf'
            output = subprocess.check_output(['vsperf',
                                              '--conf-file',
                                              conffile,
                                              '--openstack',
                                              '--load-env',
                                              '--tests',
                                              self.case_name])
            print(output)
            self.result = 100
            self.stop_time = time.time()
        except Exception:  # pylint: disable=broad-except
            print("Unexpected error:", sys.exc_info()[0])
            self.result = 0
            self.stop_time = time.time()
