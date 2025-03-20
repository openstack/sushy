# Copyright (c) 2020-2021 Dell Inc. or its subsidiaries.
#
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

from oslotest.base import BaseTestCase

from sushy.oem.dell.resources.manager import lifecycle_service


class DellLCServiceTestCase(BaseTestCase):

    def setUp(self):
        super().setUp()
        self.conn = mock.Mock()
        with open('sushy/tests/oem/dell/unit/json_samples/'
                  'lifecycle_service.json') as f:
            mock_response = self.conn.get.return_value
            mock_response.json.return_value = json.load(f)
            mock_response.status_code = 200

        mock_response = self.conn.post.return_value
        mock_response.status_code = 202
        mock_response.headers.get.return_value = '1'
        self.lifecycle_service = lifecycle_service.DellLCService(
            self.conn,
            '/redfish/v1/Dell/Managers/iDRAC.Embedded.1/DellLCService')

    def test_is_idrac_ready_true(self):
        mock_response = self.conn.post.return_value
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "LCStatus": "Ready",
            "RTStatus": "Ready",
            "ServerStatus": "OutOfPOST",
            "Status": "Ready"
            }
        target_uri = ('/redfish/v1/Dell/Managers/iDRAC.Embedded.1'
                      '/DellLCService'
                      '/Actions/DellLCService.GetRemoteServicesAPIStatus')
        idrac_ready_response = self.lifecycle_service.is_idrac_ready()
        self.conn.post.assert_called_once_with(target_uri, data={})
        self.assertTrue(idrac_ready_response)

    def test_is_idrac_ready_false(self):
        mock_response = self.conn.post.return_value
        mock_response.status_code = 202
        mock_response.json.return_value = {
            "LCStatus": "NotReady",
            "RTStatus": "NotReady",
            "ServerStatus": "OutOfPOST",
            "Status": "NotReady"
            }
        target_uri = ('/redfish/v1/Dell/Managers/iDRAC.Embedded.1'
                      '/DellLCService'
                      '/Actions/DellLCService.GetRemoteServicesAPIStatus')
        idrac_ready_response = self.lifecycle_service.is_idrac_ready()
        self.conn.post.assert_called_once_with(target_uri, data={})
        self.assertFalse(idrac_ready_response)

    def test_is_realtime_ready_true(self):
        mock_response = self.conn.post.return_value
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "LCStatus": "Ready",
            "RTStatus": "Ready",
            "ServerStatus": "OutOfPOST",
            "Status": "Ready"
            }

        self.assertTrue(self.lifecycle_service.is_realtime_ready())
        target_uri = ('/redfish/v1/Dell/Managers/iDRAC.Embedded.1'
                      '/DellLCService'
                      '/Actions/DellLCService.GetRemoteServicesAPIStatus')
        self.conn.post.assert_called_once_with(target_uri, data={})

    def test_is_realtime_ready_false(self):
        mock_response = self.conn.post.return_value
        mock_response.status_code = 202
        mock_response.json.return_value = {
            "LCStatus": "Ready",
            "RTStatus": "NotReady",
            "ServerStatus": "OutOfPOST",
            "Status": "NotReady"
            }

        self.assertFalse(self.lifecycle_service.is_realtime_ready())
        target_uri = ('/redfish/v1/Dell/Managers/iDRAC.Embedded.1'
                      '/DellLCService'
                      '/Actions/DellLCService.GetRemoteServicesAPIStatus')
        self.conn.post.assert_called_once_with(target_uri, data={})
