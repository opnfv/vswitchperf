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

"""
Handlers for tests.

Part of 'toit' - The OVS Integration Testsuite.
"""

import re
import unittest
import inspect

from toit.conf import settings

# match xxx, xxx.xxx, xxx.xxx.xxx, etc.
SPEC_RE = re.compile(
    r'^[a-zA-Z0-9_]+(\.([a-zA-Z0-9_]+))*$')


def _load_testsuite(test_dir=None):
    """
    Load tests from ``tests`` folder.

    Load tests dynamically using the ``imp`` module.

    :param test_dir: Path to a folder of test cases

    :returns: List of test case functions
    """
    if not test_dir:
        test_dir = getattr(settings, 'TEST_DIR')

    suite = unittest.TestSuite()

    for tests_suites in unittest.defaultTestLoader.discover(
            test_dir, pattern='*.py'):
        for test_suite in tests_suites:
            suite.addTests(test_suite)

    return suite


def load_tests_spec(spec_file, test_dir=None):
    """
    Read a test specification from ``spec_file`` and load matching tests.

    :param test_dir: Path to a folder of test cases
    :type test_dir: str
    :param spec_file: Path to a test specification file
    :type: str

    :returns: List of test case functions filtered by spec file
    """
    lines = []

    with open(spec_file, 'r+') as file_:
        for line in file_:
            line, _, _ = line.partition('#')  # remove comments
            line = line.strip()
            if not line:
                continue

            spec = SPEC_RE.match(line)
            if not spec:
                continue  # invalid specification line, drop silently

            lines.append(line)

    output = load_tests_list(lines, test_dir)

    return output


def load_tests_list(tests, test_dir=None):
    """
    Load a list of tests, given by ``tests``, from ``test_dir``.

    :param tests: List of tests to run
    :type tests: [str, ...]
    :param test_dir: Path to a folder of test cases
    :type test_dir: str

    :returns: List of test case functions
    """
    testsuite = _load_testsuite(test_dir)
    test_spec = []
    output = []

    for test in tests:
        if not SPEC_RE.match(test):
            continue
        else:
            test_spec.append(test.split('.'))

    for test in testsuite:
        _test_id = test.id().split('.')

        # we do a substring match on tests. If a user provides 'xxx' then
        # we should match 'xxx.*' tests (e.g. 'xxx.yy1', 'xxx.yyy.zz1'),
        # while 'xxx.yyy' should match 'xxx.yyy.*' tests (e.g.
        # 'xxx.yyy.zz1')
        for test_item in test_spec:
            llen = len(test_item)
            if any((test_item == _test_id[i:i + llen]) for i in xrange(
                    len(test_item) - llen + 1)):
                output.append(test)

    # remove duplicates
    output = list(set(output))

    return output


def load_tests_all(test_dir=None):
    """
    Load all tests from ``test_dir`` directory.

    :param test_dir: Path to a folder of test cases
    :type test_dir: str

    :returns: List of test case functions
    """
    return _load_testsuite(test_dir)


def list_tests():
    """
    Get a list of all modules and their tests from ``tests`` folder.

    :returns: List of modules with name, description and tests.
    :rtype: [(modname, moddesc, [(testname, testdesc), ...]), ...]
    """
    testsuite = _load_testsuite()

    tests = {}
    names = {}

    def get_doc(module):
        """Get summary-line from docstring for a module."""
        return inspect.getdoc(module).split('\n')[0] or 'No description.'

    for test in testsuite:
        _test_id = test.id().split('.')
        mod_name = '.'.join(_test_id[0:-2])
        test_name = _test_id[-2]
        test_desc = get_doc(test)

        if mod_name in tests:
            tests[mod_name].append((test_name, test_desc))
        else:
            tests[mod_name] = [(test_name, test_desc)]
            names[mod_name] = get_doc(inspect.getmodule(test))

    results = [(x, names[x], tests[x]) for x in tests]

    return results


def print_tests():
    """
    Get a string representation of tests in the ``tests`` folder.
    """
    test_modules = list_tests()

    output = ['Tests:\n======\n']

    for (modname, moddesc, modtests) in sorted(test_modules):
        output.append('%-23s %-54s\n' % ('[%s]' % modname, moddesc))

        for (testname, testdesc) in sorted(modtests):
            output.append('* %-22s%s' % ('%s:' % testname, testdesc))

        output.append('')

    output.append('')

    return '\n'.join(output)
