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

import os


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
            continue
        members_list.append(os.path.basename(identity))

    return tuple(members_list)
