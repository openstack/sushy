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

from sushy.oem.dell.resources.manager import constants as mgr_cons
from sushy.oem.dell.resources.manager import idrac_card_service


class DelliDRACCardServiceTestCase(BaseTestCase):

    def setUp(self):
        super().setUp()
        self.conn = mock.Mock()
        with open('sushy/tests/oem/dell/unit/json_samples/'
                  'idrac_card_service.json') as f:
            mock_response = self.conn.get.return_value
            mock_response.json.return_value = json.load(f)
            mock_response.status_code = 200

        mock_response = self.conn.post.return_value
        mock_response.status_code = 202
        mock_response.headers.get.return_value = '1'
        self.idrac_card_service = idrac_card_service.DelliDRACCardService(
            self.conn, '/redfish/v1/Dell/Managers/iDRAC.Embedded.1')

    def test_reset_idrac(self):
        self.idrac_card_service.reset_idrac()
        target_uri = ('/redfish/v1/Dell/Managers/iDRAC.Embedded.1'
                      '/DelliDRACCardService'
                      '/Actions/DelliDRACCardService.iDRACReset')
        self.conn.post.assert_called_once_with(target_uri,
                                               data={'Force': 'Graceful'})

    def test_get_allowed_reset_idrac_values(self):
        expected_values = {mgr_cons.ResetType.GRACEFUL,
                           mgr_cons.ResetType.FORCE}
        allowed_values = \
            self.idrac_card_service.get_allowed_reset_idrac_values()
        self.assertEqual(expected_values, allowed_values)

    def test_get_allowed_reset_idrac_values_not_provided_by_idrac(self):
        idrac_service_json = self.idrac_card_service.json
        base_property = '#DelliDRACCardService.iDRACReset'
        remove_property = 'Force@Redfish.AllowableValues'
        idrac_service_json['Actions'][base_property].pop(remove_property)
        expected_values = {mgr_cons.ResetType.GRACEFUL,
                           mgr_cons.ResetType.FORCE}
        allowed_values = \
            self.idrac_card_service.get_allowed_reset_idrac_values()
        self.assertEqual(expected_values, allowed_values)
