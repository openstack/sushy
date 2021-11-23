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

# Values comes from the Redfish Chassis json-schema:
# https://redfish.dmtf.org/schemas/v1/Thermal.v1_7_1.json

import enum


class FanReadingUnit(enum.Enum):

    RPM = 'RPM'
    """The fan reading and thresholds are measured in revolutions per
    minute."""

    PERCENT = 'Percent'
    """The fan reading and thresholds are measured as a percentage."""


# Backward compatibility
FAN_READING_UNIT_PERCENTAGE = FanReadingUnit.PERCENT
FAN_READING_UNIT_RPM = FanReadingUnit.RPM
