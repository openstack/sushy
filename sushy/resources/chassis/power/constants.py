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


# Power Supply Types
POWER_SUPPLY_TYPE_UNKNOWN = 'unknown'
"""The power supply type cannot be determined."""

POWER_SUPPLY_TYPE_AC = 'ac'
"""Alternating Current (AC) power supply."""

POWER_SUPPLY_TYPE_DC = 'dc'
"""Direct Current (DC) power supply."""

POWER_SUPPLY_TYPE_ACDC = 'acdc'
"""Power Supply supports both DC or AC."""

# Line Input Voltage Types
LINE_INPUT_VOLTAGE_TYPE_UNKNOWN = 'unknown'
"""The power supply line input voltage tpye cannot be determined."""

LINE_INPUT_VOLTAGE_TYPE_ACLOW = 'aclowline'
"""100-127V AC input."""

LINE_INPUT_VOLTAGE_TYPE_ACMID = 'acmidline'
"""200-240V AC input."""

LINE_INPUT_VOLTAGE_TYPE_ACHIGH = 'achighline'
"""277V AC input."""

LINE_INPUT_VOLTAGE_TYPE_DCNEG48 = 'dcneg48v'
"""-48V DC input."""

LINE_INPUT_VOLTAGE_TYPE_DC380 = 'dc380v'
"""High Voltage DC input (380V)."""

LINE_INPUT_VOLTAGE_TYPE_AC120 = 'ac120v'
"""AC 120V nominal input."""

LINE_INPUT_VOLTAGE_TYPE_AC240 = 'ac240v'
"""AC 240V nominal input."""

LINE_INPUT_VOLTAGE_TYPE_AC277 = 'ac277v'
"""AC 277V nominal input."""

LINE_INPUT_VOLTAGE_TYPE_ACDCWIDE = 'acdcwiderange'
"""Wide range AC or DC input."""

LINE_INPUT_VOLTAGE_TYPE_ACWIDE = 'acwiderange'
"""Wide range AC input."""

LINE_INPUT_VOLTAGE_TYPE_DC240 = 'dc240v'
"""DC 240V nominal input."""

# Input Types
INPUT_TYPE_AC = 'ac'
"""Alternating Current (AC) input range."""

INPUT_TYPE_DC = 'dc'
"""Direct Current (DC) input range."""
