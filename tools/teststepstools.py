# Copyright 2016 Intel Corporation.
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

"""Various helper functions for step driven testcases
"""

import re
import logging
import subprocess
import locale

class TestStepsTools(object):
    """ Various tools and functions used by step driven testcases
    """
    # Functions use nonstandard names to avoid conflicts with
    # standard python keywords.
    # pylint: disable=invalid-name
    def __init__(self):
        """ TestStepsTools initialization
        """
        self._logger = logging.getLogger(__name__)

    def Assert(self, condition):
        """ Evaluate given `condition' and raise AssertionError
            in case, that evaluation fails
        """
        try:
            assert self.Eval(condition)
        except AssertionError:
            self._logger.error('Condition %s is not True', condition)
            raise

        return True

    @staticmethod
    def validate_Assert(result, dummy_condition):
        """ Validate evaluation of given `condition'
        """
        return result

    @staticmethod
    def Eval(expression):
        """ Evaluate python `expression' and return its result
        """
        # pylint: disable=eval-used
        return eval(expression)

    @staticmethod
    def validate_Eval(result, dummy_expression):
        """ Validate result of python `expression' evaluation
        """
        return result is not None

    @staticmethod
    def Exec(command, regex=None):
        """ Execute a shell `command' and return its output filtered
            out by optional `regex' expression.
        """
        try:
            output = subprocess.check_output(command, shell=True)
        except OSError:
            return None

        output = output.decode(locale.getdefaultlocale()[1])

        if regex:
            for line in output.split('\n'):
                result = re.findall(regex, line)
                if result:
                    return result
            return []

        return output

    @staticmethod
    def validate_Exec(result, dummy_command, dummy_regex=None):
        """ validate result of shell `command' execution
        """
        return result is not None
