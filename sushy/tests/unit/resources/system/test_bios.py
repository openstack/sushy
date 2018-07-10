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
from sushy.resources.system import bios
from sushy.tests.unit import base


class BiosTestCase(base.TestCase):

    def setUp(self):
        super(BiosTestCase, self).setUp()
        self.conn = mock.Mock()
        with open('sushy/tests/unit/json_samples/bios.json') as f:
            bios_json = json.load(f)
        with open('sushy/tests/unit/json_samples/bios_settings.json') as f:
            bios_settings_json = json.load(f)

        self.conn.get.return_value.json.side_effect = [
            bios_json,
            bios_settings_json,
            bios_settings_json]

        self.sys_bios = bios.Bios(
            self.conn, '/redfish/v1/Systems/437XR1138R2/BIOS',
            redfish_version='1.0.2')

    def test__parse_attributes(self):
        self.sys_bios._parse_attributes()
        self.assertEqual('1.0.2', self.sys_bios.redfish_version)
        self.assertEqual('BIOS', self.sys_bios.identity)
        self.assertEqual('BIOS Configuration Current Settings',
                         self.sys_bios.name)
        self.assertIsNone(self.sys_bios.description)
        self.assertEqual('BiosAttributeRegistryP89.v1_0_0',
                         self.sys_bios._attribute_registry)
        self.assertEqual('', self.sys_bios.attributes['AdminPhone'])
        self.assertEqual('Uefi', self.sys_bios.attributes['BootMode'])
        self.assertEqual(0, self.sys_bios.attributes['ProcCoreDisable'])
        # testing here if settings subfield parsed by checking ETag,
        # other settings fields tested in specific settings test
        self.assertEqual('9234ac83b9700123cc32',
                         self.sys_bios._settings._etag)
        self.assertEqual('(404) 555-1212',
                         self.sys_bios.pending_attributes['AdminPhone'])

    def test_set_attribute(self):
        self.sys_bios.set_attribute('ProcTurboMode', 'Disabled')
        self.sys_bios._conn.patch.assert_called_once_with(
            '/redfish/v1/Systems/437XR1138R2/BIOS/Settings',
            data={'Attributes': {'ProcTurboMode': 'Disabled'}})

    def test_set_attribute_on_refresh(self):
        # make it to instantiate pending attributes
        self.sys_bios.pending_attributes
        self.sys_bios.set_attribute('ProcTurboMode', 'Disabled')
        self.assertTrue(self.sys_bios._pending_settings_resource._is_stale)
        # make it to refresh pending attributes on next retrieval
        self.sys_bios.pending_attributes
        self.assertFalse(self.sys_bios._pending_settings_resource._is_stale)

    def test_set_attributes(self):
        self.sys_bios.set_attributes({'ProcTurboMode': 'Disabled',
                                      'UsbControl': 'UsbDisabled'})
        self.sys_bios._conn.patch.assert_called_once_with(
            '/redfish/v1/Systems/437XR1138R2/BIOS/Settings',
            data={'Attributes': {'ProcTurboMode': 'Disabled',
                                 'UsbControl': 'UsbDisabled'}})

    def test_set_attributes_on_refresh(self):
        # make it to instantiate pending attributes
        self.sys_bios.pending_attributes
        self.sys_bios.set_attributes({'ProcTurboMode': 'Disabled',
                                      'UsbControl': 'UsbDisabled'})
        self.assertTrue(self.sys_bios._pending_settings_resource._is_stale)
        # make it to refresh pending attributes on next retrieval
        self.sys_bios.pending_attributes
        self.assertFalse(self.sys_bios._pending_settings_resource._is_stale)

    def test__get_reset_bios_action_element(self):
        value = self.sys_bios._get_reset_bios_action_element()
        self.assertEqual('/redfish/v1/Systems/437XR1138R2/BIOS/Actions/'
                         'Bios.ResetBios',
                         value.target_uri)

    def test_reset_bios_missing_action(self):
        self.sys_bios._actions.reset_bios = None
        self.assertRaisesRegex(
            exceptions.MissingActionError, '#Bios.ResetBios',
            self.sys_bios.reset_bios)

    def test__parse_attributes_missing_reset_bios_target(self):
        self.sys_bios.json['Actions']['#Bios.ResetBios'].pop(
            'target')
        self.assertRaisesRegex(
            exceptions.MissingAttributeError,
            'attribute Actions/#Bios.ResetBios/target',
            self.sys_bios._parse_attributes)

    def test_reset_bios(self):
        self.sys_bios.reset_bios()
        self.sys_bios._conn.post.assert_called_once_with(
            '/redfish/v1/Systems/437XR1138R2/BIOS/Actions/Bios.ResetBios')

    def test__get_change_password_element(self):
        value = self.sys_bios._get_change_password_element()
        self.assertEqual("/redfish/v1/Systems/437XR1138R2/BIOS/Actions/"
                         "Bios.ChangePassword",
                         value.target_uri)

    def test_change_password_missing_action(self):
        self.sys_bios._actions.change_password = None
        self.assertRaisesRegex(
            exceptions.MissingActionError, '#Bios.ChangePassword',
            self.sys_bios.change_password, 'newpassword',
                                           'oldpassword',
                                           'adminpassword')

    def test__parse_attributes_missing_change_password_target(self):
        self.sys_bios.json['Actions']['#Bios.ChangePassword'].pop(
            'target')
        self.assertRaisesRegex(
            exceptions.MissingAttributeError,
            'attribute Actions/#Bios.ChangePassword/target',
            self.sys_bios._parse_attributes)

    def test_change_password(self):
        self.sys_bios.change_password('newpassword',
                                      'oldpassword',
                                      'adminpassword')
        self.sys_bios._conn.post.assert_called_once_with(
            '/redfish/v1/Systems/437XR1138R2/BIOS/Actions/Bios.ChangePassword',
            data={'OldPassword': 'oldpassword',
                  'NewPassword': 'newpassword',
                  'PasswordName': 'adminpassword'})
