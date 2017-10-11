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

from sushy import exceptions
from sushy.resources.system import system
from sushy.tests.unit import base
from sushy import utils


class UtilsTestCase(base.TestCase):

    def test_revert_dictionary(self):
        source = {'key0': 'value0', 'key1': 'value1'}
        expected = {'value0': 'key0', 'value1': 'key1'}
        self.assertEqual(expected, utils.revert_dictionary(source))

    @mock.patch.object(utils.LOG, 'warning', autospec=True)
    def test_get_members_identities(self, log_mock):
        members = [{"@odata.id": "/redfish/v1/Systems/FOO"},
                   {"other_key": "/redfish/v1/Systems/FUN"},
                   {"@odata.id": "/redfish/v1/Systems/BAR/"}]
        expected = ('/redfish/v1/Systems/FOO', '/redfish/v1/Systems/BAR')
        self.assertEqual(expected, utils.get_members_identities(members))
        self.assertEqual(1, log_mock.call_count)

    def test_int_or_none(self):
        self.assertEqual(1, utils.int_or_none('1'))
        self.assertIsNone(None, utils.int_or_none(None))

    def setUp(self):
        super(UtilsTestCase, self).setUp()
        self.conn = mock.MagicMock()
        with open('sushy/tests/unit/json_samples/system.json', 'r') as f:
            system_json = json.loads(f.read())
        self.conn.get.return_value.json.return_value = system_json

        self.sys_inst = system.System(self.conn,
                                      '/redfish/v1/Systems/437XR1138R2',
                                      redfish_version='1.0.2')

    def test_get_sub_resource_path_by(self):
        subresource_path = 'EthernetInterfaces'
        expected_result = '/redfish/v1/Systems/437XR1138R2/EthernetInterfaces'
        value = utils.get_sub_resource_path_by(self.sys_inst,
                                               subresource_path)
        self.assertEqual(expected_result, value)

    def test_get_sub_resource_path_by_list(self):
        subresource_path = ['EthernetInterfaces']
        expected_result = '/redfish/v1/Systems/437XR1138R2/EthernetInterfaces'
        value = utils.get_sub_resource_path_by(self.sys_inst,
                                               subresource_path)
        self.assertEqual(expected_result, value)

    def test_get_sub_resource_path_by_fails(self):
        subresource_path = ['Links', 'Chassis']
        expected_result = 'attribute Links/Chassis/@odata.id is missing'
        self.assertRaisesRegex(
            exceptions.MissingAttributeError,
            expected_result,
            utils.get_sub_resource_path_by,
            self.sys_inst, subresource_path)

    def test_get_sub_resource_path_by_fails_with_empty_path(self):
        self.assertRaisesRegex(
            ValueError,
            '"subresource_name" cannot be empty',
            utils.get_sub_resource_path_by,
            self.sys_inst, [])

    def test_get_sub_resource_path_by_fails_with_empty_string(self):
        self.assertRaisesRegex(
            ValueError,
            '"subresource_name" cannot be empty',
            utils.get_sub_resource_path_by,
            self.sys_inst, '')
