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
from unittest import mock


import sushy
from sushy.resources.fabric import endpoint
from sushy.resources.fabric import fabric
from sushy.tests.unit import base


class FabricTestCase(base.TestCase):

    def setUp(self):
        super(FabricTestCase, self).setUp()
        self.conn = mock.Mock()
        with open('sushy/tests/unit/json_samples/fabric.json') as f:
            self.json_doc = json.load(f)

        self.conn.get.return_value.json.return_value = self.json_doc

        self.fabric = fabric.Fabric(self.conn, '/redfish/v1/Fabrics/SAS',
                                    redfish_version='1.0.3')

    def test__parse_attributes(self):
        # | WHEN |
        self.fabric._parse_attributes(self.json_doc)
        # | THEN |
        self.assertEqual('1.0.3', self.fabric.redfish_version)
        self.assertEqual('SAS', self.fabric.identity)
        self.assertEqual('SAS Fabric', self.fabric.name)
        self.assertEqual('A SAS Fabric with redundant switches.',
                         self.fabric.description)
        self.assertEqual(sushy.PROTOCOL_TYPE_SAS,
                         self.fabric.fabric_type)
        self.assertEqual(sushy.STATE_ENABLED, self.fabric.status.state)
        self.assertEqual(sushy.HEALTH_OK, self.fabric.status.health)

    def test_endpoints(self):
        # | GIVEN |
        with open('sushy/tests/unit/json_samples/'
                  'endpoint_collection.json') as f:
            endpoint_collection_return_value = json.load(f)

        with open('sushy/tests/unit/json_samples/'
                  'endpoint.json') as f:
            endpoint_return_value = json.load(f)

        self.conn.get.return_value.json.side_effect = [
            endpoint_collection_return_value, endpoint_return_value]

        # | WHEN |
        actual_endpoints = self.fabric.endpoints

        # | THEN |
        self.assertIsInstance(actual_endpoints,
                              endpoint.EndpointCollection)
        self.assertEqual(actual_endpoints.name, 'Endpoint Collection')

        member = actual_endpoints.get_member(
            '/redfish/v1/Fabrics/SAS/Endpoints/Drive1')

        self.assertEqual(member.name, "SAS Drive")
        self.assertEqual(member.endpoint_protocol, sushy.PROTOCOL_TYPE_SAS)

    def test_endpoints_on_refresh(self):
        # | GIVEN |
        with open('sushy/tests/unit/json_samples/'
                  'endpoint_collection.json') as f:
            self.conn.get.return_value.json.return_value = json.load(f)

        # | WHEN & THEN |
        endpts = self.fabric.endpoints
        self.assertIsInstance(endpts, endpoint.EndpointCollection)

        # On refreshing the fabric instance...
        with open('sushy/tests/unit/json_samples/fabric.json', 'r') as f:
            self.conn.get.return_value.json.return_value = json.loads(f.read())

        self.fabric.invalidate()
        self.fabric.refresh(force=False)

        # | WHEN & THEN |
        self.assertTrue(endpts._is_stale)

        # | GIVEN |
        with open('sushy/tests/unit/json_samples/'
                  'endpoint_collection.json') as f:
            self.conn.get.return_value.json.return_value = json.load(f)

        # | WHEN & THEN |
        self.assertIsInstance(self.fabric.endpoints,
                              endpoint.EndpointCollection)
        self.assertFalse(endpts._is_stale)


class FabricCollectionTestCase(base.TestCase):

    def setUp(self):
        super(FabricCollectionTestCase, self).setUp()
        self.conn = mock.Mock()
        with open('sushy/tests/unit/json_samples/'
                  'fabric_collection.json') as f:
            self.conn.get.return_value.json.return_value = json.load(f)
        self.fabric = fabric.FabricCollection(
            self.conn, '/redfish/v1/Fabrics', '1.0.3', None)

    @mock.patch.object(fabric, 'Fabric', autospec=True)
    def test_get_member(self, fabric_mock):
        self.fabric.get_member('/redfish/v1/Fabrics/SAS1')
        fabric_mock.assert_called_once_with(
            self.fabric._conn, '/redfish/v1/Fabrics/SAS1',
            self.fabric.redfish_version, None)

    @mock.patch.object(fabric, 'Fabric', autospec=True)
    def test_get_members(self, fabric_mock):
        members = self.fabric.get_members()
        calls = [
            mock.call(self.fabric._conn, '/redfish/v1/Fabrics/SAS1',
                      self.fabric.redfish_version, None),
            mock.call(self.fabric._conn, '/redfish/v1/Fabrics/SAS2',
                      self.fabric.redfish_version, None)
        ]
        fabric_mock.assert_has_calls(calls)
        self.assertIsInstance(members, list)
        self.assertEqual(2, len(members))
