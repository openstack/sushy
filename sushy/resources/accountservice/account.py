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
# https://redfish.dmtf.org/schemas/ManagerAccount.v1_12_1.json

import logging

from sushy.resources.accountservice import constants as acct_cons
from sushy.resources import base

LOG = logging.getLogger(__name__)


class ManagerAccount(base.ResourceBase):

    identity = base.Field('Id', required=True)
    """The account identity string"""

    name = base.Field('Name')
    """The name of the resource"""

    description = base.Field('Description')
    """Description"""

    user_name = base.Field('UserName')
    """The user name for the account"""

    enabled = base.Field('Enabled')
    """Whether the account is enabled"""

    locked = base.Field('Locked')
    """Whether the account is locked"""

    role_id = base.Field('RoleId')
    """The role for this account"""

    password_change_required = base.Field('PasswordChangeRequired')
    """Whether the service requires the password to be changed"""

    account_types = base.MappedListField('AccountTypes',
                                         acct_cons.AccountTypes)
    """The account types"""

    def set_password(self, password):
        """Set the account password.

        This method doesn't refresh or invalidate the resource.

        :param password: The new password.
        """
        self._conn.patch(self.path, data={'Password': password})
        # NOTE(dtantsur): not refreshing here: password is not visible anyway,
        # and refreshing the freshly updated user will fail.

    def set_enabled(self, enabled):
        """Enable or disable this account.

        :param enabled: Whether the account should be enabled.
        """
        self._conn.patch(self.path, data={'Enabled': enabled})
        self.refresh(force=True)

    def set_locked(self, locked):
        """Lock or unlock this account.

        :param locked: False to unlock the account.
        """
        self._conn.patch(self.path, data={'Locked': locked})
        self.refresh(force=True)

    def delete(self):
        """Delete this account."""
        self._conn.delete(self._path)


class ManagerAccountCollection(base.MutableResourceCollectionBase):

    _resource_type = ManagerAccount

    def create_member(self, user_name, password, role_id):
        """Create a new account.

        :param user_name: The user name for the new account.
        :param password: The password for the new account.
        :param role_id: The role for the new account.
        :returns: The created ManagerAccount resource or None.
        """
        return self._create_member(dict(
            UserName=user_name,
            Password=password,
            RoleId=role_id,
        ))
