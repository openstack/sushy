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

# This is referred from Redfish standard schema.
# https://redfish.dmtf.org/schemas/Session.v1_1_0.json

import logging

from sushy.resources import base

LOG = logging.getLogger(__name__)


class Session(base.ResourceBase):

    description = base.Field('Description')
    """The session service description"""

    identity = base.Field('Id', required=True)
    """The session service identify string"""

    name = base.Field('Name', required=True)
    """The session service name"""

    username = base.Field('UserName')
    """The UserName for the account for this session."""

    def __init__(self, connector, identity, redfish_version=None,
                 registries=None, root=None):
        """A class representing a Session

        :param connector: A Connector instance
        :param identity: The identity of the Session resource
        :param redfish_version: The version of RedFish. Used to construct
            the object according to schema of given version.
        :param registries: Dict of Redfish Message Registry objects to be
            used in any resource that needs registries to parse messages
        :param root: Sushy root object. Empty for Sushy root itself.
        """
        super(Session, self).__init__(
            connector, identity, redfish_version=redfish_version,
            registries=registries, root=root)

    def delete(self):
        """Method for deleting a Session.

        :raises: ServerSideError
        """
        self._conn.delete(self.path)


class SessionCollection(base.ResourceCollectionBase):

    name = base.Field('Name')
    """The session collection name"""

    description = base.Field('Description')
    """The session collection description"""

    @property
    def _resource_type(self):
        return Session

    def __init__(self, connector, identity, redfish_version=None,
                 registries=None, root=None):
        """A class representing a SessionCollection

        :param connector: A Connector instance
        :param identity: The identity of the Session resource
        :param redfish_version: The version of RedFish. Used to construct
            the object according to schema of given version.
        :param registries: Dict of Redfish Message Registry objects to be
            used in any resource that needs registries to parse messages
        :param root: Sushy root object. Empty for Sushy root itself.
        """
        super(SessionCollection, self).__init__(
            connector, identity, redfish_version=redfish_version,
            registries=registries, root=root)
