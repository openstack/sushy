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

EVENT_TYPE_STATUS_CHANGE = "Status Change"
"""The status of a resource has changed"""

EVENT_TYPE_RESOURCE_ADDED = "Resource Added"
"""A resource has been added."""

EVENT_TYPE_RESOURCE_REMOVED = "Resource Removed"
"""A resource has been removed"""

EVENT_TYPE_RESOURCE_UPDATED = "Resource Updated"
"""A resource has been updated"""

EVENT_TYPE_ALERT = "Alert"
"""A condition requires attention"""

EVENT_TYPE_METRIC_REPORT = "Metric Report"
"""The telemetry service is sending a metric report"""

EVENT_TYPE_OTHER = "Other"
"""Because EventType is deprecated as of Redfish Specification v1.6,
the event is based on a registry or resource but not an EventType."""
