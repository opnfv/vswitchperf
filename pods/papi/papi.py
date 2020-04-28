
"""
Automation of Pod Deployment with Kubernetes Python API
"""

class IPodPapi(IPod):
    """
    Class for controlling the pod through PAPI
    """
    def __init__(self):
        """
        Initialisation function.
        """
        super(IPodPapi, self).__init__()
        name, ext = os.path.splitext(S.getValue('LOG_FILE_POD'))

    def create(self):
        """
        Creation Process
        """

    def destroy(self):
        """
        Cleanup Process
        """
