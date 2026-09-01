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

import logging

from dateutil import parser

from sushy import exceptions
from sushy.resources import base
from sushy.resources import constants

LOG = logging.getLogger(__name__)


class IdRefField(base.CompositeField):
    """Reference to the resource odata identity field."""

    resource_uri = base.Field('@odata.id')
    """The unique identifier for a resource"""


class OperationApplyTimeSupportField(base.CompositeField):
    def __init__(self):
        super().__init__(path="@Redfish.OperationApplyTimeSupport")

    maintenance_window_duration_in_seconds = base.Field(
        'MaintenanceWindowDurationInSeconds', adapter=int)
    """The expiry time of maintenance window in seconds"""

    _maintenance_window_resource = IdRefField('MaintenanceWindowResource')
    """The location of the maintenance window settings"""

    maintenance_window_start_time = base.Field(
        'MaintenanceWindowStartTime',
        adapter=parser.parse)
    """The start time of a maintenance window"""

    supported_values = base.Field('SupportedValues', required=True,
                                  adapter=list)
    """The types of apply times that the client is allowed request when
    performing a create, delete, or action operation returned as an unmapped
    list

    Deprecated: Use `mapped_supported_values`.
    """

    mapped_supported_values = base.MappedListField(
        'SupportedValues', constants.ApplyTime, required=True)
    """The types of apply times that the client is allowed request when
    performing a create, delete, or action operation returned as a mapped
    list"""


class ActionField(base.CompositeField):
    target_uri = base.Field('target', required=True)
    operation_apply_time_support = OperationApplyTimeSupportField()


class ParametersListField(base.ListField):
    """The parameters listed by an ActionInfo resource."""

    name = base.Field('Name')
    allowed_values = base.Field('AllowableValues', adapter=list)


class ActionInfo(base.ResourceBase):
    """The resource an action can point at to describe its parameters.

    Services that do not annotate an action's allowable values on the action
    itself link to one of these instead.
    """

    parameters = ParametersListField('Parameters', default=[])

    @classmethod
    def from_uri(cls, resource, uri):
        """Fetch the ActionInfo resource an action points at.

        :param resource: the resource the action belongs to, for its
            connection to the BMC.
        :param uri: the action's ``@Redfish.ActionInfo`` annotation.
        :returns: an `ActionInfo`, or None if it cannot be read.
        """
        try:
            return cls(resource._conn, uri,
                       redfish_version=resource.redfish_version,
                       registries=resource.registries, root=resource.root)

        # A service can answer with something not shaped like an ActionInfo,
        # which the field machinery raises TypeError rather than SushyError for
        except (exceptions.SushyError, TypeError) as exc:
            LOG.warning('Could not read the ActionInfo resource at %s: %s',
                        uri, exc)
            return None

    def get_allowable_values(self, parameter):
        """Get the values the given parameter accepts.

        :param parameter: name of the parameter, e.g. ``ResetType``.
        :returns: a list of allowed values, or None if this resource does not
            constrain the parameter.
        """
        return next((p.allowed_values for p in self.parameters
                     if p.name == parameter), None)


class ResetActionField(ActionField):
    allowed_values = base.Field('ResetType@Redfish.AllowableValues',
                                adapter=list)

    action_info_uri = base.Field('@Redfish.ActionInfo')
    """Where a service publishes the values instead of annotating them."""

    def get_allowed_values(self, resource):
        """Get the reset types this action accepts.

        :param resource: the resource this action belongs to, used to fetch
            the ActionInfo resource if the action points at one.
        :returns: a list of allowed values, or None if the service does not
            make them known.
        """
        if self.allowed_values or not self.action_info_uri:
            return self.allowed_values

        action_info = ActionInfo.from_uri(resource, self.action_info_uri)

        return (action_info.get_allowable_values('ResetType')
                if action_info else None)


class InitializeActionField(ActionField):
    allowed_values = base.Field('InitializeType@Redfish.AllowableValues',
                                adapter=list)


class StatusField(base.CompositeField):
    """This Field describes the status of a resource and its children.

    This field shall contain any state or health properties of a resource.
    """
    health = base.MappedField('Health', constants.Health)
    """Represents health of resource w/o considering its dependent resources"""

    health_rollup = base.MappedField('HealthRollup', constants.Health)
    """Represents health state of resource and its dependent resources"""

    state = base.MappedField('State', constants.State)
    """Indicates the known state of the resource, such as if it is enabled."""


class IdentifiersListField(base.ListField):
    """This type describes any additional identifiers for a resource."""

    durable_name = base.Field('DurableName')
    """This indicates the world wide, persistent name of the resource."""

    durable_name_format = base.MappedField('DurableNameFormat',
                                           constants.DurableNameFormat)
    """This represents the format of the DurableName property."""
