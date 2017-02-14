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

from sushy import connector
from sushy import main
from sushy.resources.system import system
from sushy.tests.unit import base


class MainTestCase(base.TestCase):

    @mock.patch.object(connector, 'Connector', autospec=True)
    def setUp(self, mock_connector):
        super(MainTestCase, self).setUp()
        self.conn = mock.Mock()
        mock_connector.return_code = self.conn
        self.root = main.Sushy(
            'http://foo.bar:1234/redfish/v1', username='foo', password='bar',
            verify=True)
        mock_connector.assert_called_once_with(
            'http://foo.bar:1234/redfish/v1', 'foo', 'bar', True)

    def test__parse_attributes(self):
        with open('sushy/tests/unit/json_samples/root.json', 'r') as f:
            self.root._json = json.loads(f.read())
        self.root._parse_attributes()
        self.assertEqual('RootService', self.root.identity)
        self.assertEqual('Root Service', self.root.name)
        self.assertEqual('1.0.2', self.root.redfish_version)
        self.assertEqual('92384634-2938-2342-8820-489239905423',
                         self.root.uuid)

    @mock.patch.object(system, 'SystemCollection', autospec=True)
    def test_get_system_collection(self, mock_system_collection):
        self.root.get_system_collection()
        mock_system_collection.assert_called_once_with(
            self.root._conn, redfish_version=self.root.redfish_version)

    @mock.patch.object(system, 'System', autospec=True)
    def test_get_system(self, mock_system):
        self.root.get_system('fake-system-id')
        mock_system.assert_called_once_with(
            self.root._conn, 'fake-system-id',
            redfish_version=self.root.redfish_version)
