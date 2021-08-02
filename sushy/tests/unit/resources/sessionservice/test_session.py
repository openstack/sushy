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
from sushy.tests.unit import base


class SessionTestCase(base.TestCase):

    def setUp(self):
        super(SessionTestCase, self).setUp()
        self.conn = mock.Mock()
        self.auth = mock.Mock()
        with open('sushy/tests/unit/json_samples/session.json') as f:
            self.json_doc = json.load(f)
            self.conn.get.return_value.json.return_value = self.json_doc
            self.auth._session_key = 'fake_x_auth_token'
            self.auth._session_uri = self.json_doc['@odata.id']
            self.conn._auth = self.auth

        self.sess_inst = session.Session(
            self.conn, '/redfish/v1/SessionService/Sessions/1234567890ABCDEF',
            redfish_version='1.0.2')

    def test__parse_attributes(self):
        self.sess_inst._parse_attributes(self.json_doc)
        self.assertEqual('1.0.2', self.sess_inst.redfish_version)
        self.assertEqual('1234567890ABCDEF', self.sess_inst.identity)
        self.assertEqual('User Session', self.sess_inst.name)
        exp_path = '/redfish/v1/SessionService/Sessions/1234567890ABCDEF'
        self.assertEqual(exp_path, self.sess_inst.path)

    def test__parse_attributes_missing_identity(self):
        self.sess_inst.json.pop('Id')
        self.assertRaisesRegex(
            exceptions.MissingAttributeError, 'attribute Id',
            self.sess_inst._parse_attributes, self.json_doc)

    def test_session_close(self):
        session_key = self.sess_inst._conn._auth._session_key
        session_uri = self.sess_inst._conn._auth._session_uri
        self.assertEqual(session_key, 'fake_x_auth_token')
        self.assertEqual(session_uri, self.sess_inst.path)
        self.sess_inst.delete()
        self.sess_inst._conn.delete.assert_called_with(session_uri)


class SessionCollectionTestCase(base.TestCase):

    def setUp(self):
        super(SessionCollectionTestCase, self).setUp()
        self.conn = mock.Mock()
        with open('sushy/tests/unit/json_samples/'
                  'session_collection.json') as f:
            self.json_doc = json.load(f)

        self.conn.get.return_value.json.return_value = self.json_doc

        self.sess_col = session.SessionCollection(
            self.conn, '/redfish/v1/SessionService/Sessions',
            redfish_version='1.0.2')

    def test__parse_attributes(self):
        path = '/redfish/v1/SessionService/Sessions/104f9d68f58abb85'
        self.sess_col._parse_attributes(self.json_doc)
        self.assertEqual('1.0.2', self.sess_col.redfish_version)
        self.assertEqual('Session Collection', self.sess_col.name)
        self.assertEqual((path,), self.sess_col.members_identities)

    @mock.patch.object(session, 'Session', autospec=True)
    def test_get_member(self, mock_session):
        path = '/redfish/v1/SessionService/Sessions/104f9d68f58abb85'
        self.sess_col.get_member(path)
        mock_session.assert_called_once_with(
            self.sess_col._conn, path,
            redfish_version=self.sess_col.redfish_version, registries=None,
            root=self.sess_col.root)

    @mock.patch.object(session, 'Session', autospec=True)
    def test_get_members(self, mock_session):
        path = '/redfish/v1/SessionService/Sessions/104f9d68f58abb85'
        members = self.sess_col.get_members()
        mock_session.assert_called_once_with(
            self.sess_col._conn, path,
            redfish_version=self.sess_col.redfish_version, registries=None,
            root=self.sess_col.root)
        self.assertIsInstance(members, list)
        self.assertEqual(1, len(members))
