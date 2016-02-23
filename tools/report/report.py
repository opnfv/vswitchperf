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

"""
vSwitch Characterization Report Generation.

Generate reports in format defined by X.
"""

import sys
import os
import jinja2
import logging

from core.results.results_constants import ResultsConstants
from conf import settings as S
from tools import systeminfo

_TEMPLATE_FILES = ['report.jinja', 'report_rst.jinja']
_ROOT_DIR = os.path.normpath(os.path.dirname(os.path.realpath(__file__)))


def _get_env(result):
    """
    Get system configuration.

    :returns: Return a dictionary of the test environment.
              The following is an example return value:
               {'kernel': '3.10.0-229.4.2.el7.x86_64',
                'os': 'OS Version',
                'cpu': ' CPU 2.30GHz',
                'platform': '[2 sockets]',
                'nic': 'NIC'}

    """

    env = {
        'os': systeminfo.get_os(),
        'kernel': systeminfo.get_kernel(),
        'nics': systeminfo.get_nic(),
        'cpu': systeminfo.get_cpu(),
        'cpu_cores': systeminfo.get_cpu_cores(),
        'memory' : systeminfo.get_memory(),
        'platform': systeminfo.get_platform(),
        'vsperf': systeminfo.get_version('vswitchperf'),
        'traffic_gen': systeminfo.get_version(S.getValue('TRAFFICGEN')),
        'vswitch': systeminfo.get_version(S.getValue('VSWITCH')),
    }

    if S.getValue('VSWITCH').lower().count('dpdk'):
        env.update({'dpdk': systeminfo.get_version('dpdk')})

    if result[ResultsConstants.DEPLOYMENT].count('v'):
        env.update({'vnf': systeminfo.get_version(S.getValue('VNF')),
                    'guest_image': S.getValue('GUEST_IMAGE'),
                    'loopback_app': list(map(systeminfo.get_version, S.getValue('GUEST_LOOPBACK'))),
                   })

    return env


def generate(input_file, tc_results, tc_stats, test_type='performance'):
    """Generate actual report.

    Generate a Markdown-formatted file using results of tests and some
    parsed system info.

    :param input_file: Path to CSV results file

    :returns: Path to generated report
    """
    output_files = [('.'.join([os.path.splitext(input_file)[0], 'md'])),
                    ('.'.join([os.path.splitext(input_file)[0], 'rst']))]
    template_loader = jinja2.FileSystemLoader(searchpath=_ROOT_DIR)
    template_env = jinja2.Environment(loader=template_loader)

    tests = []
    try:
        for result in tc_results:
            test_config = {}
            if test_type == 'performance':
                for tc_conf in S.getValue('PERFORMANCE_TESTS'):
                    if tc_conf['Name'] == result[ResultsConstants.ID]:
                        test_config = tc_conf
                        break
            else:
                for tc_conf in S.getValue('INTEGRATION_TESTS'):
                    if tc_conf['Name'] == result[ResultsConstants.ID]:
                        test_config = tc_conf
                        break

            # pass test results, env details and configuration to template
            tests.append({
                'ID': result[ResultsConstants.ID].upper(),
                'id': result[ResultsConstants.ID],
                'deployment': result[ResultsConstants.DEPLOYMENT],
                'conf': test_config,
                'result': result,
                'env': _get_env(result),
                'stats': tc_stats
            })

            # remove id and deployment from results before rendering
            # but after _get_env() is called; tests dict has its shallow copy
            del result[ResultsConstants.ID]
            del result[ResultsConstants.DEPLOYMENT]

        template_vars = {
            'tests': tests,
        }
        i = 0
        for output_file in output_files:
            template = template_env.get_template(_TEMPLATE_FILES[i])
            output_text = template.render(template_vars) #pylint: disable=no-member
            with open(output_file, 'w') as file_:
                file_.write(output_text)
                logging.info('Test report written to "%s"', output_file)
            i += 1

    except KeyError:
        logging.info("Report: Ignoring file (Wrongly defined columns): %s",
                     (input_file))
        raise
    return output_files


if __name__ == '__main__':
    S.load_from_dir('conf')
    OUT = generate(sys.argv[1], '', '')
    print('Test report written to "%s"...' % OUT)
