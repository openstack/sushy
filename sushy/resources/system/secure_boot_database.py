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

import logging

from sushy import exceptions
from sushy.resources import base
from sushy.resources import common
from sushy.resources.system import constants

LOG = logging.getLogger(__name__)


class ResetKeysActionField(common.ActionField):

    allowed_values = base.Field('ResetKeysType@Redfish.AllowableValues',
                                adapter=list)


class ActionsField(base.CompositeField):

    reset_keys = ResetKeysActionField('#SecureBootDatabase.ResetKeys')
    """Action that resets the UEFI Secure Boot keys."""


class SecureBootDatabase(base.ResourceBase):

    # TODO(dtantsur): certificates

    database_id = base.MappedField('DatabaseId',
                                   constants.SecureBootDatabaseId)
    """Standard UEFI database type."""

    description = base.Field('Description')
    """The system description"""

    identity = base.Field('Id', required=True)
    """The secure boot database identity string"""

    name = base.Field('Name')
    """The secure boot database name"""

    # TODO(dtantsur): signatures

    _actions = ActionsField('Actions')

    def _get_reset_action_element(self):
        reset_action = self._actions.reset_keys
        if not reset_action:
            raise exceptions.MissingActionError(
                action='#SecureBootDatabase.ResetKeys', resource=self._path)
        return reset_action

    def get_allowed_reset_keys_values(self):
        """Get the allowed values for resetting the keys.

        :returns: A set with the allowed values.
        """
        reset_action = self._get_reset_action_element()

        if not reset_action.allowed_values:
            LOG.warning('Could not figure out the allowed values for the '
                        'reset keys action for %s', self.identity)
            return constants._SECURE_BOOT_DATABASE_RESET_KEYS

        return {v for v in constants._SECURE_BOOT_DATABASE_RESET_KEYS
                if v.value in reset_action.allowed_values}

    def reset_keys(self, reset_type):
        """Reset secure boot keys.

        :param reset_type: Reset type, one of `SECURE_BOOT_RESET_KEYS_*`
            constants.
        """
        valid_resets = self.get_allowed_reset_keys_values()
        if reset_type not in valid_resets:
            raise exceptions.InvalidParameterValueError(
                parameter='reset_type', value=reset_type,
                valid_values=valid_resets)

        reset_type = constants.SecureBootResetKeysType(reset_type).value
        target_uri = self._get_reset_action_element().target_uri
        self._conn.post(target_uri, data={'ResetKeysType': reset_type})


class SecureBootDatabaseCollection(base.ResourceCollectionBase):

    @property
    def _resource_type(self):
        return SecureBootDatabase

    def __init__(self, connector, path, redfish_version=None, registries=None,
                 root=None):
        """A class representing a ComputerSystemCollection

        :param connector: A Connector instance
        :param path: The canonical path to the System collection resource
        :param redfish_version: The version of RedFish. Used to construct
            the object according to schema of the given version.
        :param registries: Dict of Redfish Message Registry objects to be
            used in any resource that needs registries to parse messages
        :param root: Sushy root object. Empty for Sushy root itself.
        """
        super(SecureBootDatabaseCollection, self).__init__(
            connector, path, redfish_version=redfish_version,
            registries=registries, root=root)
