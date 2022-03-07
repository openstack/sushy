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
# https://redfish.dmtf.org/schemas/SessionService.v1_1_3.json

import logging

from sushy import exceptions
from sushy.resources import base
from sushy.resources.sessionservice import session
from sushy import utils

LOG = logging.getLogger(__name__)


class SessionService(base.ResourceBase):

    description = base.Field('Description')
    """The session service description"""

    identity = base.Field('Id', required=True)
    """The session service identify string"""

    name = base.Field('Name', required=True)
    """The session service name"""

    service_enabled = base.Field('ServiceEnabled')
    """Tells us if session service is enabled"""

    session_timeout = base.Field('SessionTimeout')
    """The session service timeout"""

    def __init__(self, connector, identity, redfish_version=None,
                 registries=None, root=None):
        """A class representing a SessionService

        Warning: This class should only be invoked with a connector which
        has already established authentication.

        :param connector: A Connector instance
        :param identity: The identity of the SessionService resource
        :param redfish_version: The version of RedFish. Used to construct
            the object according to schema of given version.
        :param registries: Dict of Redfish Message Registry objects to be
            used in any resource that needs registries to parse messages
        :param root: Sushy root object. Empty for Sushy root itself.
        """
        # Populating the base resource so session interactions can
        # occur based on the contents of it.
        super(SessionService, self).__init__(
            connector, identity, redfish_version=redfish_version,
            registries=registries, root=root)

    def _get_sessions_collection_path(self):
        """Helper function to find the SessionCollections path"""
        sessions_col = self.json.get('Sessions')
        if not sessions_col:
            raise exceptions.MissingAttributeError(
                attribute='Sessions', resource=self._path)
        return sessions_col.get('@odata.id')

    @property
    @utils.cache_it
    def sessions(self):
        """Property to provide reference to the `SessionCollection` instance

        It is calculated once when the first time it is queried. On refresh,
        this property gets reset.
        """
        return session.SessionCollection(
            self._conn, self._get_sessions_collection_path(),
            redfish_version=self.redfish_version, registries=self.registries,
            root=self.root)

    def close_session(self, session_uri):
        """This function is for closing a session based on its id.

        :raises: ServerSideError
        """
        self._conn.delete(session_uri)

    def create_session(self, username, password, target_uri=None):
        """This function will try to create a session.

        Create a session and return the associated key and URI.

        :param username: the username of the user requesting a new session
        :param password: the password associated to the user requesting
            a new session
        :param target_uri: the "Sessions" uri, usually in the form:
            '/redfish/v1/SessionService/Sessions'
        :returns: A session key and uri in the form of a tuple
        :raises: MissingXAuthToken
        :raises: ConnectionError
        :raises: AccessError
        :raises: HTTPError
        """
        if not target_uri:
            try:
                target_uri = self._get_sessions_collection_path()
            except Exception:
                # Defaulting to /Sessions
                target_uri = self.path + '/Sessions'

        data = {'UserName': username, 'Password': password}
        LOG.debug("Requesting new session from %s.", target_uri)
        rsp = self._conn.post(target_uri, data=data)
        session_key = rsp.headers.get('X-Auth-Token')
        if session_key is None:
            raise exceptions.MissingXAuthToken(
                method='POST', url=target_uri, response=rsp)

        session_uri = rsp.headers.get('Location')
        if session_uri is None:
            LOG.warning("Received X-Auth-Token but NO session uri.")

        return session_key, session_uri
