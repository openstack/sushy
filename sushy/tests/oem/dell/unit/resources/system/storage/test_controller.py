# Copyright (c) 2022 Dell Inc. or its subsidiaries.
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

from oslotest.base import BaseTestCase
import sushy
from sushy.resources.system.storage import controller as sushy_constroller

from sushy.oem.dell.resources.system.storage import constants as ctrl_cons
from sushy.oem.dell.resources.system.storage import controller as oem_ctrl


class ControllerTestCase(BaseTestCase):

    def setUp(self):
        super().setUp()
        self.conn = mock.Mock()

        with open('sushy/tests/oem/dell/unit/json_samples/'
                  'storage_controller.json') as f:
            mock_response = self.conn.get.return_value
            mock_response.json.return_value = json.load(f)
            mock_response.status_code = 200

            self.controller = sushy_constroller.StorageController(
                self.conn,
                '/redfish/v1/Systems/437XR1138R2/Storage/1/Controllers/1')
            self.oem_controller = oem_ctrl.DellStorageControllerExtension(
                self.conn,
                '/redfish/v1/Systems/437XR1138R2/Storage/1/Controllers/1')
            self.oem_controller = self.oem_controller.set_parent_resource(
                self.controller, 'Dell')

    def test_parse_attributes(self):
        self.assertEqual(
            ctrl_cons.ControllerMode.EHBA,
            self.oem_controller.dell_storage_controller.controller_mode)

    def test_convert_to_raid(self):
        mock_controller = mock.Mock()
        mock_task_monitor = mock.Mock()
        mock_controller.update.return_value = mock_task_monitor
        self.oem_controller._parent_resource = mock_controller

        res = self.oem_controller.convert_to_raid()

        self.assertEqual(mock_task_monitor, res)
        patch = {"Oem": {"Dell": {"DellStorageController": {
                 "ControllerMode": "RAID"}}}}
        mock_controller.update.assert_called_once_with(
            patch, apply_time=sushy.ApplyTime.ON_RESET)

    def test_convert_to_raid_already_raid(self):
        mock_controller = mock.Mock()
        self.oem_controller._parent_resource = mock_controller
        json = self.oem_controller.json
        json['Oem']['Dell']['DellStorageController']['ControllerMode'] = 'RAID'
        self.oem_controller.refresh()

        res = self.oem_controller.convert_to_raid()

        self.assertIsNone(res)
        mock_controller.update.assert_not_called()
