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

from testcases import TestCase
from conf import settings as S
from collections import OrderedDict

CHECK_PREFIX = 'validate_'

class IntegrationTestCase(TestCase):
    """IntegrationTestCase class
    """

    def __init__(self, cfg, results_dir):
        """ Testcase initialization
        """
        self._type = 'integration'
        super(IntegrationTestCase, self).__init__(cfg, results_dir)
        self._logger = logging.getLogger(__name__)
        self._inttest = None

    def report_status(self, label, status):
        """ Log status of test step
        """
        self._logger.debug("%s ... %s", label, 'OK' if status else 'FAILED')

    def run_initialize(self):
        """ Prepare test execution environment
        """
        super(IntegrationTestCase, self).run_initialize()
        self._inttest = {'status' : True, 'details' : ''}

    def run(self):
        """Run the test

        All setup and teardown through controllers is included.
        """
        def eval_step_params(params, step_result):
            """ Evaluates referrences to results from previous steps
            """
            def eval_param(param, STEP):
                """ Helper function
                """
                if isinstance(param, str):
                    tmp_param = ''
                    # evaluate every #STEP reference inside parameter itself
                    for chunk in param.split('#'):
                        if chunk.startswith('STEP['):
                            tmp_param = tmp_param + str(eval(chunk))
                        else:
                            tmp_param = tmp_param + chunk
                    return tmp_param
                elif isinstance(param, list) or isinstance(param, tuple):
                    tmp_list = []
                    for item in param:
                        tmp_list.append(eval_param(item, STEP))
                    return tmp_list
                elif isinstance(param, dict):
                    tmp_dict = {}
                    for (key, value) in param.items():
                        tmp_dict[key] = eval_param(value, STEP)
                    return tmp_dict
                else:
                    return param

            eval_params = []
            # evaluate all parameters if needed
            for param in params:
                eval_params.append(eval_param(param, step_result))
            return eval_params

        # prepare test execution environment
        self.run_initialize()

        with self._vswitch_ctl, self._loadgen:
            with self._vnf_ctl, self._collector:
                if not self._vswitch_none:
                    self._add_flows()

                # run traffic generator if requested, otherwise wait for manual termination
                if S.getValue('mode') == 'trafficgen-off':
                    time.sleep(2)
                    self._logger.debug("All is set. Please run traffic generator manually.")
                    input(os.linesep + "Press Enter to terminate vswitchperf..." + os.linesep + os.linesep)
                else:
                    with self._traffic_ctl:
                        if not self.test:
                            self._traffic_ctl.send_traffic(self._traffic)
                        else:
                            # execute test based on TestSteps definition
                            if self.test:
                                step_result = [None] * len(self.test)
                                for i, step in enumerate(self.test):
                                    step_ok = False
                                    if step[0] == 'vswitch':
                                        test_object = self._vswitch_ctl.get_vswitch()
                                    elif step[0] == 'trafficgen':
                                        test_object = self._traffic_ctl
                                    else:
                                        self._logger.error("Unsupported test object %s", step[0])
                                        self._inttest = {'status' : False, 'details' : ' '.join(step)}
                                        self.report_status("Step '{}'".format(' '.join(step)), self._inttest['status'])
                                        break

                                    test_method = getattr(test_object, step[1])
                                    test_method_check = getattr(test_object, CHECK_PREFIX + step[1])

                                    step_params = []
                                    if test_method and test_method_check and \
                                        callable(test_method) and callable(test_method_check):

                                        try:
                                            step_params = eval_step_params(step[2:], step_result)
                                            step_log = '{} {}'.format(' '.join(step[:2]), step_params)
                                            step_result[i] = test_method(*step_params)
                                            self._logger.debug("Step {} '{}' results '{}'".format(
                                                i, step_log, step_result[i]))
                                            time.sleep(2)
                                            step_ok = test_method_check(step_result[i], *step_params)
                                        except AssertionError:
                                            self._inttest = {'status' : False, 'details' : step_log}
                                            self._logger.error("Step {} raised assertion error".format(i))
                                            break
                                        except IndexError:
                                            self._inttest = {'status' : False, 'details' : step_log}
                                            self._logger.error("Step {} result index error {}".format(
                                                i, ' '.join(step[2:])))
                                            break

                                    self.report_status("Step {} - '{}'".format(i, step_log), step_ok)
                                    if not step_ok:
                                        self._inttest = {'status' : False, 'details' : step_log}
                                        break

                    # dump vswitch flows before they are affected by VNF termination
                    if not self._vswitch_none:
                        self._vswitch_ctl.dump_vswitch_flows()

        # tear down test execution environment and log results
        self.run_finalize()

        # report test results
        self.run_report()

    def run_report(self):
        """ Report test results
        """
        if self.test:
            results = OrderedDict()
            results['status'] = 'OK' if self._inttest['status'] else 'FAILED'
            results['details'] = self._inttest['details']
            TestCase._write_result_to_file([results], self._output_file)
            self.report_status("Test '{}'".format(self.name), self._inttest['status'])
            # inform vsperf about testcase failure
            if not self._inttest['status']:
                raise Exception
