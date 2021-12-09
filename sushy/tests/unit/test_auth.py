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

from unittest import mock

import requests

from sushy import auth
from sushy import connector
from sushy import exceptions
from sushy import main
from sushy.tests.unit import base


class BasicAuthTestCase(base.TestCase):

    @mock.patch.object(main, 'Sushy', autospec=True)
    @mock.patch.object(connector, 'Connector', autospec=True)
    def setUp(self, mock_connector, mock_root):
        super(BasicAuthTestCase, self).setUp()
        self.username = 'TestUsername'
        self.password = 'TestP@$$W0RD'
        self.base_auth = auth.BasicAuth(self.username,
                                        self.password)
        self.conn = mock_connector.return_value
        self.root = mock_root.return_value

    def test_init(self):
        self.assertEqual(self.username,
                         self.base_auth._username)
        self.assertEqual(self.password,
                         self.base_auth._password)
        self.assertIsNone(self.base_auth._root_resource)
        self.assertIsNone(self.base_auth._connector)

    def test_set_context(self):
        self.base_auth.set_context(self.root, self.conn)
        self.assertEqual(self.base_auth._root_resource,
                         self.root)
        self.assertEqual(self.base_auth._connector,
                         self.conn)

    def test__do_authenticate_no_context(self):
        self.assertRaises(RuntimeError,
                          self.base_auth.authenticate)

    def test__do_authenticate(self):
        self.base_auth.set_context(self.root, self.conn)
        self.base_auth.authenticate()
        self.conn.set_http_basic_auth.assert_called_once_with(self.username,
                                                              self.password)

    def test_can_refresh_session(self):
        self.assertFalse(self.base_auth.can_refresh_session())

    @mock.patch.object(auth.BasicAuth, 'close', autospec=True)
    def test_context_manager(self, auth_close):
        with auth.BasicAuth(self.username, self.password) as base_auth:
            self.assertEqual(self.username, base_auth._username)
            self.assertEqual(self.password, base_auth._password)
        auth_close.assert_called_once_with(base_auth)


class SessionAuthTestCase(base.TestCase):

    @mock.patch.object(main, 'Sushy', autospec=True)
    @mock.patch.object(connector, 'Connector', autospec=True)
    def setUp(self, mock_connector, mock_root):
        super(SessionAuthTestCase, self).setUp()
        self.username = 'TestUsername'
        self.password = 'TestP@$$W0RD'
        self.sess_key = 'TestingKey'
        self.sess_uri = ('https://testing:8000/redfish/v1/'
                         'SessionService/Sessions/testing')
        self.sess_auth = auth.SessionAuth(self.username,
                                          self.password)
        self.conn = mock_connector.return_value
        self.conn._session = mock.Mock(spec=requests.Session)
        self.conn._session.headers = {}
        self.conn._session.auth = None
        self.root = mock_root.return_value

    def test_init(self):
        self.assertEqual(self.username,
                         self.sess_auth._username)
        self.assertEqual(self.password,
                         self.sess_auth._password)
        self.assertIsNone(self.sess_auth._root_resource)
        self.assertIsNone(self.sess_auth._connector)
        self.assertIsNone(self.sess_auth._session_key)
        self.assertIsNone(self.sess_auth._session_resource_id)

    def test_get_session_key(self):
        self.sess_auth._session_key = self.sess_key
        self.assertEqual(self.sess_key,
                         self.sess_auth.get_session_key())

    def test_get_session_resource_id(self):
        self.sess_auth._session_resource_id = self.sess_uri
        self.assertEqual(self.sess_uri,
                         self.sess_auth.get_session_resource_id())

    def test_reset_session_attrs(self):
        self.sess_auth.set_context(self.root, self.conn)
        self.sess_auth._session_key = self.sess_key
        self.sess_auth._session_resource_id = self.sess_uri
        self.conn._session.headers = {'X-Auth-Token': 'meow'}
        self.assertEqual(self.sess_uri,
                         self.sess_auth.get_session_resource_id())
        self.assertEqual(self.sess_key,
                         self.sess_auth.get_session_key())
        self.sess_auth.reset_session_attrs()
        self.assertIsNone(self.sess_auth.get_session_resource_id())
        self.assertIsNone(self.sess_auth.get_session_key())
        self.assertNotIn('X-Auth-Token', self.conn._session.headers)

    def test_set_context(self):
        self.sess_auth.set_context(self.root, self.conn)
        self.assertEqual(self.sess_auth._root_resource,
                         self.root)
        self.assertEqual(self.sess_auth._connector,
                         self.conn)

    def test__do_authenticate_no_context(self):
        self.assertRaises(RuntimeError,
                          self.sess_auth.authenticate)

    def test__do_authenticate(self):
        self.assertIsNone(self.sess_auth.get_session_resource_id())
        self.assertIsNone(self.sess_auth.get_session_key())
        self.assertFalse(self.sess_auth._session_auth_previously_successful)
        self.root.create_session.return_value = (self.sess_key,
                                                 self.sess_uri)
        self.sess_auth.set_context(self.root, self.conn)
        self.sess_auth.authenticate()
        self.assertEqual(self.sess_uri,
                         self.sess_auth.get_session_resource_id())
        self.assertEqual(self.sess_key,
                         self.sess_auth.get_session_key())
        self.assertTrue(self.sess_auth._session_auth_previously_successful)
        self.conn.set_http_session_auth.assert_called_once_with(self.sess_key)

    def test_can_refresh_session(self):
        self.root.create_session.return_value = (self.sess_key,
                                                 self.sess_uri)
        self.sess_auth.set_context(self.root, self.conn)
        self.sess_auth.authenticate()

        self.assertTrue(self.sess_auth.can_refresh_session())

    def test_refresh(self):
        self.assertIsNone(self.sess_auth.get_session_resource_id())
        self.assertIsNone(self.sess_auth.get_session_key())
        self.root.create_session.return_value = (self.sess_key,
                                                 self.sess_uri)
        self._session = mock.Mock(spec=requests.Session)
        self.sess_auth.set_context(self.root, self.conn)
        self.sess_auth.refresh_session()
        self.assertEqual(self.sess_uri,
                         self.sess_auth.get_session_resource_id())
        self.assertEqual(self.sess_key,
                         self.sess_auth.get_session_key())
        self.conn.set_http_session_auth.assert_called_once_with(self.sess_key)

    def test_close_do_nothing(self):
        self.sess_auth._session_key = None
        self.sess_auth.set_context(self.root, self.conn)
        self.sess_auth.close()
        self.conn.delete.assert_not_called()

    def test_close(self):
        self.sess_auth._session_key = self.sess_key
        self.sess_auth._session_resource_id = self.sess_uri
        self.sess_auth.set_context(self.root, self.conn)
        self.sess_auth.close()
        self.conn.delete.assert_called_once_with(self.sess_uri)
        self.assertIsNone(self.sess_auth.get_session_resource_id())
        self.assertIsNone(self.sess_auth.get_session_key())

    @mock.patch.object(auth, 'LOG', autospec=True)
    def test_close_fail(self, mock_LOG):
        self.sess_auth._session_key = self.sess_key
        self.sess_auth._session_resource_id = self.sess_uri
        self.conn.delete.side_effect = (
            exceptions.ServerSideError(
                'DELETE', 'any_url', mock.MagicMock()))

        self.sess_auth.set_context(self.root, self.conn)
        self.sess_auth.close()

        self.assertTrue(mock_LOG.warning.called)
        self.assertIsNone(self.sess_auth.get_session_resource_id())
        self.assertIsNone(self.sess_auth.get_session_key())

    @mock.patch.object(auth.SessionAuth, 'close', autospec=True)
    def test_context_manager(self, auth_close):
        with auth.SessionAuth(self.username, self.password) as session_auth:
            self.assertEqual(self.username, session_auth._username)
            self.assertEqual(self.password, session_auth._password)
        auth_close.assert_called_once_with(session_auth)


class SessionOrBasicAuthTestCase(base.TestCase):

    @mock.patch.object(main, 'Sushy', autospec=True)
    @mock.patch.object(connector, 'Connector', autospec=True)
    def setUp(self, mock_connector, mock_root):
        super(SessionOrBasicAuthTestCase, self).setUp()
        self.username = 'TestUsername'
        self.password = 'TestP@$$W0RD'
        self.sess_key = 'TestingKey'
        self.sess_uri = ('https://testing:8000/redfish/v1/'
                         'SessionService/Sessions/testing')
        self.conn = mock_connector.return_value
        self.conn._session = mock.Mock(spec=requests.Session)
        self.conn._session.headers = {}
        self.conn._session.auth = None
        self.root = mock_root.return_value

        self.sess_basic_auth = auth.SessionOrBasicAuth(self.username,
                                                       self.password)

    def test_init(self):
        self.assertEqual(self.username,
                         self.sess_basic_auth._username)
        self.assertEqual(self.password,
                         self.sess_basic_auth._password)
        self.assertIsNone(self.sess_basic_auth._root_resource)
        self.assertIsNone(self.sess_basic_auth._connector)
        self.assertIsNone(self.sess_basic_auth._session_key)
        self.assertIsNone(self.sess_basic_auth._session_resource_id)

    def test_get_session_key(self):
        self.sess_basic_auth._session_key = self.sess_key
        self.assertEqual(self.sess_key,
                         self.sess_basic_auth.get_session_key())

    def test_get_session_resource_id(self):
        self.sess_basic_auth._session_resource_id = self.sess_uri
        self.assertEqual(self.sess_uri,
                         self.sess_basic_auth.get_session_resource_id())

    def test_reset_session_attrs(self):
        self.sess_basic_auth.set_context(self.root, self.conn)
        self.sess_basic_auth._session_key = self.sess_key
        self.sess_basic_auth._session_resource_id = self.sess_uri
        self.conn._session.auth = 'meow'
        self.conn._session.headers = {'X-Auth-Token': 'meow'}
        self.assertEqual(self.sess_uri,
                         self.sess_basic_auth.get_session_resource_id())
        self.assertEqual(self.sess_key,
                         self.sess_basic_auth.get_session_key())
        self.sess_basic_auth.reset_session_attrs()
        self.assertIsNone(self.sess_basic_auth.get_session_resource_id())
        self.assertIsNone(self.sess_basic_auth.get_session_key())
        self.assertNotIn('X-Auth-Token', self.conn._session.headers)
        self.assertIsNone(self.conn._session.auth)

    def test_set_context(self):
        self.sess_basic_auth.set_context(self.root, self.conn)
        self.assertEqual(self.sess_basic_auth._root_resource,
                         self.root)
        self.assertEqual(self.sess_basic_auth._connector,
                         self.conn)

    def test__do_authenticate_no_context(self):
        self.assertRaises(RuntimeError,
                          self.sess_basic_auth.authenticate)

    def test__do_authenticate(self):
        self.assertIsNone(self.sess_basic_auth.get_session_resource_id())
        self.assertIsNone(self.sess_basic_auth.get_session_key())
        self.root.create_session.return_value = (self.sess_key,
                                                 self.sess_uri)
        self.sess_basic_auth.set_context(self.root, self.conn)
        self.sess_basic_auth.authenticate()
        self.assertEqual(self.sess_uri,
                         self.sess_basic_auth.get_session_resource_id())
        self.assertEqual(self.sess_key,
                         self.sess_basic_auth.get_session_key())
        self.conn.set_http_session_auth.assert_called_once_with(self.sess_key)

    def test__do_authenticate_for_basic_auth(self):
        self.assertIsNone(self.sess_basic_auth.get_session_resource_id())
        self.assertIsNone(self.sess_basic_auth.get_session_key())
        self.root.create_session.side_effect = exceptions.SushyError
        self.sess_basic_auth.set_context(self.root, self.conn)
        self.sess_basic_auth.authenticate()

        self.assertIsNone(self.sess_basic_auth.get_session_resource_id())
        self.assertIsNone(self.sess_basic_auth.get_session_key())
        self.conn.set_http_basic_auth.assert_called_once_with(
            self.username, self.password)

    def test_can_refresh_session(self):
        self.root.create_session.return_value = (self.sess_key,
                                                 self.sess_uri)
        self.sess_basic_auth.set_context(self.root, self.conn)
        self.sess_basic_auth.authenticate()

        self.assertTrue(self.sess_basic_auth.can_refresh_session())

    def test_refresh_no_previous_session(self):
        self.assertIsNone(self.sess_basic_auth.get_session_resource_id())
        self.assertIsNone(self.sess_basic_auth.get_session_key())
        self.sess_basic_auth.set_context(self.root, self.conn)
        self.sess_basic_auth.refresh_session()
        self.assertIsNone(self.sess_basic_auth.get_session_resource_id())
        self.assertIsNone(self.sess_basic_auth.get_session_key())
        self.conn.set_http_session_auth.assert_not_called()
        self.conn.set_http_basic_auth.assert_not_called()

    def test_refresh_previous_session_exists(self):
        self.sess_basic_auth._session_key = 'ThisisFirstKey'
        test_url = ('https://testing:8000/redfish/v1/SessionService'
                    '/Sessions/testingfirst')
        self.sess_basic_auth._session_resource_id = test_url
        self.root.create_session.return_value = (self.sess_key,
                                                 self.sess_uri)
        self.sess_basic_auth.set_context(self.root, self.conn)
        self.sess_basic_auth.refresh_session()
        self.assertEqual(self.sess_uri,
                         self.sess_basic_auth.get_session_resource_id())
        self.assertEqual(self.sess_key,
                         self.sess_basic_auth.get_session_key())
        self.conn.set_http_session_auth.assert_called_once_with(self.sess_key)

    @mock.patch.object(auth.SessionOrBasicAuth,
                       '_fallback_to_basic_authentication',
                       autospec=True)
    def test_refresh_refresh_connection_error(self, mock_activate_basic_auth):
        self.sess_basic_auth._session_key = 'ThisisFirstKey'
        test_url = ('https://testing:8000/redfish/v1/SessionService'
                    '/Sessions/testingfirst')
        self.sess_basic_auth._session_auth_previously_successful = True
        self.sess_basic_auth._session_resource_id = test_url
        self.root.create_session.side_effect = \
            exceptions.ConnectionError('meow')
        self.sess_basic_auth.set_context(self.root, self.conn)
        self.assertRaises(exceptions.ConnectionError,
                          self.sess_basic_auth.refresh_session)
        self.assertIsNone(self.sess_basic_auth.get_session_resource_id())
        self.assertIsNone(self.sess_basic_auth.get_session_key())
        self.conn.set_http_session_auth.assert_not_called()
        self.assertIsNone(self.sess_basic_auth.basic_auth._root_resource)
        self.assertIsNone(self.sess_basic_auth.basic_auth._connector)
        self.assertFalse(mock_activate_basic_auth.called)

    @mock.patch.object(auth.SessionOrBasicAuth,
                       '_fallback_to_basic_authentication',
                       autospec=True)
    def test_refresh_refresh_connection_error_clears(
            self, mock_activate_basic_auth):
        self.sess_basic_auth._session_key = 'ThisisFirstKey'
        test_url = ('https://testing:8000/redfish/v1/SessionService'
                    '/Sessions/testingfirst')
        self.sess_basic_auth._session_auth_previously_successful = True
        self.sess_basic_auth._session_resource_id = test_url
        self.root.create_session.side_effect = [
            exceptions.ConnectionError('meow'),
            (self.sess_key, self.sess_uri)
        ]
        self.sess_basic_auth.set_context(self.root, self.conn)
        self.assertRaises(exceptions.ConnectionError,
                          self.sess_basic_auth.refresh_session)
        self.assertIsNone(self.sess_basic_auth.get_session_resource_id())
        self.assertIsNone(self.sess_basic_auth.get_session_key())
        self.conn.set_http_session_auth.assert_not_called()
        self.assertIsNone(self.sess_basic_auth.basic_auth._root_resource)
        self.assertIsNone(self.sess_basic_auth.basic_auth._connector)
        self.assertFalse(mock_activate_basic_auth.called)
        # Refresh no longer works, explicit authentication is now required.
        self.sess_basic_auth.refresh_session()
        self.conn.set_http_session_auth.assert_not_called()

        self.sess_basic_auth.authenticate()
        self.conn.set_http_session_auth.assert_called_once_with(self.sess_key)

    @mock.patch.object(auth.SessionOrBasicAuth,
                       '_fallback_to_basic_authentication',
                       autospec=True)
    def test_authenticate_session_fails(self, mock_activate_basic_auth):
        self.sess_basic_auth._session_key = None
        self.sess_basic_auth._session_auth_previously_successful = False
        test_url = ('https://testing:8000/redfish/v1/SessionService'
                    '/Sessions/testingfirst')
        self.sess_basic_auth._session_resource_id = test_url
        ae_exc = exceptions.AccessError(
            'GET', 'any_url', mock.MagicMock())

        self.root.create_session.side_effect = ae_exc
        self.sess_basic_auth.set_context(self.root, self.conn)
        self.sess_basic_auth.authenticate()
        # We fall back to basic auth as we failed to authenticate.
        self.assertTrue(mock_activate_basic_auth.called)

    @mock.patch.object(auth, 'LOG', autospec=True)
    @mock.patch.object(auth.SessionOrBasicAuth,
                       '_fallback_to_basic_authentication',
                       autospec=True)
    def test_authenticate_session_fails_reauth_raises_exception(
            self, mock_activate_basic_auth, mock_log):
        self.sess_basic_auth._session_key = None
        self.sess_basic_auth._session_auth_previously_successful = True
        test_url = ('https://testing:8000/redfish/v1/SessionService'
                    '/Sessions/testingfirst')
        self.sess_basic_auth._session_resource_id = test_url
        ae_exc = exceptions.AccessError(
            'GET', 'any_url', mock.MagicMock())

        self.root.create_session.side_effect = ae_exc
        self.sess_basic_auth.set_context(self.root, self.conn)
        self.assertRaises(exceptions.AccessError,
                          self.sess_basic_auth.authenticate)
        self.assertTrue(mock_log.debug.called)
        # We do not fallback to basic auth if we have already been
        # authenticated.
        self.assertFalse(mock_activate_basic_auth.called)

    @mock.patch.object(auth.SessionOrBasicAuth,
                       '_fallback_to_basic_authentication',
                       autospec=True)
    def test_authenticate_session_fails_connection_error(
            self, mock_activate_basic_auth):
        self.sess_basic_auth._session_key = None
        self.sess_basic_auth._session_auth_previously_successful = False
        test_url = ('https://testing:8000/redfish/v1/SessionService'
                    '/Sessions/testingfirst')
        self.sess_basic_auth._session_resource_id = test_url
        mock_sess_serv = mock.Mock()

        ae_exc = exceptions.ConnectionError('boo')

        self.root.create_session.side_effect = ae_exc
        self.root.get_session_service.return_value = mock_sess_serv
        self.sess_basic_auth.set_context(self.root, self.conn)
        self.assertRaises(exceptions.ConnectionError,
                          self.sess_basic_auth.authenticate)
        # We don't fall back to basic auth if we've never connected
        # before
        self.assertFalse(mock_activate_basic_auth.called)

    def test_close_do_nothing(self):
        self.conn.delete.assert_not_called()

    def test_close(self):
        self.sess_basic_auth._session_key = self.sess_key
        self.sess_basic_auth._session_resource_id = self.sess_uri
        self.sess_basic_auth.set_context(self.root, self.conn)
        self.sess_basic_auth.close()
        self.conn.delete.assert_called_once_with(self.sess_uri)
        self.assertIsNone(self.sess_basic_auth.get_session_resource_id())
        self.assertIsNone(self.sess_basic_auth.get_session_key())

    @mock.patch.object(auth.SessionOrBasicAuth, 'close', autospec=True)
    def test_context_manager(self, auth_close):
        with auth.SessionOrBasicAuth(
                self.username, self.password) as session_or_base_auth:
            self.assertEqual(self.username, session_or_base_auth._username)
            self.assertEqual(self.password, session_or_base_auth._password)
        auth_close.assert_called_once_with(session_or_base_auth)
