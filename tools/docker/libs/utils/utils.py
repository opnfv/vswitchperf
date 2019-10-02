# Copyright 2013: Mirantis Inc.
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.


NON_NONE_DEFAULT = object()


def get_key_with_default(data, key, default=NON_NONE_DEFAULT):
    value = data.get(key, default)
    if value is NON_NONE_DEFAULT:
        raise KeyError(key)
    return value


def make_dict_from_map(data, key_map):
    return {dest_key: get_key_with_default(data, src_key, default)
            for dest_key, (src_key, default) in key_map.items()}


def try_int(s, *args):
    """Convert to integer if possible."""
    try:
        return int(s)
    except (TypeError, ValueError):
        return args[0] if args else s
