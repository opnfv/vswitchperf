# Copyright 2016-2017 Intel Corporation.
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

import logging
import subprocess
import locale
from tools.functions import filter_output
from tools.tasks import run_background_task

_LOGGER = logging.getLogger(__name__)

class TestStepsTools(object):
    """ Various tools and functions used by step driven testcases
    """
    # Functions use nonstandard names to avoid conflicts with
    # standard python keywords.
    # pylint: disable=invalid-name
    @staticmethod
    def Assert(condition):
        """ Evaluate given `condition' and raise AssertionError
            in case, that evaluation fails
        """
        try:
            assert TestStepsTools.Eval(condition)
        except AssertionError:
            _LOGGER.error('Condition %s is not True', condition)
            raise

        return True

    @staticmethod
    def validate_Assert(result, _dummy_condition):
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
    def validate_Eval(result, _dummy_expression):
        """ Validate result of python `expression' evaluation
        """
        return result is not None

    @staticmethod
    def Exec_Python(code):
        """ Execute a python `code' and return True on success
        """
        # pylint: disable=exec-used
        try:
            exec(code, globals())
        # pylint: disable=broad-except
        # pylint: disable=bare-except
        except:
            _LOGGER.error('Execution of following code has failed %s', code)
            return False
        return True

    @staticmethod
    def validate_Exec_Python(result, _dummy_code):
        """ Validate result of python `code' execution
        """
        return result

    @staticmethod
    def Exec_Shell(command, regex=None):
        """ Execute a shell `command' and return its output filtered
            out by optional `regex' expression.
        """
        try:
            output = subprocess.check_output(command, shell=True)
        except OSError:
            return None

        output = output.decode(locale.getdefaultlocale()[1])

        if regex:
            return filter_output(output, regex)

        return output

    @staticmethod
    def validate_Exec_Shell(result, _dummy_command, _dummy_regex=None):
        """ validate result of shell `command' execution
        """
        return result is not None

    @staticmethod
    def Exec_Shell_Background(command):
        """ Execute a shell `command' at the background and return its PID id
        """
        try:
            pid = run_background_task(command.split(), _LOGGER, "Background task: {}".format(command))
            return pid
        except OSError:
            return None

    @staticmethod
    def validate_Exec_Shell_Background(result, _dummy_command, _dummy_regex=None):
        """ validate result of shell `command' execution on the background
        """
        return result is not None
