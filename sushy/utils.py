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

from sushy import exceptions

LOG = logging.getLogger(__name__)


def revert_dictionary(dictionary):
    """Given a dictionary revert it's mapping

    :param dictionary: A dictionary to be reverted
    :returns: A dictionary with the keys and values reverted

    """
    return {v: k for k, v in dictionary.items()}


def get_members_identities(members):
    """Extract and return a tuple of members identities

    :param members: A list of members in JSON format
    :returns: A tuple containing the members paths

    """
    members_list = []
    for member in members:
        path = member.get('@odata.id')
        if not path:
            LOG.warning('Could not find the \'@odata.id\' attribute for '
                        'member %s', member)
            continue
        members_list.append(path.rstrip('/'))

    return tuple(members_list)


def int_or_none(x):
    """Given a value x it cast as int or None

    :param x: The value to transform and return
    :returns: Either None or x cast to an int

    """
    if x is None:
        return None
    return int(x)


def get_sub_resource_path_by(resource, subresource_name):
    """Helper function to find the subresource path

    :param resource: ResourceBase instance on which the name
        gets queried upon.
    :param subresource_name: name of the resource field to
        fetch the '@odata.id' from.
    """
    subresource_element = resource.json.get(subresource_name)
    if not subresource_element:
        raise exceptions.MissingAttributeError(attribute=subresource_name,
                                               resource=resource.path)
    if '@odata.id' not in subresource_element:
        raise exceptions.MissingAttributeError(
            attribute=(subresource_name + '/@odata.id'),
            resource=resource.path)
    return subresource_element['@odata.id']
