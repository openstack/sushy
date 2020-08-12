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
# https://redfish.dmtf.org/schemas/Settings.v1_2_0.json

import logging

from dateutil import parser

from sushy.resources import base
from sushy.resources import common
from sushy.resources import constants as res_cons
from sushy.resources import mappings as res_maps
from sushy.resources.registry import message_registry

# Settings update statuses

UPDATE_UNKNOWN = 0
"""Update status unknown"""

UPDATE_SUCCESS = 1
"""Update was successful"""

UPDATE_FAILURE = 2
"""Update encountered errors"""

UPDATE_PENDING = 3
"""Update waiting for being applied"""

NO_UPDATES = 4
"""No updates made"""


class SettingsUpdate(object):
    """Contains Settings update status and details of the update"""

    def __init__(self, status, messages):
        self._status = status
        self._messages = messages

    @property
    def status(self):
        """The status of the update"""
        return self._status

    @property
    def messages(self):
        """List of :class:`.MessageListField` with messages from the update"""
        return self._messages


LOG = logging.getLogger(__name__)


class MaintenanceWindowField(base.CompositeField):

    maintenance_window_duration_in_seconds = base.Field(
        'MaintenanceWindowDurationInSeconds',
        required=True)
    """The expiry time of maintenance window in seconds"""

    maintenance_window_start_time = base.Field(
        'MaintenanceWindowStartTime',
        required=True,
        adapter=parser.parse)
    """The start time of a maintenance window"""


class SettingsApplyTimeField(base.CompositeField):
    def __init__(self):
        super(SettingsApplyTimeField, self).__init__(
            path="@Redfish.SettingsApplyTime")

    apply_time = base.Field('ApplyTime', adapter=str)
    """When the future configuration should be applied"""

    apply_time_allowable_values = base.Field(
        'ApplyTime@Redfish.AllowableValues', adapter=list)
    """The list of allowable ApplyTime values"""

    maintenance_window_start_time = base.Field('MaintenanceWindowStartTime',
                                               adapter=parser.parse)
    """The start time of a maintenance window"""

    maintenance_window_duration_in_seconds = base.Field(
        'MaintenanceWindowDurationInSeconds', adapter=int)
    """The expiry time of maintenance window in seconds"""


class SettingsField(base.CompositeField):
    """The settings of a resource

    Represents the future state and configuration of the resource. The
    field is added to resources that support future state and
    configuration.

    This field includes several properties to help clients monitor when
    the resource is consumed by the service and determine the results of
    applying the values, which may or may not have been successful.
    """

    def __init__(self):
        super(SettingsField, self).__init__(path="@Redfish.Settings")

    time = base.Field('Time')
    """Indicates the time the settings were applied to the server"""

    _etag = base.Field('ETag')
    """The ETag of the resource to which the settings were applied,
    after the application
    """

    _settings_object_idref = common.IdRefField("SettingsObject")
    """Reference to the resource the client may PUT/PATCH in order
    to change this resource
    """

    _supported_apply_times = base.MappedListField(
        'SupportedApplyTimes',
        res_maps.APPLY_TIME_VALUE_MAP)
    """List of supported apply times"""

    @property
    def maintenance_window(self):
        """MaintenanceWindow field

        Indicates if a given resource has a maintenance window assignment
        for applying settings or operations
        """
        LOG.warning('The @Redfish.MaintenanceWindow annotation does not '
                    'appear within @Redfish.Settings. Instead use the '
                    'maintenance_window property in the target resource '
                    '(e.g. System resource)')
        return None

    messages = base.MessageListField("Messages")
    """Represents the results of the last time the values of the Settings
    resource were applied to the server"""

    @property
    def operation_apply_time_support(self):
        """OperationApplyTimeSupport field

        Indicates if a client is allowed to request for a specific apply
        time of a create, delete, or action operation of a given resource
        """
        LOG.warning('Redfish ApplyTime annotations do not appear within '
                    '@Redfish.Settings. Instead use the apply_time_settings '
                    'property in the target resource (e.g. Bios resource)')
        return None

    def commit(self, connector, value):
        """Commits new settings values

        The new values will be applied when the system or a service
        restarts.

        :param connector: A Connector instance
        :param value: Value representing JSON whose structure is specific
            to each resource and the caller must format it correctly
        """

        connector.patch(self.resource_uri, data=value)

    @property
    def resource_uri(self):
        return self._settings_object_idref.resource_uri

    def get_status(self, registries):
        """Determines the status of last update based

        Uses message id-s and severity to determine the status.

        :param registries: registries to use to parse message
        :returns: :class:`.SettingsUpdate` object containing status
            and any messages
        """

        if not self.time:
            return SettingsUpdate(NO_UPDATES, None)

        parsed_msgs = []
        for m in self.messages:
            parsed_msgs.append(
                message_registry.parse_message(registries, m))
        any_errors = any(m for m in parsed_msgs
                         if not m.severity == res_cons.SEVERITY_OK)

        if any_errors:
            status = UPDATE_FAILURE
        else:
            status = UPDATE_SUCCESS
        return SettingsUpdate(status, parsed_msgs)
