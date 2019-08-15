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
import mock

from sushy import exceptions
from sushy.resources import constants as res_cons
from sushy.resources.updateservice import constants as ups_cons
from sushy.resources.updateservice import softwareinventory
from sushy.resources.updateservice import updateservice
from sushy.tests.unit import base


class UpdateServiceTestCase(base.TestCase):

    def setUp(self):
        super(UpdateServiceTestCase, self).setUp()
        self.conn = mock.Mock()
        with open('sushy/tests/unit/json_samples/updateservice.json') as f:
            self.json_doc = json.load(f)

        self.conn.get.return_value.json.return_value = self.json_doc

        self.upd_serv = updateservice.UpdateService(
            self.conn, '/redfish/v1/UpdateService/UpdateService',
            redfish_version='1.3.0')

    def test__parse_attributes(self):
        self.upd_serv._parse_attributes(self.json_doc)
        self.assertEqual('UpdateService', self.upd_serv.identity)
        self.assertEqual('/FWUpdate', self.upd_serv.http_push_uri)
        self.assertIn('/FWUpdate', self.upd_serv.http_push_uri_targets)
        self.assertFalse(self.upd_serv.http_push_uri_targets_busy)
        self.assertEqual('Update service', self.upd_serv.name)
        self.assertTrue(self.upd_serv.service_enabled)
        self.assertEqual(res_cons.STATE_ENABLED, self.upd_serv.status.state)
        self.assertEqual(res_cons.HEALTH_OK, self.upd_serv.status.health)
        self.assertEqual(
            res_cons.HEALTH_OK,
            self.upd_serv.status.health_rollup)

    def test__parse_attributes_missing_actions(self):
        self.upd_serv.json.pop('Actions')
        self.assertRaisesRegex(
            exceptions.MissingAttributeError, 'attribute Actions',
            self.upd_serv._parse_attributes, self.json_doc)

    def test_simple_update(self):
        self.upd_serv.simple_update(
            image_uri='local.server/update.exe',
            targets=['/redfish/v1/UpdateService/FirmwareInventory/BMC'],
            transfer_protocol=ups_cons.UPDATE_PROTOCOL_HTTPS)
        self.upd_serv._conn.post.assert_called_once_with(
            '/redfish/v1/UpdateService/Actions/SimpleUpdate',
            data={
                'ImageURI': 'local.server/update.exe',
                'Targets': ['/redfish/v1/UpdateService/FirmwareInventory/BMC'],
                'TransferProtocol': 'HTTPS'})

    def test_simple_update_backward_compatible_protocol(self):
        self.upd_serv.simple_update(
            image_uri='local.server/update.exe',
            targets='/redfish/v1/UpdateService/Actions/SimpleUpdate',
            transfer_protocol='HTTPS')
        self.upd_serv._conn.post.assert_called_once_with(
            '/redfish/v1/UpdateService/Actions/SimpleUpdate',
            data={
                'ImageURI': 'local.server/update.exe',
                'Targets': '/redfish/v1/UpdateService/Actions/SimpleUpdate',
                'TransferProtocol': 'HTTPS'})

    def test_simple_update_without_target(self):
        self.upd_serv.simple_update(
            image_uri='local.server/update.exe',
            transfer_protocol='HTTPS')
        self.upd_serv._conn.post.assert_called_once_with(
            '/redfish/v1/UpdateService/Actions/SimpleUpdate',
            data={
                'ImageURI': 'local.server/update.exe',
                'TransferProtocol': 'HTTPS'})

    def test_simple_update_bad_protocol(self):
        self.assertRaises(
            exceptions.InvalidParameterValueError,
            self.upd_serv.simple_update,
            image_uri='local.server/update.exe',
            targets='/redfish/v1/UpdateService/Actions/SimpleUpdate',
            transfer_protocol='ROYAL')

    def test_software_inventory(self):
        # | GIVEN |
        self.conn.get.return_value.json.reset_mock()
        with open('sushy/tests/unit/json_samples/'
                  'softwareinventory_collection.json') as f:
            self.conn.get.return_value.json.return_value = json.load(f)
        # | WHEN |
        actual_software_inventory = self.upd_serv.software_inventory
        # | THEN |
        self.assertIsInstance(actual_software_inventory,
                              softwareinventory.SoftwareInventoryCollection)
        self.conn.get.return_value.json.assert_called_once_with()

        # reset mock
        self.conn.get.return_value.json.reset_mock()
        # | WHEN & THEN |
        self.assertIs(actual_software_inventory,
                      self.upd_serv.software_inventory)
        self.conn.get.return_value.json.assert_not_called()

    def test_firmware_inventory(self):
        # | GIVEN |
        self.conn.get.return_value.json.reset_mock()
        with open('sushy/tests/unit/json_samples/'
                  'softwareinventory_collection.json') as f:
            self.conn.get.return_value.json.return_value = json.load(f)
        # | WHEN |
        actual_firmware_inventory = self.upd_serv.firmware_inventory
        # | THEN |
        self.assertIsInstance(actual_firmware_inventory,
                              softwareinventory.SoftwareInventoryCollection)
        self.conn.get.return_value.json.assert_called_once_with()

        # reset mock
        self.conn.get.return_value.json.reset_mock()
        # | WHEN & THEN |
        self.assertIs(actual_firmware_inventory,
                      self.upd_serv.firmware_inventory)
        self.conn.get.return_value.json.assert_not_called()
