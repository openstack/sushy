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

# Values comes from the Redfish System json-schema 1.0.0:
# http://redfish.dmtf.org/schemas/v1/Resource.json or
# https://redfish.dmtf.org/schemas/v1/MessageRegistry.v1_1_1.json

# Health related constants.
HEALTH_OK = 'ok'
HEALTH_WARNING = 'warning'
HEALTH_CRITICAL = 'critical'

# State related constants.
STATE_ENABLED = 'enabled'
STATE_DISABLED = 'disabled'
STATE_STANDBYOFFLINE = 'standby offline'
STATE_STANDBYSPARE = 'standby spare'
STATE_INTEST = 'in test'
STATE_STARTING = 'starting'
STATE_ABSENT = 'absent'
STATE_UNAVAILABLEOFFLINE = 'unavailable offline'
STATE_DEFERRING = 'deferring'
STATE_QUIESCED = 'quiesced'
STATE_UPDATING = 'updating'

# Message Registry message parameter type related constants.
PARAMTYPE_STRING = 'string'
PARAMTYPE_NUMBER = 'number'

# Severity related constants
SEVERITY_OK = 'ok'
SEVERITY_WARNING = 'warning'
SEVERITY_CRITICAL = 'critical'
