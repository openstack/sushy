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


import mock

from sushy.tests.unit import base
from sushy import utils


class UtilsTestCase(base.TestCase):

    def test_revert_dictionary(self):
        source = {'key0': 'value0', 'key1': 'value1'}
        expected = {'value0': 'key0', 'value1': 'key1'}
        self.assertEqual(expected, utils.revert_dictionary(source))

    @mock.patch.object(utils.LOG, 'warning', autospec=True)
    def test_get_members_ids(self, log_mock):
        members = [{"@odata.id": "/redfish/v1/Systems/FOO"},
                   {"other_key": "/redfish/v1/Systems/FUN"},
                   {"@odata.id": "/redfish/v1/Systems/BAR/"}]
        expected = ('FOO', 'BAR')
        self.assertEqual(expected, utils.get_members_ids(members))
        self.assertEqual(1, log_mock.call_count)

    def test_strip_redfish_base(self):
        expected = 'Systems/1'
        self.assertEqual(expected, utils.strip_redfish_base('Systems/1'))
        self.assertEqual(expected, utils.strip_redfish_base('/Systems/1'))
        self.assertEqual(expected,
                         utils.strip_redfish_base('/redfish/v1/Systems/1'))
        self.assertEqual(expected,
                         utils.strip_redfish_base('redfish/v1/Systems/1'))
        self.assertEqual(expected,
                         utils.strip_redfish_base('/redfish/v2/Systems/1'))
        self.assertEqual(expected,
                         utils.strip_redfish_base('redfish/v2/Systems/1'))
