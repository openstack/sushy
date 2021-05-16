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

from sushy.resources.eventservice import constants as evt_cons


EVENT_TYPE_VALUE_MAP = {
    'StatusChange': evt_cons.EVENT_TYPE_STATUS_CHANGE,
    'ResourceAdded': evt_cons.EVENT_TYPE_RESOURCE_ADDED,
    'ResourceRemoved': evt_cons.EVENT_TYPE_RESOURCE_REMOVED,
    'ResourceUpdated': evt_cons.EVENT_TYPE_RESOURCE_UPDATED,
    'Alert': evt_cons.EVENT_TYPE_ALERT,
    'MetricReport': evt_cons.EVENT_TYPE_METRIC_REPORT,
    'Other': evt_cons.EVENT_TYPE_OTHER
}
