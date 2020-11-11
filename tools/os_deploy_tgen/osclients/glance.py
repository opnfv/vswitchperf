# Copyright (c) 2020 Mirantis Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Glance CLient
"""

def get_image(glance_client, image_name):
    """
    Get the IMage
    """
    for image in glance_client.images.list():
        if image.name == image_name:
            return image
    return None


def get_supported_versions(glance_client):
    """
    Get Supported Version
    """
    return set(version['id'] for version in glance_client.versions.list())
