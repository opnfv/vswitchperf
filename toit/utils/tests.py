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
Shared utilities for test suite.

Part of 'toit' - The OVS Integration Testsuite.
"""

from toit.conf import settings


def get_test_param(key, default=None):
    """
    Retrieve value for test param ``key`` if available.

    :param key: Key to retrieve from test params.
    :param default: Default to return if key not found.

    :returns: Value for ``key`` if found, else ``default``.
    """
    test_params = getattr(settings, 'TEST_PARAMS')

    return test_params.get(key, default) if test_params else default


def get_expected_performance(test):
    """
    Retrieve expected performance figures for a given ``test``.

    :param test: Module (test) to get values for

    :returns: Minimum valid test value
    """
    test_name = test.__class__.__name__
    test_mod = test.__module__

    if test_mod in getattr(settings, 'PERF_TARGETS'):
        if test_name in getattr(settings, 'PERF_TARGETS')[test_mod]:
            return getattr(settings, 'PERF_TARGETS')[test_mod][test_name]

    raise ValueError(
        'Did not find valid PERF_TARGET value for test \'%s.%s\'' %
        (test_mod, test_name))


def get_expected_throughput(test):
    """
    Retrieve expected throughput figures for a given ``test``.

    :param test: Module (test) to get values for

    :returns: Minimum valid test value
    """
    test_name = test.__class__.__name__
    test_mod = test.__module__

    if test_mod in getattr(settings, 'THROUGHPUT_TARGETS'):
        if test_name in getattr(settings, 'THROUGHPUT_TARGETS')[test_mod]:
            return getattr(settings, 'THROUGHPUT_TARGETS')[test_mod][test_name]

    raise ValueError(
        'Did not find valid THROUGHPUT_TARGET value for test \'%s.%s\'' %
        (test_mod, test_name))
