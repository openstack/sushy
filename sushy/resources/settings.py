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
# http://redfish.dmtf.org/schemas/v1/Settings.v1_0_0.json


from sushy.resources import base
from sushy.resources import common
from sushy.resources import mappings as res_maps


class MessageListField(base.ListField):
    """List of messages with details of settings update status"""

    message_id = base.Field('MessageId', required=True)
    """The key for this message which can be used
    to look up the message in a message registry
    """

    message = base.Field('Message')
    """Human readable message, if provided"""

    severity = base.MappedField('Severity',
                                res_maps.SEVERITY_VALUE_MAP)
    """Severity of the error"""

    resolution = base.Field('Resolution')
    """Used to provide suggestions on how to resolve
    the situation that caused the error
    """

    _related_properties = base.Field('RelatedProperties')
    """List of properties described by the message"""

    message_args = base.Field('MessageArgs')
    """List of message substitution arguments for the message
    referenced by `message_id` from the message registry
    """


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

    messages = MessageListField("Messages")
    """Represents the results of the last time the values of the Settings
    resource were applied to the server"""

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
