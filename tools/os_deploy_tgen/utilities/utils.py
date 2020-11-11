# Copyright 2020 Spirent Communications, Mirantis
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
Utilities for deploying Trafficgenerator on Openstack.
This Code is based on Openstack Shaker.
"""

#import errno
#import functools
import logging
import os
import random
import re
import uuid
#import collections
import yaml
from pykwalify import core as pykwalify_core
from pykwalify import errors as pykwalify_errors

from conf import settings as S

LOG = logging.getLogger(__name__)

def read_file(file_name, base_dir=''):
    """
    Read Files
    """
    full_path = os.path.normpath(os.path.join(base_dir, file_name))

    if not os.path.exists(full_path):
        full_path = os.path.normpath(os.path.join('tools',
                                                  'os_deploy_tgen',
                                                  file_name))
        if not os.path.exists(full_path):
            full_path = os.path.normpath(os.path.join('tools',
                                                      'os_deploy_tgen',
                                                      'templates',
                                                      file_name))
            if not os.path.exists(full_path):
                msg = ('File %s not found by absolute nor by relative path' %
                       file_name)
                LOG.error(msg)
                raise IOError(msg)

    fid = None
    try:
        fid = open(full_path)
        return fid.read()
    except IOError as exc:
        LOG.error('Error reading file: %s', exc)
        raise
    finally:
        if fid:
            fid.close()


def write_file(data, file_name, base_dir=''):
    """
    Write to file
    """
    full_path = os.path.normpath(os.path.join(base_dir, file_name))
    fid = None
    try:
        fid = open(full_path, 'w')
        return fid.write(data)
    except IOError as err:
        LOG.error('Error writing file: %s', err)
        raise
    finally:
        if fid:
            fid.close()


def read_yaml_file(file_name):
    """
    Read Yaml File
    """
    raw = read_file(file_name)
    return read_yaml(raw)


def read_yaml(raw):
    """
    Read YAML
    """
    try:
        parsed = yaml.safe_load(raw)
        return parsed
    except Exception as error:
        LOG.error('Failed to parse input %(yaml)s in YAML format: %(err)s',
                  dict(yaml=raw, err=error))
        raise


def split_address(address):
    """
    Split addresses
    """
    try:
        host, port = address.split(':')
    except ValueError:
        LOG.error('Invalid address: %s, "host:port" expected', address)
        raise
    return host, port


def random_string(length=6):
    """
    Generate Random String
    """
    return ''.join(random.sample('adefikmoprstuz', length))


def make_record_id():
    """
    Create record-ID
    """
    return str(uuid.uuid4())

def strict(strc):
    """
    Strict Check
    """
    return re.sub(r'[^\w\d]+', '_', re.sub(r'\(.+\)', '', strc)).lower()


def validate_yaml(data, schema):
    """
    Validate Yaml
    """
    cor = pykwalify_core.Core(source_data=data, schema_data=schema)
    try:
        cor.validate(raise_exception=True)
    except pykwalify_errors.SchemaError as err:
        raise Exception('File does not conform to schema') from err


def pack_openstack_params():
    """
    Packe Openstack Parameters
    """
    if not S.hasValue('OS_AUTH_URL'):
        raise Exception(
            'OpenStack authentication endpoint is missing')

    params = dict(auth=dict(username=S.getValue('OS_USERNAME'),
                            password=S.getValue('OS_PASSWORD'),
                            auth_url=S.getValue('OS_AUTH_URL')),
                  os_region_name=S.getValue('OS_REGION_NAME'),
                  os_cacert=S.getValue('OS_CA_CERT'),
                  os_insecure=S.getValue('OS_INSECURE'))

    if S.hasValue('OS_PROJECT_NAME'):
        value = S.getValue('OS_PROJECT_NAME')
        params['auth']['project_name'] = value
    if S.hasValue('OS_PROJECT_DOMAIN_NAME'):
        value = S.getValue('OS_PROJECT_DOMAIN_NAME')
        params['auth']['project_domain_name'] = value
    if S.hasValue('OS_USER_DOMAIN_NAME'):
        value = S.getValue('OS_USER_DOMAIN_NAME')
        params['auth']['user_domain_name'] = value
    if S.hasValue('OS_INTERFACE'):
        value = S.getValue('OS_INTERFACE')
        params['os_interface'] = value
    if S.hasValue('OS_API_VERSION'):
        value = S.getValue('OS_API_VERSION')
        params['identity_api_version'] = value
    if S.hasValue('OS_PROFILE'):
        value = S.getValue('OS_PROFILE')
        params['os_profile'] = value
    return params
