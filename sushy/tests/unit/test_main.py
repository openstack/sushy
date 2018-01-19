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

import mock

from sushy import auth
from sushy import connector
from sushy import main
from sushy.resources.manager import manager
from sushy.resources.sessionservice import session
from sushy.resources.sessionservice import sessionservice
from sushy.resources.system import system
from sushy.tests.unit import base


class MainTestCase(base.TestCase):

    @mock.patch.object(auth, 'SessionOrBasicAuth', autospec=True)
    @mock.patch.object(connector, 'Connector', autospec=True)
    @mock.patch.object(sessionservice, 'SessionService', autospec=True)
    def setUp(self, mock_session_service, mock_connector, mock_auth):
        super(MainTestCase, self).setUp()
        self.conn = mock.Mock()
        self.sess_serv = mock.Mock()
        self.sess_serv.create_session.return_value = (None, None)
        mock_session_service.return_value = self.sess_serv
        mock_connector.return_value = self.conn
        with open('sushy/tests/unit/json_samples/root.json', 'r') as f:
            self.conn.get.return_value.json.return_value = json.loads(f.read())
        self.root = main.Sushy('http://foo.bar:1234',
                               verify=True, auth=mock_auth)
        mock_connector.assert_called_once_with(
            'http://foo.bar:1234', verify=True)

    def test__parse_attributes(self):
        self.root._parse_attributes()
        self.assertEqual('RootService', self.root.identity)
        self.assertEqual('Root Service', self.root.name)
        self.assertEqual('1.0.2', self.root.redfish_version)
        self.assertEqual('92384634-2938-2342-8820-489239905423',
                         self.root.uuid)
        self.assertEqual('/redfish/v1/Systems', self.root._systems_path)
        self.assertEqual('/redfish/v1/Managers', self.root._managers_path)
        self.assertEqual('/redfish/v1/SessionService',
                         self.root._session_service_path)

    @mock.patch.object(connector, 'Connector', autospec=True)
    def test__init_throws_exception(self, mock_Connector):
        self.assertRaises(
            ValueError, main.Sushy, 'http://foo.bar:1234',
            'foo', 'bar', auth=mock.MagicMock())

    @mock.patch.object(connector, 'Connector', autospec=True)
    def test_custom_connector(self, mock_Sushy_Connector):
        connector_mock = mock.MagicMock()
        with open('sushy/tests/unit/json_samples/root.json', 'r') as f:
            connector_mock.get.return_value.json.return_value = (
                json.loads(f.read()))
        main.Sushy('http://foo.bar:1234', 'foo', 'bar',
                   connector=connector_mock)
        self.assertTrue(connector_mock.post.called)
        self.assertTrue(connector_mock.get.called)
        self.assertFalse(mock_Sushy_Connector.called)

    @mock.patch.object(system, 'SystemCollection', autospec=True)
    def test_get_system_collection(self, mock_system_collection):
        self.root.get_system_collection()
        mock_system_collection.assert_called_once_with(
            self.root._conn, '/redfish/v1/Systems',
            redfish_version=self.root.redfish_version)

    @mock.patch.object(system, 'System', autospec=True)
    def test_get_system(self, mock_system):
        self.root.get_system('fake-system-id')
        mock_system.assert_called_once_with(
            self.root._conn, 'fake-system-id',
            redfish_version=self.root.redfish_version)

    @mock.patch.object(manager, 'ManagerCollection', autospec=True)
    def test_get_manager_collection(self, ManagerCollection_mock):
        self.root.get_manager_collection()
        ManagerCollection_mock.assert_called_once_with(
            self.root._conn, '/redfish/v1/Managers',
            redfish_version=self.root.redfish_version)

    @mock.patch.object(manager, 'Manager', autospec=True)
    def test_get_manager(self, Manager_mock):
        self.root.get_manager('fake-manager-id')
        Manager_mock.assert_called_once_with(
            self.root._conn, 'fake-manager-id',
            redfish_version=self.root.redfish_version)

    @mock.patch.object(sessionservice, 'SessionService', autospec=True)
    def test_get_sessionservice(self, mock_sess_serv):
        self.root.get_session_service()
        mock_sess_serv.assert_called_once_with(
            self.root._conn, '/redfish/v1/SessionService',
            redfish_version=self.root.redfish_version)

    @mock.patch.object(session, 'Session', autospec=True)
    def test_get_session(self, mock_sess):
        self.root.get_session('asdf')
        mock_sess.assert_called_once_with(
            self.root._conn, 'asdf',
            redfish_version=self.root.redfish_version)
