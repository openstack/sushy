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
from sushy.resources.accountservice import accountservice
from sushy.resources.certificateservice import certificate
from sushy.tests.unit import base


class AccountServiceTestCase(base.TestCase):

    def setUp(self):
        super().setUp()
        self.conn = mock.Mock()
        with open('sushy/tests/unit/json_samples/'
                  'account_service.json') as f:
            self.json_doc = json.load(f)

        self.conn.get.return_value.json.return_value = self.json_doc

        self.account_service = accountservice.AccountService(
            self.conn, '/redfish/v1/AccountService',
            redfish_version='1.0.2')

    def test__parse_attributes(self):
        self.account_service._parse_attributes(self.json_doc)
        self.assertEqual('AccountService', self.account_service.identity)
        self.assertEqual('Account Service', self.account_service.name)
        self.assertTrue(self.account_service.service_enabled)
        self.assertEqual(5, self.account_service.account_lockout_threshold)
        self.assertEqual(30, self.account_service.account_lockout_duration)
        self.assertEqual(
            30, self.account_service.account_lockout_counter_reset_after)
        self.assertEqual(8, self.account_service.min_password_length)
        self.assertEqual(127, self.account_service.max_password_length)
        self.assertEqual(sushy.LocalAccountAuth.FALLBACK,
                         self.account_service.local_account_auth)

    def test_ldap(self):
        ldap = self.account_service.ldap
        self.assertFalse(ldap.service_enabled)
        self.assertEqual(['ldaps://ldap.contoso.com:636'],
                         ldap.service_addresses)
        self.assertEqual(
            sushy.AuthenticationType.USERNAME_AND_PASSWORD,
            ldap.authentication.authentication_type)
        self.assertEqual('cn=manager,dc=contoso,dc=com',
                         ldap.authentication.username)
        self.assertEqual(
            ['dc=contoso,dc=com'],
            ldap.ldap_service.search_settings.base_distinguished_names)
        self.assertEqual(
            'uid',
            ldap.ldap_service.search_settings.username_attribute)
        self.assertEqual(
            'cn',
            ldap.ldap_service.search_settings.group_name_attribute)
        self.assertEqual(
            'memberof',
            ldap.ldap_service.search_settings.groups_attribute)
        self.assertEqual(1, len(ldap.remote_role_mapping))
        self.assertEqual('cn=admins,dc=contoso,dc=com',
                         ldap.remote_role_mapping[0].remote_group)
        self.assertEqual('Administrator',
                         ldap.remote_role_mapping[0].local_role)
        self.assertEqual('/redfish/v1/AccountService/LDAP/Certificates',
                         ldap._certificates_path)

    def test_active_directory(self):
        ad = self.account_service.active_directory
        self.assertFalse(ad.service_enabled)
        self.assertEqual(['ad.contoso.com'], ad.service_addresses)
        self.assertEqual(
            sushy.AuthenticationType.KERBEROS_KEYTAB,
            ad.authentication.authentication_type)
        self.assertEqual(1, len(ad.remote_role_mapping))
        self.assertEqual('Domain Admins',
                         ad.remote_role_mapping[0].remote_group)
        self.assertEqual('Administrator',
                         ad.remote_role_mapping[0].local_role)

    @mock.patch.object(account, 'ManagerAccountCollection', autospec=True)
    def test_accounts(self, mock_accounts):
        self.account_service.accounts
        mock_accounts.assert_called_once_with(
            self.conn, '/redfish/v1/AccountService/Accounts',
            redfish_version=self.account_service.redfish_version,
            registries=None,
            root=self.account_service.root)

    @mock.patch.object(certificate, 'CertificateCollection', autospec=True)
    def test_ldap_certificates(self, mock_certs):
        self.account_service.ldap_certificates
        mock_certs.assert_called_once_with(
            self.conn, '/redfish/v1/AccountService/LDAP/Certificates',
            redfish_version=self.account_service.redfish_version,
            registries=None,
            root=self.account_service.root)

    @mock.patch.object(certificate, 'CertificateCollection', autospec=True)
    def test_active_directory_certificates(self, mock_certs):
        self.account_service.active_directory_certificates
        mock_certs.assert_called_once_with(
            self.conn,
            '/redfish/v1/AccountService/ActiveDirectory/Certificates',
            redfish_version=self.account_service.redfish_version,
            registries=None,
            root=self.account_service.root)
