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

from http import client as http_client
import json
from unittest import mock

import sushy
from sushy.resources.system.storage import controller
from sushy import taskmonitor
from sushy.tests.unit import base


class ControllerTestCase(base.TestCase):

    def setUp(self):
        super(ControllerTestCase, self).setUp()
        self.conn = mock.Mock()
        with open('sushy/tests/unit/json_samples/'
                  'storage_controller.json') as f:
            self.json_doc = json.load(f)
        with open('sushy/tests/unit/json_samples/'
                  'storage_controller_settings.json') as f:
            self.settings_json = json.load(f)

        self.conn.get.return_value.json.side_effect = [
            self.json_doc, self.settings_json]

        self.controller = controller.StorageController(
            self.conn,
            '/redfish/v1/Systems/437XR1138R2/Storage/1/Controllers/1',
            redfish_version='1.0.2')

    def test__parse_attributes(self):
        self.controller._parse_attributes(self.json_doc)
        self.assertEqual('1', self.controller.identity)
        self.assertEqual('Contoso Integrated RAID', self.controller.name)
        self.assertEqual(sushy.Health.OK, self.controller.status.health)
        self.assertEqual(sushy.State.ENABLED, self.controller.status.state)
        identifiers = self.controller.identifiers
        self.assertIsInstance(identifiers, list)
        self.assertEqual(1, len(identifiers))
        identifier = identifiers[0]
        self.assertEqual(sushy.DurableNameFormat.NAA,
                         identifier.durable_name_format)
        self.assertEqual('345C59DBD970859C', identifier.durable_name)
        self.assertEqual(12, self.controller.speed_gbps)
        self.assertEqual([sushy.Protocol.PCIe],
                         self.controller.controller_protocols)
        self.assertEqual([sushy.Protocol.SAS, sushy.Protocol.SATA],
                         self.controller.device_protocols)
        self.assertEqual([sushy.RAIDType.RAID0, sushy.RAIDType.RAID1],
                         self.controller.raid_types)
        self.assertEqual('1', self.controller.pending_settings.identity)
        self.assertEqual([sushy.ApplyTime.IMMEDIATE, sushy.ApplyTime.ON_RESET],
                         self.controller.supported_apply_times)

    def test_update(self):
        self.conn.get.return_value.json.side_effect = [
            self.json_doc, self.json_doc]
        mock_response = mock.Mock()
        mock_response.status_code = http_client.ACCEPTED
        mock_response.headers = {'Content-Length': 42,
                                 'Location': '/Task/545',
                                 'Retry-After': 20,
                                 'Allow': 'DELETE'}
        mock_response.content = None
        self.controller._conn.patch.return_value = mock_response
        tm = self.controller.update(
            {'ControllerRates': {'ConsistencyCheckRatePercent': 30}},
            apply_time=sushy.ApplyTime.ON_RESET)
        self.controller._conn.patch.assert_called_once_with(
            '/redfish/v1/Systems/437XR1138R2/Storage/1/Controllers/1/Settings',
            data={'ControllerRates': {'ConsistencyCheckRatePercent': 30},
                  '@Redfish.SettingsApplyTime': {
                      '@odata.type': '#Settings.v1_0_0.PreferredApplyTime',
                      'ApplyTime': 'OnReset'}},
            etag=None)
        self.assertIsInstance(tm, taskmonitor.TaskMonitor)
        self.assertEqual('/Task/545', tm.task_monitor_uri)


class ControllerCollectionTestCase(base.TestCase):

    def setUp(self):
        super(ControllerCollectionTestCase, self).setUp()
        self.conn = mock.Mock()
        with open('sushy/tests/unit/json_samples/'
                  'storage_controller_collection.json') as f:
            self.json_doc = json.load(f)

        with open('sushy/tests/unit/json_samples/'
                  'storage_controller.json') as f:
            self.json_doc_ctrl = json.load(f)

        self.conn.get.return_value.json.return_value = self.json_doc

        self.ctrl_col = controller.ControllerCollection(
            self.conn,
            '/redfish/v1/Systems/437XR1138R2/Storage/1/Controllers',
            redfish_version='1.0.2')

    def test__parse_attributes(self):
        self.ctrl_col._parse_attributes(self.json_doc)
        self.assertEqual((
            '/redfish/v1/Systems/437XR1138R2/Storage/1/Controllers/1',),
            self.ctrl_col.members_identities)

    @mock.patch.object(controller, 'StorageController', autospec=True)
    def test_get_member(self, mock_controller):
        self.ctrl_col.get_member(
            '/redfish/v1/Systems/437XR1138R2/Storage/1/Controllers/1')
        mock_controller.assert_called_once_with(
            self.ctrl_col._conn,
            '/redfish/v1/Systems/437XR1138R2/Storage/1/Controllers/1',
            redfish_version=self.ctrl_col.redfish_version, registries=None,
            root=self.ctrl_col.root)

    @mock.patch.object(controller, 'StorageController', autospec=True)
    def test_get_members(self, mock_controller):
        members = self.ctrl_col.get_members()
        mock_controller.assert_called_once_with(
            self.ctrl_col._conn,
            '/redfish/v1/Systems/437XR1138R2/Storage/1/Controllers/1',
            redfish_version=self.ctrl_col.redfish_version, registries=None,
            root=self.ctrl_col.root)
        self.assertIsInstance(members, list)
        self.assertEqual(1, len(members))

    def test_summary(self):
        self.conn.get.return_value.json.return_value = self.json_doc_ctrl
        self.assertEqual({'1': {'Health': sushy.Health.OK,
                                'State': sushy.State.ENABLED}},
                         self.ctrl_col.summary)
