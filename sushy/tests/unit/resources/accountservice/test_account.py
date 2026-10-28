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

import sushy
from sushy.resources.accountservice import account
from sushy.tests.unit import base


class ManagerAccountTestCase(base.TestCase):

    def setUp(self):
        super().setUp()
        self.conn = mock.Mock()
        with open('sushy/tests/unit/json_samples/'
                  'manager_account.json') as f:
            self.json_doc = json.load(f)

        self.conn.get.return_value.json.return_value = self.json_doc

        self.account = account.ManagerAccount(
            self.conn, '/redfish/v1/AccountService/Accounts/2',
            redfish_version='1.0.2')

    def test__parse_attributes(self):
        self.account._parse_attributes(self.json_doc)
        self.assertEqual('2', self.account.identity)
        self.assertEqual('User Account', self.account.name)
        self.assertEqual('Admin User Account', self.account.description)
        self.assertEqual('admin', self.account.user_name)
        self.assertTrue(self.account.enabled)
        self.assertFalse(self.account.locked)
        self.assertEqual('Administrator', self.account.role_id)
        self.assertFalse(self.account.password_change_required)
        self.assertEqual(
            [sushy.AccountTypes.REDFISH, sushy.AccountTypes.IPMI],
            self.account.account_types)

    def test_set_password(self):
        self.conn.get.reset_mock()
        self.account.set_password('newpass')
        self.conn.patch.assert_called_once_with(
            '/redfish/v1/AccountService/Accounts/2',
            data={'Password': 'newpass'})
        # No invalidation and no refresh
        self.conn.get.assert_not_called()
        self.assertFalse(self.account._is_stale)

    def test_set_enabled(self):
        self.account.set_enabled(False)
        self.conn.patch.assert_called_once_with(
            '/redfish/v1/AccountService/Accounts/2',
            data={'Enabled': False})

    def test_set_locked(self):
        self.account.set_locked(False)
        self.conn.patch.assert_called_once_with(
            '/redfish/v1/AccountService/Accounts/2',
            data={'Locked': False})

    def test_delete(self):
        self.account.delete()
        self.conn.delete.assert_called_once_with(
            '/redfish/v1/AccountService/Accounts/2')


class ManagerAccountCollectionTestCase(base.TestCase):

    def setUp(self):
        super().setUp()
        self.conn = mock.Mock()
        with open('sushy/tests/unit/json_samples/'
                  'manager_account_collection.json') as f:
            self.json_doc = json.load(f)

        self.conn.get.return_value.json.return_value = self.json_doc

        self.account_col = account.ManagerAccountCollection(
            self.conn, '/redfish/v1/AccountService/Accounts',
            redfish_version='1.0.2')

    def test__parse_attributes(self):
        self.account_col._parse_attributes(self.json_doc)
        self.assertEqual('Accounts Collection', self.account_col.name)
        self.assertEqual(
            ('/redfish/v1/AccountService/Accounts/1',
             '/redfish/v1/AccountService/Accounts/2'),
            self.account_col.members_identities)

    def test_create_member(self):
        self.conn.post.return_value.headers = {
            'Location': '/redfish/v1/AccountService/Accounts/3'
        }
        with open('sushy/tests/unit/json_samples/'
                  'manager_account.json') as f:
            self.conn.get.return_value.json.return_value = json.load(f)
        result = self.account_col.create_member(
            'newuser', 'pass123', 'Operator')
        self.conn.post.assert_called_once_with(
            '/redfish/v1/AccountService/Accounts',
            data={'UserName': 'newuser',
                  'Password': 'pass123',
                  'RoleId': 'Operator'})
        self.assertIsNotNone(result)
