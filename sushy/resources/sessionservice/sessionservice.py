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
from sushy.resources import base
from sushy.resources.sessionservice import session

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

    _sessions = None  # ref to SessionCollection instance

    session_timeout = base.Field('SessionTimeout')
    """The session service timeout"""

    def __init__(self, connector, identity, redfish_version=None):
        """A class representing a SessionService

        :param connector: A Connector instance
        :param identity: The identity of the SessionService resource
        :param redfish_version: The version of RedFish. Used to construct
            the object according to schema of given version.
        """
        try:
            super(SessionService, self).__init__(
                connector, identity, redfish_version)
        except exceptions.AccessError as ae:
            LOG.warning('Received access error "%(ae)s". '
                        'Unable to refresh SessionService.',
                        {'ae': ae})

    def _get_sessions_collection_path(self):
        """Helper function to find the SessionCollections path"""
        sessions_col = self.json.get('Sessions')
        if not sessions_col:
            raise exceptions.MissingAttributeError(
                attribute='Sessions', resource=self._path)
        return sessions_col.get('@odata.id')

    @property
    def sessions(self):
        """Property to provide reference to the `SessionCollection` instance

        It is calculated once when the first time it is queried. On refresh,
        this property gets reset.
        """
        if self._sessions is None:
            self._sessions = session.SessionCollection(
                self._conn, self._get_sessions_collection_path(),
                redfish_version=self.redfish_version)

        self._sessions.refresh(force=False)
        return self._sessions

    def _do_refresh(self, force=False):
        """Do custom resource specific refresh activities

        On refresh, all sub-resources are marked as stale, i.e.
        greedy-refresh not done for them unless forced by ``force``
        argument.
        """
        if self._sessions is not None:
            self._sessions.invalidate(force)

    def close_session(self, session_uri):
        """This function is for closing a session based on its id.

        :raises: ServerSideError
        """
        self._conn.delete(session_uri)

    def create_session(self, username, password):
        """This function will try to create a session.

        :returns: A session key and uri in the form of a tuple
        :raises: MissingXAuthToken
        :raises: ConnectionError
        :raises: AccessError
        :raises: HTTPError
        """
        try:
            target_uri = self._get_sessions_collection_path()
        except Exception:
            # Defaulting to /Sessions
            target_uri = self.path + '/Sessions'

        data = {'UserName': username, 'Password': password}
        headers = {'X-Auth-Token': None}

        rsp = self._conn.post(target_uri, data=data, headers=headers)
        session_key = rsp.headers.get('X-Auth-Token')
        if session_key is None:
            raise exceptions.MissingXAuthToken(
                method='POST', url=target_uri, response=rsp)

        session_uri = rsp.headers.get('Location')
        if session_uri is None:
            LOG.warning("Received X-Auth-Token but NO session uri.")

        return session_key, session_uri
