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
"""IntegrationTestCase class
"""

import os
import time
import logging
import copy
import re

from collections import OrderedDict
from testcases import TestCase
from conf import settings as S
from tools import namespace
from tools import veth
from tools.teststepstools import TestStepsTools
from core.loader import Loader

class IntegrationTestCase(TestCase):
    """IntegrationTestCase class
    """

    def __init__(self, cfg):
        """ Testcase initialization
        """
        self._type = 'integration'
        super(IntegrationTestCase, self).__init__(cfg)
        self._logger = logging.getLogger(__name__)
        # enforce check of step result for step driven testcases
        self._step_check = True

    def run_report(self):
        """ Report test results
        """
        if self.test:
            results = OrderedDict()
            results['status'] = 'OK' if self._step_status['status'] else 'FAILED'
            results['details'] = self._step_status['details']
            TestCase.write_result_to_file([results], self._output_file)
            self.step_report_status("Test '{}'".format(self.name), self._step_status['status'])
            # inform vsperf about testcase failure
            if not self._step_status['status']:
                raise Exception
        else:
            super(IntegrationTestCase, self).run_report()
