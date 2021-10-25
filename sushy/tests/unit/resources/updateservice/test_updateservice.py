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
from sushy.resources.updateservice import constants as ups_cons
from sushy.resources.updateservice import softwareinventory
from sushy.resources.updateservice import updateservice
from sushy import taskmonitor
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
        self.assertEqual(res_cons.State.ENABLED, self.upd_serv.status.state)
        self.assertEqual(res_cons.Health.OK, self.upd_serv.status.health)
        self.assertEqual(
            res_cons.Health.OK,
            self.upd_serv.status.health_rollup)

    def test__parse_attributes_missing_actions(self):
        self.upd_serv.json.pop('Actions')
        self.assertRaisesRegex(
            exceptions.MissingAttributeError, 'attribute Actions',
            self.upd_serv._parse_attributes, self.json_doc)

    def test_simple_update(self):
        with open('sushy/tests/unit/json_samples/task_monitor.json') as f:
            task_json = json.load(f)
        task_submitted = mock.Mock()
        task_submitted.json.return_value = task_json
        task_submitted.status_code = 202
        task_submitted.headers = {'Content-Length': 42,
                                  'Location': '/Task/545'}
        self.conn.post.return_value = task_submitted

        tm = self.upd_serv.simple_update(
            image_uri='local.server/update.exe',
            targets=['/redfish/v1/UpdateService/FirmwareInventory/BMC'],
            transfer_protocol=ups_cons.UpdateTransferProtocolType.HTTPS)

        self.assertIsInstance(tm, taskmonitor.TaskMonitor)
        self.assertEqual('/Task/545', tm.task_monitor_uri)

        self.upd_serv._conn.post.assert_called_once_with(
            '/redfish/v1/UpdateService/Actions/SimpleUpdate',
            data={
                'ImageURI': 'local.server/update.exe',
                'Targets': ['/redfish/v1/UpdateService/FirmwareInventory/BMC'],
                'TransferProtocol': 'HTTPS'})

    def test_simple_update_task_uri(self):
        with open('sushy/tests/unit/json_samples/task.json') as f:
            task_json = json.load(f)
        task_submitted = mock.Mock()
        task_submitted.json.return_value = task_json
        task_submitted.status_code = 202
        task_submitted.headers = {'Content-Length': 42,
                                  'Location': '/Taskmonitor/545'}
        self.conn.post.return_value = task_submitted

        tm = self.upd_serv.simple_update(
            image_uri='local.server/update.exe',
            targets=['/redfish/v1/UpdateService/FirmwareInventory/BMC'],
            transfer_protocol=ups_cons.UpdateTransferProtocolType.HTTPS)

        self.assertIsInstance(tm, taskmonitor.TaskMonitor)
        self.assertEqual('/redfish/v1/TaskService/Tasks/545',
                         tm.task_monitor_uri)

        self.upd_serv._conn.post.assert_called_once_with(
            '/redfish/v1/UpdateService/Actions/SimpleUpdate',
            data={
                'ImageURI': 'local.server/update.exe',
                'Targets': ['/redfish/v1/UpdateService/FirmwareInventory/BMC'],
                'TransferProtocol': 'HTTPS'})

    def test_simple_update_missing_location(self):
        with open('sushy/tests/unit/json_samples/task_monitor.json') as f:
            task_json = json.load(f)
        task_submitted = mock.Mock()
        task_submitted.json.return_value = task_json
        task_submitted.status_code = 202
        task_submitted.headers = {'Allow': 'GET'}
        self.conn.post.return_value = task_submitted

        self.assertRaises(
            exceptions.MissingHeaderError,
            self.upd_serv.simple_update,
            image_uri='local.server/update.exe',
            targets='/redfish/v1/UpdateService/Actions/SimpleUpdate',
            transfer_protocol='HTTPS')

    def test_simple_update_backward_compatible_protocol(self):
        with open('sushy/tests/unit/json_samples/task.json') as f:
            task_json = json.load(f)
        task_submitted = mock.Mock()
        task_submitted.json.return_value = task_json
        task_submitted.status_code = 202
        task_submitted.headers = {'Content-Length': 42,
                                  'Location': '/Task/545'}
        self.conn.post.return_value = task_submitted

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
        with open('sushy/tests/unit/json_samples/task.json') as f:
            task_json = json.load(f)
        task_submitted = mock.Mock()
        task_submitted.json.return_value = task_json
        task_submitted.status_code = 202
        task_submitted.headers = {'Content-Length': 42,
                                  'Location': '/Task/545'}
        self.conn.post.return_value = task_submitted
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

    @mock.patch.object(softwareinventory, 'SoftwareInventoryCollection',
                       autospec=True)
    def test_software_inventory(self, software_inventory_collection_mock):
        self.upd_serv.software_inventory
        software_inventory_collection_mock.assert_called_once_with(
            self.conn, '/redfish/v1/UpdateService/SoftwareInventory',
            self.upd_serv.redfish_version,
            self.upd_serv._registries,
            self.upd_serv.root)

    @mock.patch.object(softwareinventory, 'SoftwareInventoryCollection',
                       autospec=True)
    def test_firmware_inventory(self, software_inventory_collection_mock):
        self.upd_serv.firmware_inventory
        software_inventory_collection_mock.assert_called_once_with(
            self.conn, '/redfish/v1/UpdateService/FirmwareInventory',
            self.upd_serv.redfish_version,
            self.upd_serv._registries, self.upd_serv.root)


class UpdateServiceNoInvTestCase(base.TestCase):

    def setUp(self):
        super(UpdateServiceNoInvTestCase, self).setUp()
        self.conn = mock.Mock()
        no_inv_json = 'sushy/tests/unit/json_samples/updateservice_no_inv.json'
        with open(no_inv_json) as f:
            self.json_doc = json.load(f)

        self.conn.get.return_value.json.return_value = self.json_doc

        self.upd_serv = updateservice.UpdateService(
            self.conn, '/redfish/v1/UpdateService/UpdateService',
            redfish_version='1.3.0')

    def test_software_inventory_when_sw_inv_absent(self):
        self.assertRaisesRegex(
            exceptions.MissingAttributeError,
            'SoftwareInventory/@odata.id',
            getattr, self.upd_serv, 'software_inventory')

    def test_firmware_inventory_when_fw_inv_absent(self):
        self.assertRaisesRegex(
            exceptions.MissingAttributeError,
            'FirmwareInventory/@odata.id',
            getattr, self.upd_serv, 'firmware_inventory')
