# -*- coding: utf-8 -*-

# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

import json

import mock

import sushy
from sushy.resources.fabric import fabric
from sushy.tests.unit import base


class FabricTestCase(base.TestCase):

    def setUp(self):
        super(FabricTestCase, self).setUp()
        self.conn = mock.Mock()
        with open('sushy/tests/unit/json_samples/fabric.json') as f:
            self.conn.get.return_value.json.return_value = json.load(f)

        self.fabric = fabric.Fabric(self.conn, '/redfish/v1/Fabrics/SAS',
                                    redfish_version='1.0.3')

    def test__parse_attributes(self):
        # | WHEN |
        self.fabric._parse_attributes()
        # | THEN |
        self.assertEqual('1.0.3', self.fabric.redfish_version)
        self.assertEqual('SAS', self.fabric.identity)
        self.assertEqual('SAS Fabric', self.fabric.name)
        self.assertEqual('A SAS Fabric with redundant switches.',
                         self.fabric.description)
        self.assertEqual(sushy.FABRIC_TYPE_SAS,
                         self.fabric.fabric_type)
        self.assertEqual(sushy.STATE_ENABLED, self.fabric.status.state)
        self.assertEqual(sushy.HEALTH_OK, self.fabric.status.health)


class FabricCollectionTestCase(base.TestCase):

    def setUp(self):
        super(FabricCollectionTestCase, self).setUp()
        self.conn = mock.Mock()
        with open('sushy/tests/unit/json_samples/'
                  'fabric_collection.json') as f:
            self.conn.get.return_value.json.return_value = json.load(f)
        self.fabric = fabric.FabricCollection(
            self.conn, '/redfish/v1/Fabrics', redfish_version='1.0.3')

    @mock.patch.object(fabric, 'Fabric', autospec=True)
    def test_get_member(self, fabric_mock):
        self.fabric.get_member('/redfish/v1/Fabrics/SAS1')
        fabric_mock.assert_called_once_with(
            self.fabric._conn, '/redfish/v1/Fabrics/SAS1',
            redfish_version=self.fabric.redfish_version)

    @mock.patch.object(fabric, 'Fabric', autospec=True)
    def test_get_members(self, fabric_mock):
        members = self.fabric.get_members()
        calls = [
            mock.call(self.fabric._conn, '/redfish/v1/Fabrics/SAS1',
                      redfish_version=self.fabric.redfish_version),
            mock.call(self.fabric._conn, '/redfish/v1/Fabrics/SAS2',
                      redfish_version=self.fabric.redfish_version)
        ]
        fabric_mock.assert_has_calls(calls)
        self.assertIsInstance(members, list)
        self.assertEqual(2, len(members))
