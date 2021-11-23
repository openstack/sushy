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
# https://redfish.dmtf.org/schemas/v1/Power.v1_7_1.json

import enum


class PowerSupplyType(enum.Enum):
    UNKNOWN = 'Unknown'
    """The power supply type cannot be determined."""

    AC = 'AC'
    """Alternating Current (AC) power supply."""

    DC = 'DC'
    """Direct Current (DC) power supply."""

    AC_OR_DC = 'ACorDC'
    """The power supply supports both DC or AC."""


# Backward compatibility
POWER_SUPPLY_TYPE_UNKNOWN = PowerSupplyType.UNKNOWN
POWER_SUPPLY_TYPE_AC = PowerSupplyType.AC
POWER_SUPPLY_TYPE_DC = PowerSupplyType.DC
POWER_SUPPLY_TYPE_ACDC = PowerSupplyType.AC_OR_DC


class LineInputVoltageType(enum.Enum):
    UNKNOWN = 'Unknown'
    """The power supply line input voltage type cannot be determined."""

    AC_LOW_LINE = 'ACLowLine'
    """100-127V AC input."""

    AC_MID_LINE = 'ACMidLine'
    """200-240V AC input."""

    AC_HIGH_LINE = 'ACHighLine'
    """277V AC input."""

    DC_NEG48V = 'DCNeg48V'
    """-48V DC input."""

    DC_380V = 'DC380V'
    """High Voltage DC input (380V)."""

    AC_120V = 'AC120V'
    """AC 120V nominal input."""

    AC_240V = 'AC240V'
    """AC 240V nominal input."""

    AC_277V = 'AC277V'
    """AC 277V nominal input."""

    AC_AND_DC_WIDE_RANGE = 'ACandDCWideRange'
    """Wide range AC or DC input."""

    AC_WIDE_RANGE = 'ACWideRange'
    """Wide range AC input."""

    DC_240V = 'DC240V'
    """DC 240V nominal input."""


# Backward compatibility
LINE_INPUT_VOLTAGE_TYPE_UNKNOWN = LineInputVoltageType.UNKNOWN
LINE_INPUT_VOLTAGE_TYPE_ACLOW = LineInputVoltageType.AC_LOW_LINE
LINE_INPUT_VOLTAGE_TYPE_ACMID = LineInputVoltageType.AC_MID_LINE
LINE_INPUT_VOLTAGE_TYPE_ACHIGH = LineInputVoltageType.AC_HIGH_LINE
LINE_INPUT_VOLTAGE_TYPE_DCNEG48 = LineInputVoltageType.DC_NEG48V
LINE_INPUT_VOLTAGE_TYPE_DC380V = LineInputVoltageType.DC_380V
LINE_INPUT_VOLTAGE_TYPE_AC120V = LineInputVoltageType.AC_120V
LINE_INPUT_VOLTAGE_TYPE_AC240V = LineInputVoltageType.AC_240V
LINE_INPUT_VOLTAGE_TYPE_AC277V = LineInputVoltageType.AC_277V
LINE_INPUT_VOLTAGE_TYPE_ACDCWIDE = LineInputVoltageType.AC_AND_DC_WIDE_RANGE
LINE_INPUT_VOLTAGE_TYPE_ACWIDE = LineInputVoltageType.AC_WIDE_RANGE
LINE_INPUT_VOLTAGE_TYPE_DC240V = LineInputVoltageType.DC_240V


class PowerInputType(enum.Enum):
    AC = 'AC'
    """Alternating Current (AC) input range."""

    DC = 'DC'
    """Direct Current (DC) input range."""


# Backward compatibility
INPUT_TYPE_AC = PowerInputType.AC
INPUT_TYPE_DC = PowerInputType.DC
