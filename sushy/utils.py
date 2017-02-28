# Copyright 2017 Red Hat, Inc.
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

import logging
import os

LOG = logging.getLogger(__name__)


def revert_dictionary(dictionary):
    """Given a dictionary revert it's mapping

    :param dictionary: A dictionary to be reverted
    :returns: A dictionary with the keys and values reverted

    """
    return {v: k for k, v in dictionary.items()}


def get_members_ids(members):
    """Extract and return a tuple of members identities

    :param members: A list of members in JSON format
    :returns: A tuple containing the members identities

    """
    members_list = []
    for member in members:
        identity = member.get('@odata.id')
        if not identity:
            LOG.warning('Could not find the \'@odata.id\' attribute for '
                        'member %s', member)
            continue
        members_list.append(os.path.basename(identity.rstrip('/')))

    return tuple(members_list)


def strip_redfish_base(path):
    """Strip redfish base 'redfish/v1/' from path

    :param path: A string of redfish resource path
    :returns: path without redfish base 'redfish/v1/'

    """
    sub_path = path.lstrip('/')

    # To support further redfish version, didn't hardcode to 'redfish/v1'
    redfish_base_path = 'redfish/v'

    if sub_path.startswith(redfish_base_path):
        # Find next occurrence of '/' after redfish base path and strip the
        # base path before it
        sub_path = sub_path[sub_path.find('/', len(redfish_base_path)) + 1:]

    return sub_path
