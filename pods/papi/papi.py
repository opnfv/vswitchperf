# Copyright 2020 University Of Delhi.
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
Automation of Pod Deployment with Kubernetes Python API
"""

# import os
import logging
import json
import time
import yaml
from kubernetes import client, config
from kubernetes.client.rest import ApiException

from conf import settings as S
from pods.pod.pod import IPod

class Papi(IPod):
    """
    Class for controlling the pod through PAPI
    """

    def __init__(self):
        """
        Initialisation function.
        """
        #super(Papi, self).__init__()
        super().__init__()

        self._logger = logging.getLogger(__name__)
        self._sriov_config = None
        self._sriov_config_ns = None
        config.load_kube_config(S.getValue('K8S_CONFIG_FILEPATH'))

    def create(self):
        """
        Creation Process
        """
        # create vswitchperf namespace
        api = client.CoreV1Api()
        namespace = 'default'
        #namespace = 'vswitchperf'
        # replace_namespace(api, namespace)

        # sriov configmap
        if S.getValue('PLUGIN') == 'sriov':
            configmap = load_manifest(S.getValue('CONFIGMAP_FILEPATH'))
            self._sriov_config = configmap['metadata']['name']
            self._sriov_config_ns = configmap['metadata']['namespace']
            api.create_namespaced_config_map(self._sriov_config_ns, configmap)


        # create nad(network attachent definitions)
        group = 'k8s.cni.cncf.io'
        version = 'v1'
        kind_plural = 'network-attachment-definitions'
        api = client.CustomObjectsApi()

        for nad_filepath in S.getValue('NETWORK_ATTACHMENT_FILEPATH'):
            nad_manifest = load_manifest(nad_filepath)

            try:
                response = api.create_namespaced_custom_object(group, version, namespace,
                                                               kind_plural, nad_manifest)
                self._logger.info(str(response))
                self._logger.info("Created Network Attachment Definition: %s", nad_filepath)
            except ApiException as err:
                raise Exception from err

        #create pod workloads
        pod_manifest = load_manifest(S.getValue('POD_MANIFEST_FILEPATH'))
        api = client.CoreV1Api()

        try:
            response = api.create_namespaced_pod(namespace, pod_manifest)
            self._logger.info(str(response))
            self._logger.info("Created POD %d ...", self._number)
        except ApiException as err:
            raise Exception from err

        time.sleep(12)

    def terminate(self):
        """
        Cleanup Process
        """
        #self._logger.info(self._log_prefix + "Cleaning vswitchperf namespace")
        self._logger.info("Terminating Pod")
        api = client.CoreV1Api()
        # api.delete_namespace(name="vswitchperf", body=client.V1DeleteOptions())

        if S.getValue('PLUGIN') == 'sriov':
            api.delete_namespaced_config_map(self._sriov_config, self._sriov_config_ns)


def load_manifest(filepath):
    """
    Reads k8s manifest files and returns as string

    :param str filepath: filename of k8s manifest file to read

    :return: k8s resource definition as string
    """
    with open(filepath) as handle:
        data = handle.read()

    try:
        manifest = json.loads(data)
    except json.decoder.JSONDecodeError:
        try:
            manifest = yaml.safe_load(data)
        except yaml.parser.ParserError as err:
            raise Exception from err

    return manifest

def replace_namespace(api, namespace):
    """
    Creates namespace if does not exists
    """
    namespaces = api.list_namespace()
    for nsi in namespaces.items:
        if namespace == nsi.metadata.name:
            api.delete_namespace(name=namespace,
                                 body=client.V1DeleteOptions())
            break

        time.sleep(0.5)
        api.create_namespace(client.V1Namespace(
            metadata=client.V1ObjectMeta(name=namespace)))
