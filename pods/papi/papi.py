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

import os
import logging
import json
import yaml
from kubernetes import client, config, utils
from kubernetes.client.rest import ApiException

from conf import settings as S
from pods import IPod

class IPodPapi(IPod):
    """
    Class for controlling the pod through PAPI
    """

    def __init__(self):
        """
        Initialisation function.
        """
        super(IPodPapi, self).__init__()

        self._logger = logging.getLogger(__name__)
        config.load_kube_config(S.getValue('K8S_CONFIG_FILEPATH'))



    def create(self):
        """
        Creation Process
        """
        # create vswitchperf namespace
        api = client.CoreV1Api()
        namespace = 'vswitchperf'
        api.create_namespace(client.V1Namespace(metadata=client.V1ObjectMeta(name=namespace)))


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
                self._logger.info(self._log_prefix + str(response))
                self._logger.info(self._log_prefix + f"Created Network Attachment Definition: {nad_filepath}")
            except ApiException as e:
                raise Exception(f"Failed to create Network Attachment Definition: {nad_filepath}")

        #create pod workloads
        pod_manifest = load_manifest(S.getValue('POD_MANIFEST_FILEPATH'))
        api = client.CoreV1Api()

        response = api.create_namespaced_pod(namespace, pod_manifest)
        self._logger.info(self._log_prefix + str(response))
        self._logger.info(self._log_prefix + "Created POD %d ...", self._number)


    def terminate(self):
        """
        Cleanup Process
        """
        self._logger.info(self._log_prefix + "Cleaning vswitchperf namespace")
        api = client.CoreV1Api()
        api.delete_namespace(name="vswitchperf", body=client.V1DeleteOptions())

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
        except yaml.parser.ParserError:
            raise Exception(f"Invalid file: {filename}")

    return manifest
