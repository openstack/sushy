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

# This is referred from Redfish standard schema.
# https://redfish.dmtf.org/schemas/AccountService.v1_15_1.json

import logging

from sushy import exceptions
from sushy.resources.accountservice import account
from sushy.resources.accountservice import constants as acct_cons
from sushy.resources import base
from sushy.resources.certificateservice import certificate
from sushy.resources import common
from sushy import utils

LOG = logging.getLogger(__name__)


class LDAPSearchSettingsField(base.CompositeField):
    base_distinguished_names = base.Field('BaseDistinguishedNames',
                                          adapter=list)
    username_attribute = base.Field('UsernameAttribute')
    group_name_attribute = base.Field('GroupNameAttribute')
    groups_attribute = base.Field('GroupsAttribute')


class LDAPServiceField(base.CompositeField):
    search_settings = LDAPSearchSettingsField('SearchSettings')


class AuthenticationField(base.CompositeField):
    authentication_type = base.MappedField(
        'AuthenticationType', acct_cons.AuthenticationType)
    username = base.Field('Username')


class RoleMappingField(base.ListField):
    remote_group = base.Field('RemoteGroup')
    remote_user = base.Field('RemoteUser')
    local_role = base.Field('LocalRole')


class ExternalAccountProviderField(base.CompositeField):
    service_enabled = base.Field('ServiceEnabled')
    service_addresses = base.Field('ServiceAddresses', adapter=list)
    authentication = AuthenticationField('Authentication')
    ldap_service = LDAPServiceField('LDAPService')
    remote_role_mapping = RoleMappingField('RemoteRoleMapping')
    _certificates_path = base.Field(['Certificates', '@odata.id'])


class AccountService(base.ResourceBase):

    identity = base.Field('Id', required=True)
    """The account service identity string"""

    name = base.Field('Name')
    """The name of the resource"""

    description = base.Field('Description')
    """Description"""

    service_enabled = base.Field('ServiceEnabled')
    """Whether the account service is enabled"""

    account_lockout_threshold = base.Field('AccountLockoutThreshold')
    """Number of failed login attempts before the account is locked"""

    account_lockout_duration = base.Field('AccountLockoutDuration')
    """Duration in seconds an account is locked after exceeding the
    lockout threshold"""

    account_lockout_counter_reset_after = base.Field(
        'AccountLockoutCounterResetAfter')
    """Duration in seconds after which the failed login counter resets"""

    min_password_length = base.Field('MinPasswordLength')
    """Minimum password length"""

    max_password_length = base.Field('MaxPasswordLength')
    """Maximum password length"""

    local_account_auth = base.MappedField('LocalAccountAuth',
                                          acct_cons.LocalAccountAuth)
    """Whether local accounts are authorized"""

    ldap = ExternalAccountProviderField('LDAP')
    """LDAP external account provider settings"""

    active_directory = ExternalAccountProviderField('ActiveDirectory')
    """Active Directory external account provider settings"""

    status = common.StatusField('Status')
    """Describes the status and health of this resource."""

    @property
    @utils.cache_it
    def accounts(self):
        """Property to reference the ManagerAccountCollection."""
        return account.ManagerAccountCollection(
            self._conn,
            utils.get_sub_resource_path_by(self, 'Accounts'),
            redfish_version=self.redfish_version,
            registries=self.registries, root=self.root)

    @property
    @utils.cache_it
    def ldap_certificates(self):
        """Property to reference the LDAP CertificateCollection."""
        if not self.ldap or not self.ldap._certificates_path:
            raise exceptions.MissingAttributeError(
                attribute='LDAP/Certificates/@odata.id',
                resource=self._path)
        return certificate.CertificateCollection(
            self._conn, self.ldap._certificates_path,
            redfish_version=self.redfish_version,
            registries=self.registries, root=self.root)

    @property
    @utils.cache_it
    def active_directory_certificates(self):
        """Property to reference the Active Directory CertificateCollection."""
        if not self.active_directory \
                or not self.active_directory._certificates_path:
            raise exceptions.MissingAttributeError(
                attribute='ActiveDirectory/Certificates/@odata.id',
                resource=self._path)
        return certificate.CertificateCollection(
            self._conn, self.active_directory._certificates_path,
            redfish_version=self.redfish_version,
            registries=self.registries, root=self.root)
