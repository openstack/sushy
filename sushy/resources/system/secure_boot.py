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

# This is referred from Redfish standard schema.
# http://redfish.dmtf.org/schemas/v1/SecureBoot.v1_1_0.json

import logging

from sushy import exceptions
from sushy.resources import base
from sushy.resources import common
from sushy.resources.system import mappings

LOG = logging.getLogger(__name__)


class ResetKeysActionField(common.ActionField):

    allowed_values = base.Field('ResetKeysType@Redfish.AllowableValues',
                                adapter=list)


class ActionsField(base.CompositeField):

    reset_keys = ResetKeysActionField('#SecureBoot.ResetKeys')
    """Action that resets the UEFI Secure Boot keys."""


class SecureBoot(base.ResourceBase):

    identity = base.Field('Id', required=True)
    """The Bios resource identity string"""

    name = base.Field('Name')
    """The name of the resource"""

    description = base.Field('Description')
    """Human-readable description of the BIOS resource"""

    current_boot = base.MappedField('SecureBootCurrentBoot',
                                    mappings.SECURE_BOOT_STATE)
    """The UEFI Secure Boot state during the current boot cycle."""

    enabled = base.Field('SecureBootEnable')
    """Whether the UEFI Secure Boot takes effect on next boot.

    This property can be enabled in UEFI boot mode only.
    """

    mode = base.MappedField('SecureBootMode', mappings.SECURE_BOOT_MODE)
    """The current UEFI Secure Boot Mode."""

    # TODO(dtantsur): SecureBootDatabases

    _actions = ActionsField('Actions')

    def __init__(self, connector, path, redfish_version=None, registries=None):
        """A class representing secure boot settings.

        :param connector: A Connector instance
        :param path: Sub-URI path to the SecureBoot resource
        :param registries: Dict of message registries to be used when
            parsing messages of attribute update status
        """
        super().__init__(connector, path, redfish_version, registries)

    def _get_reset_action_element(self):
        reset_action = self._actions.reset_keys
        if not reset_action:
            raise exceptions.MissingActionError(action='#SecureBoot.ResetKeys',
                                                resource=self._path)
        return reset_action

    def get_allowed_reset_keys_values(self):
        """Get the allowed values for resetting the keys.

        :returns: A set with the allowed values.
        """
        reset_action = self._get_reset_action_element()

        if not reset_action.allowed_values:
            LOG.warning('Could not figure out the allowed values for the '
                        'reset keys action for %s', self.identity)
            return set(mappings.SECURE_BOOT_RESET_KEYS_REV)

        return set([mappings.SECURE_BOOT_RESET_KEYS[v] for v in
                    set(mappings.SECURE_BOOT_RESET_KEYS).
                    intersection(reset_action.allowed_values)])

    def reset_keys(self, reset_type):
        """Reset secure boot keys.

        :param reset_type: Reset type, one of `SECORE_BOOT_RESET_KEYS_*`
            constants.
        """
        valid_resets = self.get_allowed_reset_keys_values()
        if reset_type not in valid_resets:
            raise exceptions.InvalidParameterValueError(
                parameter='reset_type', value=reset_type,
                valid_values=valid_resets)

        target_uri = self._get_reset_action_element().target_uri
        self._conn.post(target_uri, data={'ResetKeysType': reset_type})

    def set_enabled(self, enabled):
        """Enable/disable secure boot.

        :param enabled: True, if secure boot is enabled for next boot.
        """
        if not isinstance(enabled, bool):
            raise exceptions.InvalidParameterValueError(
                "Expected a boolean for 'enabled', got %r" % enabled)

        self._conn.patch(self.path, data={'SecureBootEnable': enabled})
