#  Licensed under the Apache License, Version 2.0 (the "License"); you may
#  not use this file except in compliance with the License. You may obtain
#  a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#  WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#  License for the specific language governing permissions and limitations
#  under the License.

# Sushy Redfish Authentication Modes

import abc
import logging

from sushy import exceptions

LOG = logging.getLogger(__name__)


class AuthBase(object, metaclass=abc.ABCMeta):

    def __init__(self, username=None, password=None):
        """A class representing a base Sushy authentication mechanism

        :param username: User account with admin/server-profile
            access privilege.
        :param password: User account password.
        """
        self._username = username
        self._password = password
        self._root_resource = None
        self._connector = None

    def set_context(self, root_resource, connector):
        """Set the context of the authentication object.

        :param root_resource: Root sushy object
        :param connector: Connector for http connections
        """
        # Set the root resource, and connector to use
        # for normal opreations.
        self._root_resource = root_resource
        self._connector = connector
        self._connector.set_auth(self)

    def authenticate(self):
        """Perform authentication.

        :raises: RuntimeError
        """
        if self._root_resource is None or self._connector is None:
            raise RuntimeError('_root_resource / _connector is missing. '
                               'Forgot to call set_context()?')
        self._do_authenticate()

    @abc.abstractmethod
    def _do_authenticate(self):
        """Method to establish a session to a Redfish controller.

        Needs to be implemented by extending auth class,
        because each authentication type will authenticate in its own way.
        """

    @abc.abstractmethod
    def can_refresh_session(self):
        """Method to assert if session based refresh can be done."""

    def close(self):
        """Shutdown Redfish authentication object

        Undoes whatever should be undone to cancel authenticated session.
        """

    def __enter__(self):
        """Allow object to be called with the 'with' statement."""
        return self

    def __exit__(self, exception_type, exception_value, traceback):
        """Allow object to be called with the 'with' statement.

        Allow object to be called with the 'with' statement but
        also ensure we call close method on exit.
        """
        self.close()


class BasicAuth(AuthBase):
    """Basic Authentication class.

       This is a class used to encapsulate a basic authentication session.

       :param username: User account with admin/server-profile
           access privilege.
       :param password: User account password.
    """

    def _do_authenticate(self):
        """Attempts to establish a Basic Authentication Session.

        """
        LOG.debug('Setting basic authentication connector information.')
        self._connector.set_http_basic_auth(self._username, self._password)

    def can_refresh_session(self):
        """Method to assert if session based refresh can be done."""
        return False


class SessionAuth(AuthBase):
    """Session Authentication class.

       This is a class used to encapsulate a redfish session.
    """

    def __init__(self, username=None, password=None):
        """A class representing a Session Authentication object.

        :param username: User account with admin/server-profile access
             privilege.
        :param password: User account password.
        """
        self._session_key = None
        """Our Sessions Key"""
        self._session_resource_id = None
        """Our Sessions Unique Resource ID or URL"""
        self._session_auth_previously_successful = False
        """Our reminder for tracking if session auth has previously worked."""

        super(SessionAuth, self).__init__(username,
                                          password)

    def get_session_key(self):
        """Returns the session key.

        :returns: The session key.
        """
        return self._session_key

    def get_session_resource_id(self):
        """Returns the session resource id.

        :returns: The session resource id.
        """
        return self._session_resource_id

    def _do_authenticate(self):
        """Establish a redfish session.

        :raises: MissingXAuthToken
        :raises: ConnectionError
        :raises: AccessError
        :raises: HTTPError
        """
        auth_token = None

        auth_token, session_uri = self._root_resource.create_session(
            self._username, self._password)
        # Record the session authentication data.
        self._session_key = auth_token
        self._session_resource_id = session_uri
        # Set flag so we know we've previously successfully achieved
        # session authentication in order to lockout possible fallback during
        # session refresh/renegotiation.
        self._session_auth_previously_successful = True
        self._connector.set_http_session_auth(auth_token)

    def can_refresh_session(self):
        """Method to assert if session based refresh can be done."""
        return (self._session_key is not None
                and self._session_resource_id is not None)

    def refresh_session(self):
        """Method to refresh a session to a Redfish controller.

        This method is called to create a new session after
        a session that has already been established
        has timed-out or expired.

        :raises: MissingXAuthToken
        :raises: ConnectionError
        :raises: AccessError
        :raises: HTTPError
        """
        self.reset_session_attrs()
        self._do_authenticate()

    def close(self):
        """Close the Redfish Session.

        Attempts to close an established RedfishSession by
        deleting it from the remote Redfish controller.
        """
        if self._session_resource_id is not None:
            try:
                self._connector.delete(self._session_resource_id)
            except (exceptions.AccessError,
                    exceptions.ServerSideError) as exc:
                LOG.warning('Received exception "%(exception)s" while '
                            'attempting to delete the active session: '
                            '%(session_id)s',
                            {'exception': exc,
                             'session_id': self._session_resource_id})
            self.reset_session_attrs()

    def reset_session_attrs(self):
        """Reset active session related attributes."""
        self._session_key = None
        self._session_resource_id = None
        # Requests session object data is merged with user submitted data
        # per https://requests.readthedocs.io/en/master/user/advanced/
        # so we need to clear data explicitly set on the session too.
        self._connector._session.auth = None
        if 'X-Auth-Token' in self._connector._session.headers:
            # Delete the token value that was saved to the session
            # as otherwise we would end up with a dictionary containing
            # a {'X-Auth-Token': null} being sent across to the remote
            # bmc.
            del self._connector._session.headers['X-Auth-Token']


class SessionOrBasicAuth(SessionAuth):

    def __init__(self, username=None, password=None):
        super(SessionOrBasicAuth, self).__init__(username, password)
        self.basic_auth = BasicAuth(username=username, password=password)

    def _fallback_to_basic_authentication(self):
        """Fallback to basic authentication."""
        self.reset_session_attrs()
        self.basic_auth.set_context(self._root_resource, self._connector)
        self.basic_auth.authenticate()

    def _do_authenticate(self):
        """Establish a RedfishSession.

        We will attempt to establish a redfish session. If we are unable
        to establish one, fallback to basic authentication.
        """
        try:
            # Attempt session based authentication
            super(SessionOrBasicAuth, self)._do_authenticate()
        except exceptions.AccessError as e:
            if (not self.can_refresh_session()
                    and not self._session_auth_previously_successful):
                # We should only try and fallback if we've not been able
                # to establish a session. If we had a session previously
                # and we're trying to fallback, something fishy is afoot.
                LOG.warning('Falling back to "Basic" authentication as '
                            'we have been unable to authenticate to the '
                            'BMC. Exception: %(exception)s.',
                            {'exception': e})
                self._fallback_to_basic_authentication()
            else:
                # We previously had session authentication, something
                # has changed which is far out of the ordinary.
                LOG.debug('Received exception "%(exception)s" while '
                          'attempting to re-establish a session. '
                          'Raising AccessError, as something fishy '
                          'has occurred and the BMC has suddenly '
                          'ceased to support Session based '
                          'authentication.',
                          {'exception': e})
                raise
        except exceptions.ConnectionError as e:
            # The reason to explicitly catch a connectivity failure is the
            # case where transitory connectivity failures can occur while
            # working to authenticate.
            LOG.debug('Encountered a connectivity failure while attempting '
                      'to authenticate. We will not explicitly fallback. '
                      'Error: %(exception)s',
                      {'exception': e})
            # Previously we would silently eat the failure as SushyError
            # and fallback as it is a general fault. Callers on direct
            # invocations through a connector _op method call can still
            # receieve these exceptions, and applicaitons like Ironic do
            # consider a client re-use disqualifier if there has been
            # a connection failure, so it is okay for us to fix the behavior
            # here.
            raise
        except exceptions.SushyError as e:
            LOG.debug('Received exception "%(exception)s" while '
                      'attempting to establish a session. '
                      'Falling back to basic authentication.',
                      {'exception': e})
            self._fallback_to_basic_authentication()

    def refresh_session(self):
        """Method to refresh a session to a Redfish controller.

        This method is called to create a new RedfishSession
        if we have previously established a RedfishSession and
        the previous session has timed-out or expired.
        If we did not previously have an established session,
        we simply return our BasicAuthentication requests.Session.
        """
        if self.can_refresh_session():
            super(SessionOrBasicAuth, self).refresh_session()
