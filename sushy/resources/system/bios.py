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
# https://redfish.dmtf.org/schemas/Bios.v1_0_3.json

from http import client as http_client
import logging

from sushy import exceptions
from sushy.resources import base
from sushy.resources import common
from sushy.resources import settings
from sushy import utils

LOG = logging.getLogger(__name__)


class ActionsField(base.CompositeField):
    change_password = common.ActionField('#Bios.ChangePassword')
    reset_bios = common.ActionField('#Bios.ResetBios')


class Bios(base.ResourceBase):

    def __init__(self, connector, path, redfish_version=None, registries=None,
                 root=None):
        """A class representing a Bios

        :param connector: A Connector instance
        :param path: Sub-URI path to the Bios resource
        :param registries: Dict of message registries to be used when
            parsing messages of attribute update status
        :param root: Sushy root object. Empty for Sushy root itself.
        """
        super(Bios, self).__init__(
            connector, path, redfish_version=redfish_version,
            registries=registries, root=root)

    identity = base.Field('Id', required=True)
    """The Bios resource identity string"""

    name = base.Field('Name')
    """The name of the resource"""

    description = base.Field('Description')
    """Human-readable description of the BIOS resource"""

    _attribute_registry = base.Field('AttributeRegistry')
    """The Resource ID of the Attribute Registry
    for the BIOS Attributes resource
    """

    _settings = settings.SettingsField()
    """Results of last BIOS attribute update"""

    attributes = base.Field('Attributes')
    """Vendor-specific key-value dict of effective BIOS attributes

    Attributes cannot be updated directly.
    To update use :py:func:`~set_attribute` or :py:func:`~set_attributes`
    """

    maintenance_window = settings.MaintenanceWindowField(
        '@Redfish.MaintenanceWindow')
    """Indicates if a given resource has a maintenance window assignment
    for applying settings or operations"""

    _actions = ActionsField('Actions')

    _apply_time_settings = settings.SettingsApplyTimeField()

    @property
    @utils.cache_it
    def _pending_settings_resource(self):
        """Pending BIOS settings resource"""
        return Bios(
            self._conn, self._settings.resource_uri,
            registries=None,
            redfish_version=self.redfish_version, root=self.root)

    @property
    def pending_attributes(self):
        """Pending BIOS attributes

        BIOS attributes that have been committed to the system,
        but for them to take effect system restart is necessary
        """
        return self._pending_settings_resource.attributes

    @property
    def apply_time_settings(self):
        return self._pending_settings_resource._apply_time_settings

    def set_attribute(self, key, value, apply_time=None,
                      maint_window_start_time=None,
                      maint_window_duration=None):
        """Update an attribute

        Attribute update is not immediate but requires system restart.
        Committed attributes can be checked at :py:attr:`~pending_attributes`
        property

        :param key: Attribute name
        :param value: Attribute value
        :param apply_time: When to update the attribute. Optional.
            An :py:class:`sushy.ApplyTime` value.
        :param maint_window_start_time: The start time of a maintenance window,
            datetime. Required when updating during maintenance window and
            default maintenance window not set by the system.
        :param maint_window_duration: Duration of maintenance time since
            maintenance window start time in seconds. Required when updating
            during maintenance window and default maintenance window not
            set by the system.
        """
        self.set_attributes({key: value}, apply_time, maint_window_start_time,
                            maint_window_duration)

    def set_attributes(self, value, apply_time=None,
                       maint_window_start_time=None,
                       maint_window_duration=None):
        """Update many attributes at once

        Attribute update is not immediate but requires system restart.
        Committed attributes can be checked at :py:attr:`~pending_attributes`
        property

        :param value: Key-value pairs for attribute name and value
        :param apply_time: When to update the attributes. Optional.
            An :py:class:`sushy.ApplyTime` value.
        :param maint_window_start_time: The start time of a maintenance window,
            datetime. Required when updating during maintenance window and
            default maintenance window not set by the system.
        :param maint_window_duration: Duration of maintenance time since
            maintenance window start time in seconds. Required when updating
            during maintenance window and default maintenance window not
            set by the system.
        """
        payload = {'Attributes': value}
        payload = utils.process_apply_time_input(
            payload, apply_time, maint_window_start_time,
            maint_window_duration)
        # NOTE(vanou): To retrieve current ETag value of @Redfish.Settings
        # but not update cached _pending_settings_resource, because cached
        # property is only this one and re-cache is not required
        self.refresh(force=False)
        self._settings.commit(self._conn,
                              payload)
        utils.cache_clear(self, force_refresh=False,
                          only_these=['_pending_settings_resource'])

    def _get_reset_bios_action_element(self):
        actions = self._actions

        if not actions:
            raise exceptions.MissingAttributeError(attribute="Actions",
                                                   resource=self._path)

        reset_bios_action = actions.reset_bios

        if not reset_bios_action:
            raise exceptions.MissingActionError(action='#Bios.ResetBios',
                                                resource=self._path)
        return reset_bios_action

    def _get_change_password_element(self):
        actions = self._actions

        if not actions:
            raise exceptions.MissingAttributeError(attribute="Actions",
                                                   resource=self._path)

        change_password_action = actions.change_password

        if not change_password_action:
            raise exceptions.MissingActionError(action='#Bios.ChangePassword',
                                                resource=self._path)
        return change_password_action

    def reset_bios(self):
        """Reset the BIOS attributes to default"""

        target_uri = self._get_reset_bios_action_element().target_uri

        LOG.debug('Resetting BIOS attributes %s ...', self.identity)
        try:
            self._conn.post(target_uri)
        except exceptions.HTTPError as resp:
            # Send empty payload, if BMC expects body
            if resp.status_code in [http_client.UNSUPPORTED_MEDIA_TYPE,
                                    http_client.BAD_REQUEST]:
                self._conn.post(target_uri, data={})
            else:
                raise

        LOG.info('BIOS attributes %s is being reset', self.identity)

    def change_password(self, new_password, old_password, password_name):
        """Change BIOS password"""

        target_uri = self._get_change_password_element().target_uri

        LOG.debug('Changing BIOS password %s ...', self.identity)
        self._conn.post(target_uri, data={'NewPassword': new_password,
                                          'OldPassword': old_password,
                                          'PasswordName': password_name})
        LOG.info('BIOS password %s is being changed', self.identity)

    @property
    def update_status(self):
        """Status of the last attribute update

        :returns: :class:`sushy.resources.settings.SettingsUpdate` object
            containing status and any messages
        """
        return self._settings.get_status(self._registries)

    @property
    def supported_apply_times(self):
        """List of supported BIOS update apply times

        :returns: List of supported update apply time names
        """
        return self._settings._supported_apply_times

    def get_attribute_registry(self, language='en'):
        """Get the Attribute Registry associated with this BIOS instance

        :param language: RFC 5646 language code for Message Registries.
            Indicates language of registry to be used. Defaults to 'en'.
        :returns: the BIOS Attribute Registry
        """
        return self._get_registry(self._attribute_registry,
                                  language=language,
                                  description='BIOS attribute registry')
