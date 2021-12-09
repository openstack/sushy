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

import json
from unittest import mock


from sushy import exceptions
from sushy.resources.sessionservice import session
from sushy.resources.sessionservice import sessionservice
from sushy.tests.unit import base


class SessionServiceTestCase(base.TestCase):

    def setUp(self):
        super(SessionServiceTestCase, self).setUp()
        self.conn = mock.MagicMock()
        with open('sushy/tests/unit/json_samples/session_service.json') as f:
            self.json_doc = json.load(f)

        self.conn.get.return_value.json.return_value = self.json_doc

        self.sess_serv_inst = sessionservice.SessionService(
            self.conn, '/redfish/v1/SessionService',
            redfish_version='1.0.2')

    def test__init_throws_exception(self):
        self.conn.get.return_value.json.reset_mock()
        self.conn.get.return_value.json.side_effect = (
            exceptions.AccessError(
                'GET', 'any_url', mock.MagicMock()))
        # Previously sushy would just mask these, but now we raise
        # the access error to the user.
        self.assertRaises(exceptions.AccessError,
                          sessionservice.SessionService,
                          self.conn, '/redfish/v1/SessionService',
                          redfish_version='1.0.2')

    def test__parse_attributes(self):
        self.sess_serv_inst._parse_attributes(self.json_doc)
        exp_path = '/redfish/v1/SessionService'
        self.assertEqual('1.0.2', self.sess_serv_inst.redfish_version)
        self.assertEqual('SessionService', self.sess_serv_inst.identity)
        self.assertEqual('Session Service', self.sess_serv_inst.name)
        self.assertEqual(30, self.sess_serv_inst.session_timeout)
        self.assertEqual(exp_path, self.sess_serv_inst.path)

    def test__get_sessions_collection_path(self):
        self.sess_serv_inst.json.pop('Sessions')
        self.assertRaisesRegex(
            exceptions.MissingAttributeError, 'attribute Sessions',
            self.sess_serv_inst._get_sessions_collection_path)

    @mock.patch.object(session, 'SessionCollection', autospec=True)
    def test_session_collection(self, mock_sess_col):
        self.sess_serv_inst.sessions
        mock_sess_col.assert_called_once_with(
            self.sess_serv_inst._conn,
            '/redfish/v1/SessionService/Sessions',
            self.sess_serv_inst.redfish_version, None,
            self.sess_serv_inst.root)

    def test_create_session(self):
        with open('sushy/tests/unit/json_samples/'
                  'session_creation_headers.json') as f:
            self.conn.post.return_value.headers = json.load(f)

        session_key, session_uri = (
            self.sess_serv_inst.create_session('foo', 'secret'))
        self.assertEqual('adc530e2016a0ea98c76c087f0e4b76f', session_key)
        self.assertEqual(
            '/redfish/v1/SessionService/Sessions/151edd65d41c0b89',
            session_uri)

    def test_create_session_unknown_path(self):
        del self.sess_serv_inst.json['Sessions']
        with open('sushy/tests/unit/json_samples/'
                  'session_creation_headers.json') as f:
            self.conn.post.return_value.headers = json.load(f)

        session_key, session_uri = (
            self.sess_serv_inst.create_session('foo', 'secret'))
        self.assertEqual('adc530e2016a0ea98c76c087f0e4b76f', session_key)
        self.assertEqual(
            '/redfish/v1/SessionService/Sessions/151edd65d41c0b89',
            session_uri)
        uri = self.sess_serv_inst.path + '/Sessions'
        data = {'UserName': 'foo', 'Password': 'secret'}
        self.conn.post.assert_called_once_with(uri,
                                               data=data)

    def test_create_session_missing_x_auth_token(self):
        with open('sushy/tests/unit/json_samples/'
                  'session_creation_headers.json') as f:
            self.conn.post.return_value.headers = json.load(f)

        self.conn.post.return_value.headers.pop('X-Auth-Token')
        self.assertRaisesRegex(
            exceptions.MissingXAuthToken, 'No X-Auth-Token returned',
            self.sess_serv_inst.create_session, 'foo', 'bar')

    @mock.patch.object(sessionservice, 'LOG', autospec=True)
    def test_create_session_missing_location(self, mock_LOG):
        with open('sushy/tests/unit/json_samples/'
                  'session_creation_headers.json') as f:
            self.conn.post.return_value.headers = json.load(f)

        self.conn.post.return_value.headers.pop('Location')
        self.sess_serv_inst.create_session('foo', 'bar')
        self.assertTrue(mock_LOG.warning.called)

    def _setUp_sessions(self):
        self.conn.get.return_value.json.reset_mock()
        successive_return_values = []
        with open('sushy/tests/unit/json_samples/session.json') as f:
            successive_return_values.append(json.load(f))
        self.conn.get.return_value.json.side_effect = successive_return_values

    def test_sessions(self):
        # | GIVEN |
        self._setUp_sessions()
        # | WHEN |
        actual_sessions = self.sess_serv_inst.sessions
        # | THEN |
        self.assertIsInstance(actual_sessions, session.SessionCollection)
        self.conn.get.return_value.json.assert_called_once_with()

        # reset mock
        self.conn.get.return_value.json.reset_mock()

        # | WHEN & THEN |
        # tests for same object on invoking subsequently
        self.assertIs(actual_sessions, self.sess_serv_inst.sessions)
        self.conn.get.return_value.json.assert_not_called()

    def test_sessions_on_refresh(self):
        # | GIVEN |
        self._setUp_sessions()
        # | WHEN & THEN |
        self.assertIsInstance(self.sess_serv_inst.sessions,
                              session.SessionCollection)

        self.conn.get.return_value.json.side_effect = None
        # On refreshing the sess_serv_inst instance...
        with open('sushy/tests/unit/json_samples/session.json') as f:
            self.conn.get.return_value.json.return_value = json.load(f)
        self.sess_serv_inst.refresh(force=True)

        # | WHEN & THEN |
        self.assertFalse(self.sess_serv_inst.sessions._is_stale)

    def test_close_session(self):
        self.sess_serv_inst.close_session('session/identity')
        self.conn.delete.assert_called_once_with('session/identity')
