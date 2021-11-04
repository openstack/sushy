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
from sushy.resources.system import secure_boot_database
from sushy.tests.unit import base


class SecureBootDatabaseTestCase(base.TestCase):

    def setUp(self):
        super(SecureBootDatabaseTestCase, self).setUp()
        self.conn = mock.Mock()
        with open('sushy/tests/unit/json_samples/'
                  'secure_boot_database.json') as f:
            self.secure_boot_json = json.load(f)

        self.conn.get.return_value.json.return_value = self.secure_boot_json
        self.secure_boot = secure_boot_database.SecureBootDatabase(
            self.conn,
            '/redfish/v1/Systems/437XR1138R2/SecureBoot'
            '/SecureBootDatabases/db',
            registries={}, redfish_version='1.0.0')

    def test__parse_attributes(self):
        self.secure_boot._parse_attributes(self.secure_boot_json)
        self.assertEqual('1.0.0', self.secure_boot.redfish_version)
        self.assertEqual('db', self.secure_boot.identity)
        self.assertEqual('db - Authorized Signature Database',
                         self.secure_boot.name)

    @mock.patch.object(secure_boot_database.LOG, 'warning', autospec=True)
    def test_get_allowed_reset_keys_values(self, mock_log):
        self.assertEqual({
            constants.SecureBootResetKeysType.RESET_ALL_KEYS_TO_DEFAULT,
            constants.SecureBootResetKeysType.DELETE_ALL_KEYS
        }, self.secure_boot.get_allowed_reset_keys_values())
        self.assertFalse(mock_log.called)

    @mock.patch.object(secure_boot_database.LOG, 'warning', autospec=True)
    def test_get_allowed_reset_keys_values_no_values(self, mock_log):
        self.secure_boot._actions.reset_keys.allowed_values = None
        self.assertEqual({
            constants.SecureBootResetKeysType.RESET_ALL_KEYS_TO_DEFAULT,
            constants.SecureBootResetKeysType.DELETE_ALL_KEYS
        }, self.secure_boot.get_allowed_reset_keys_values())
        self.assertTrue(mock_log.called)

    @mock.patch.object(secure_boot_database.LOG, 'warning', autospec=True)
    def test_get_allowed_reset_keys_values_custom_values(self, mock_log):
        self.secure_boot._actions.reset_keys.allowed_values = [
            'ResetAllKeysToDefault',
            'IamNotRedfishCompatible',
        ]
        self.assertEqual(
            {constants.SecureBootResetKeysType.RESET_ALL_KEYS_TO_DEFAULT},
            self.secure_boot.get_allowed_reset_keys_values())
        self.assertFalse(mock_log.called)

    def test_reset_keys(self):
        self.secure_boot.reset_keys(
            constants.SecureBootResetKeysType.RESET_ALL_KEYS_TO_DEFAULT)
        self.conn.post.assert_called_once_with(
            '/redfish/v1/Systems/437XR1138R2/SecureBoot/SecureBootDatabases/db'
            '/Actions/SecureBootDatabase.ResetKeys',
            data={'ResetKeysType': 'ResetAllKeysToDefault'})

    def test_reset_keys_wrong_value(self):
        self.assertRaises(exceptions.InvalidParameterValueError,
                          self.secure_boot.reset_keys, 'DeleteEverything')


class SecureBootDatabaseCollectionTestCase(base.TestCase):

    def setUp(self):
        super(SecureBootDatabaseCollectionTestCase, self).setUp()
        self.conn = mock.Mock()
        with open('sushy/tests/unit/json_samples/'
                  'secure_boot_database_collection.json') as f:
            self.json_doc = json.load(f)

        self.conn.get.return_value.json.return_value = self.json_doc

        self.collection = secure_boot_database.SecureBootDatabaseCollection(
            self.conn, '/redfish/v1/Systems/437XR1138R2/SecureBootDatabases',
            redfish_version='1.0.0')

    def test__parse_attributes(self):
        self.collection._parse_attributes(self.json_doc)
        self.assertEqual('1.0.0', self.collection.redfish_version)
        self.assertEqual('UEFI SecureBoot Database Collection',
                         self.collection.name)
        self.assertEqual(tuple(
            '/redfish/v1/Systems/437XR1138R2/SecureBoot/SecureBootDatabases/'
            + member
            for member in ('PK', 'KEK', 'db', 'dbx',
                           'PKDefault', 'KEKDefault',
                           'dbDefault', 'dbxDefault')
        ), self.collection.members_identities)

    @mock.patch.object(secure_boot_database, 'SecureBootDatabase',
                       autospec=True)
    def test_get_member(self, mock_secure_boot_database):
        self.collection.get_member(
            '/redfish/v1/Systems/437XR1138R2/SecureBoot'
            '/SecureBootDatabases/db')
        mock_secure_boot_database.assert_called_once_with(
            self.collection._conn,
            '/redfish/v1/Systems/437XR1138R2/SecureBoot'
            '/SecureBootDatabases/db',
            redfish_version=self.collection.redfish_version, registries=None,
            root=self.collection.root)

    @mock.patch.object(secure_boot_database, 'SecureBootDatabase',
                       autospec=True)
    def test_get_members(self, mock_secure_boot_database):
        members = self.collection.get_members()
        calls = [
            mock.call(self.collection._conn,
                      '/redfish/v1/Systems/437XR1138R2/SecureBoot'
                      '/SecureBootDatabases/%s' % member,
                      redfish_version=self.collection.redfish_version,
                      registries=None,
                      root=self.collection.root)
            for member in ('PK', 'KEK', 'db', 'dbx',
                           'PKDefault', 'KEKDefault',
                           'dbDefault', 'dbxDefault')
        ]
        mock_secure_boot_database.assert_has_calls(calls)
        self.assertIsInstance(members, list)
        self.assertEqual(8, len(members))
