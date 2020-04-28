"""
Interface for POD
"""

import time
import pexpect
from tools import tasks

class IPod(tasks.Process):
    """
    Interface for POD

    Inheriting from Process helps in managing system process.
    execute a command, wait, kill, etc.
    """
    _number_pods = 0

    def __init__(self):
        """
        Initialization Method
        """
        raise NotImplementedError()

    def create(self):
        """
        Start the Pod
        """
        raise NotImplementedError()


    def terminate(self):
        """
        Stop the Pod
        """
        raise NotImplementedError()

    @staticmethod
    def reset_pod_counter():
        """
        Reset internal POD counter

        This method is static
        """
        IPod._number_pods = 0
