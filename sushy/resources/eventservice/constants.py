# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# EventType constants
# http://redfish.dmtf.org/schemas/v1/Event.json#/definitions/EventType
# https://redfish.dmtf.org/schemas/v1/EventService.v1_0_6.json

import enum


class EventType(enum.Enum):

    STATUS_CHANGE = 'StatusChange'
    """The status of a resource has changed."""

    RESOURCE_UPDATED = 'ResourceUpdated'
    """A resource has been updated."""

    RESOURCE_ADDED = 'ResourceAdded'
    """A resource has been added."""

    RESOURCE_REMOVED = 'ResourceRemoved'
    """A resource has been removed."""

    ALERT = 'Alert'
    """A condition requires attention."""

    METRIC_REPORT = 'MetricReport'
    """The telemetry service is sending a metric report."""

    OTHER = 'Other'
    """Because EventType is deprecated as of Redfish Specification v1.6, the
    event is based on a registry or resource but not an EventType."""


# Backward compatibility
EVENT_TYPE_STATUS_CHANGE = EventType.STATUS_CHANGE
EVENT_TYPE_RESOURCE_UPDATED = EventType.RESOURCE_UPDATED
EVENT_TYPE_RESOURCE_ADDED = EventType.RESOURCE_ADDED
EVENT_TYPE_RESOURCE_REMOVED = EventType.RESOURCE_REMOVED
EVENT_TYPE_ALERT = EventType.ALERT
EVENT_TYPE_METRIC_REPORT = EventType.METRIC_REPORT
EVENT_TYPE_OTHER = EventType.OTHER
