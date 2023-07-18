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

from sushy import exceptions
from sushy.resources.system import constants
from sushy.resources.system import secure_boot
from sushy.resources.system import secure_boot_database
from sushy.tests.unit import base


class SecureBootTestCase(base.TestCase):

    def setUp(self):
        super(SecureBootTestCase, self).setUp()
        self.conn = mock.Mock()
        with open('sushy/tests/unit/json_samples/secure_boot.json') as f:
            self.secure_boot_json = json.load(f)

        self.conn.get.return_value.json.return_value = self.secure_boot_json
        self.conn.get.return_value.headers = {'ETag': 'b26ae716a2c1f39f'}
        self.secure_boot = secure_boot.SecureBoot(
            self.conn, '/redfish/v1/Systems/437XR1138R2/SecureBoot',
            registries={}, redfish_version='1.1.0')

    def test__parse_attributes(self):
        self.secure_boot._parse_attributes(self.secure_boot_json)
        self.assertEqual('1.1.0', self.secure_boot.redfish_version)
        self.assertEqual('SecureBoot', self.secure_boot.identity)
        self.assertEqual('UEFI Secure Boot', self.secure_boot.name)
        self.assertIsNone(self.secure_boot.description)
        self.assertIs(False, self.secure_boot.enabled)
        self.assertEqual(constants.SecureBootCurrentBoot.DISABLED,
                         self.secure_boot.current_boot)
        self.assertEqual(constants.SecureBootMode.DEPLOYED,
                         self.secure_boot.mode)

    @mock.patch.object(secure_boot.LOG, 'warning', autospec=True)
    def test_get_allowed_reset_keys_values(self, mock_log):
        self.assertEqual({
            constants.SecureBootResetKeysType.RESET_ALL_KEYS_TO_DEFAULT,
            constants.SecureBootResetKeysType.DELETE_ALL_KEYS,
            constants.SecureBootResetKeysType.DELETE_PK
        }, self.secure_boot.get_allowed_reset_keys_values())
        self.assertFalse(mock_log.called)

    @mock.patch.object(secure_boot.LOG, 'warning', autospec=True)
    def test_get_allowed_reset_keys_values_no_values(self, mock_log):
        self.secure_boot._actions.reset_keys.allowed_values = None
        self.assertEqual({
            constants.SecureBootResetKeysType.RESET_ALL_KEYS_TO_DEFAULT,
            constants.SecureBootResetKeysType.DELETE_ALL_KEYS,
            constants.SecureBootResetKeysType.DELETE_PK
        }, self.secure_boot.get_allowed_reset_keys_values())
        self.assertTrue(mock_log.called)

    @mock.patch.object(secure_boot.LOG, 'warning', autospec=True)
    def test_get_allowed_reset_keys_values_custom_values(self, mock_log):
        self.secure_boot._actions.reset_keys.allowed_values = [
            'ResetAllKeysToDefault',
            'IamNotRedfishCompatible',
        ]
        self.assertEqual(
            {constants.SecureBootResetKeysType.RESET_ALL_KEYS_TO_DEFAULT},
            self.secure_boot.get_allowed_reset_keys_values())
        self.assertFalse(mock_log.called)

    def test_set_enabled(self):
        self.secure_boot.set_enabled(True)
        self.conn.patch.assert_called_once_with(
            '/redfish/v1/Systems/437XR1138R2/SecureBoot',
            data={'SecureBootEnable': True},
            etag='b26ae716a2c1f39f')

    def test_set_enabled_wrong_type(self):
        self.assertRaises(exceptions.InvalidParameterValueError,
                          self.secure_boot.set_enabled, 'banana')

    def test_reset_keys(self):
        self.secure_boot.reset_keys(
            constants.SecureBootResetKeysType.RESET_ALL_KEYS_TO_DEFAULT)
        self.conn.post.assert_called_once_with(
            '/redfish/v1/Systems/437XR1138R2/SecureBoot'
            '/Actions/SecureBoot.ResetKeys',
            data={'ResetKeysType': 'ResetAllKeysToDefault'})

    def test_reset_keys_wrong_value(self):
        self.assertRaises(exceptions.InvalidParameterValueError,
                          self.secure_boot.reset_keys, 'DeleteEverything')

    def test_databases(self):
        self.conn.get.return_value.json.reset_mock()

        with open('sushy/tests/unit/json_samples/'
                  'secure_boot_database_collection.json') as f:
            self.conn.get.return_value.json.return_value = json.load(f)

        result = self.secure_boot.databases
        self.assertIsInstance(
            result, secure_boot_database.SecureBootDatabaseCollection)
        self.conn.get.return_value.json.assert_called_once_with()

        self.conn.get.return_value.json.reset_mock()

        self.assertIs(result, self.secure_boot.databases)
        self.conn.get.return_value.json.assert_not_called()
