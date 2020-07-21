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


from sushy.resources.oem import fake
from sushy.resources.system import system
from sushy.tests.unit import base


class FakeOEMSystemExtensionTestCase(base.TestCase):

    def setUp(self):
        super(FakeOEMSystemExtensionTestCase, self).setUp()
        self.conn = mock.MagicMock()
        with open('sushy/tests/unit/json_samples/system.json', 'r') as f:
            self.conn.get.return_value.json.return_value = json.loads(f.read())

        self.sys_instance = system.System(
            self.conn, '/redfish/v1/Systems/437XR1138R2',
            redfish_version='1.0.2')
        self.fake_sys_oem_extn = fake.FakeOEMSystemExtension(
            self.conn, '',
            redfish_version='1.0.2')
        self.fake_sys_oem_extn = self.fake_sys_oem_extn.set_parent_resource(
            self.sys_instance, 'Contoso')

    def test__parse_oem_attributes(self):
        self.assertEqual('#Contoso.ComputerSystem',
                         self.fake_sys_oem_extn.data_type)
        self.assertEqual('PacWest Production Facility', (
            self.fake_sys_oem_extn.production_location.facility_name))
        self.assertEqual('USA', (
            self.fake_sys_oem_extn.production_location.country))
        self.assertEqual(
            "/redfish/v1/Systems/437XR1138R2/Oem/Contoso/Actions/"
            "Contoso.Reset",
            self.fake_sys_oem_extn._actions.reset.target_uri)

    def test_get_reset_system_path(self):
        value = self.fake_sys_oem_extn.get_reset_system_path()
        expected = (
            '/redfish/v1/Systems/437XR1138R2/Oem/Contoso/Actions/Contoso.Reset'
            )
        self.assertEqual(expected, value)
