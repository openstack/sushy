# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import json
from unittest import mock

from sushy import exceptions
from sushy.resources import constants as res_cons
from sushy.resources.updateservice import softwareinventory
from sushy.tests.unit import base


class SoftwareInventoryTestCase(base.TestCase):

    def setUp(self):
        super(SoftwareInventoryTestCase, self).setUp()
        conn = mock.Mock()
        with open(
            'sushy/tests/unit/json_samples/softwareinventory.json') as f:
            self.json_doc = json.load(f)

        conn.get.return_value.json.return_value = self.json_doc

        self.soft_inv = softwareinventory.SoftwareInventory(
            conn,
            '/redfish/v1/UpdateService/SoftwareInventory/1',
            redfish_version='1.3.0')

    def test__parse_attributes(self):
        self.soft_inv._parse_attributes(self.json_doc)
        self.assertEqual('BMC', self.soft_inv.identity)
        self.assertEqual(
            '1.30.367a12-rev1',
            self.soft_inv.lowest_supported_version)
        self.assertEqual('Contoso', self.soft_inv.manufacturer)
        self.assertEqual('Contoso BMC Firmware', self.soft_inv.name)
        self.assertEqual('2017-08-22T12:00:00', self.soft_inv.release_date)
        self.assertEqual(
            res_cons.State.ENABLED,
            self.soft_inv.status.state)
        self.assertEqual(res_cons.Health.OK, self.soft_inv.status.health)
        self.assertEqual(
            '1624A9DF-5E13-47FC-874A-DF3AFF143089',
            self.soft_inv.software_id)
        self.assertTrue(self.soft_inv.updateable)
        self.assertEqual('1.45.455b66-rev4', self.soft_inv.version)

    def test__parse_attributes_return(self):
        attributes = self.soft_inv._parse_attributes(self.json_doc)

        # Test that various types are returned correctly
        self.assertEqual('BMC', attributes.get('identity'))
        self.assertEqual({'health': res_cons.Health.OK,
                          'health_rollup': None,
                          'state': res_cons.State.ENABLED},
                         attributes.get('status'))
        self.assertEqual(True, attributes.get('updateable'))

    def test__parse_attributes_missing_identity(self):
        self.soft_inv.json.pop('Id')
        self.assertRaisesRegex(
            exceptions.MissingAttributeError, 'attribute Id',
            self.soft_inv._parse_attributes, self.json_doc)


class SoftwareInventoryCollectionTestCase(base.TestCase):

    def setUp(self):
        super(SoftwareInventoryCollectionTestCase, self).setUp()
        conn = mock.Mock()
        with open('sushy/tests/unit/json_samples/'
                  'firmwareinventory_collection.json') as f:
            self.json_doc = json.load(f)

        conn.get.return_value.json.return_value = self.json_doc

        self.soft_inv_col = softwareinventory.SoftwareInventoryCollection(
            conn, '/redfish/v1/UpdateService/FirmwareInventory',
            redfish_version='1.3.0')

    def test__parse_attributes(self):
        self.soft_inv_col._parse_attributes(self.json_doc)
        self.assertEqual('1.3.0', self.soft_inv_col.redfish_version)
        self.assertEqual(
            'Firmware Inventory Collection',
            self.soft_inv_col.name)

    @mock.patch.object(
        softwareinventory, 'SoftwareInventory', autospec=True)
    def test_get_member(self, mock_softwareinventory):
        path = ('/redfish/v1/UpdateService/FirmwareInventory/'
                'Current-102303-19.0.12')
        self.soft_inv_col.get_member(path)
        mock_softwareinventory.assert_called_once_with(
            self.soft_inv_col._conn, path,
            self.soft_inv_col.redfish_version, None, self.soft_inv_col.root)

    @mock.patch.object(
        softwareinventory, 'SoftwareInventory', autospec=True)
    def test_get_members(self, mock_softwareinventory):
        members = self.soft_inv_col.get_members()
        calls = [
            mock.call(self.soft_inv_col._conn,
                      ('/redfish/v1/UpdateService/FirmwareInventory/'
                       'Current-101560-25.5.6.0009'),
                      redfish_version=self.soft_inv_col.redfish_version,
                      registries=None,
                      root=self.soft_inv_col.root),

            mock.call(self.soft_inv_col._conn,
                      ('/redfish/v1/UpdateService/FirmwareInventory/'
                       'Installed-101560-25.5.6.0009'),
                      redfish_version=self.soft_inv_col.redfish_version,
                      registries=None,
                      root=self.soft_inv_col.root),

            mock.call(self.soft_inv_col._conn,
                      ('/redfish/v1/UpdateService/FirmwareInventory/'
                       'Previous-102302-18.8.9'),
                      redfish_version=self.soft_inv_col.redfish_version,
                      registries=None,
                      root=self.soft_inv_col.root)
        ]
        mock_softwareinventory.assert_has_calls(calls)
        self.assertIsInstance(members, list)
        self.assertEqual(3, len(members))
