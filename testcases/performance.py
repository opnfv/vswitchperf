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
"""PerformanceTestCase class
"""

import logging

from testcases import TestCase
from tools.report import report
from conf import settings as S

class PerformanceTestCase(TestCase):
    """PerformanceTestCase class

    In this basic form runs RFC2544 throughput test
    """
    def __init__(self, cfg, results_dir):
        """ Testcase initialization
        """
        self._type = 'performance'
        super(PerformanceTestCase, self).__init__(cfg, results_dir)
        self._logger = logging.getLogger(__name__)

    def run_report(self):
        super(PerformanceTestCase, self).run_report()
        if S.getValue('mode') != 'trafficgen-off':
            report.generate(self._output_file, self._tc_results, self._collector.get_results(), self._type)
