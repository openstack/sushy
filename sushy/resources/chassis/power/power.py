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
# http://redfish.dmtf.org/schemas/v1/Power.v1_3_0.json

from sushy.resources import base
from sushy.resources.chassis.power import constants as pow_cons
from sushy.resources import common
from sushy.resources import constants as res_cons
from sushy import utils


class InputRangeListField(base.ListField):
    """This type describes an input range for a power supply"""

    input_type = base.MappedField('InputType', pow_cons.PowerInputType)
    """The Input type (AC or DC)"""

    maximum_frequency_hz = base.Field('MaximumFrequencyHz',
                                      adapter=utils.int_or_none)
    """The maximum line input frequency at which this power supply input range
    is effective"""

    maximum_voltage = base.Field('MaximumVoltage', adapter=utils.int_or_none)
    """The maximum line input voltage at which this power supply input range
    is effective"""

    minimum_frequency_hz = base.Field('MinimumFrequencyHz',
                                      adapter=utils.int_or_none)
    """The minimum line input frequency at which this power supply input range
    is effective"""

    minimum_voltage = base.Field('MinimumVoltage', adapter=utils.int_or_none)
    """The minimum line input voltage at which this power supply input range
    is effective"""

    output_wattage = base.Field('OutputWattage', adapter=utils.int_or_none)
    """The maximum capacity of this Power Supply when operating in this input
    range"""


class PowerSupplyListField(base.ListField):
    """The power supplies associated with this Power resource"""

    firmware_version = base.Field('FirmwareVersion')
    """The firmware version for this Power Supply"""

    identity = base.Field('MemberId')
    """Identifier of the Power Supply"""

    indicator_led = base.MappedField('IndicatorLed', res_cons.IndicatorLED)
    """The state of the indicator LED, used to identify the power supply"""

    input_ranges = InputRangeListField('InputRanges', default=[])
    """This is the input ranges that the power supply can use"""

    last_power_output_watts = base.Field('LastPowerOutputWatts',
                                         adapter=utils.int_or_none)
    """The average power output of this Power Supply"""

    line_input_voltage = base.Field('LineInputVoltage',
                                    adapter=utils.int_or_none)
    """The line input voltage at which the Power Supply is operating"""

    line_input_voltage_type = base.MappedField('LineInputVoltageType',
                                               pow_cons.LineInputVoltageType)
    """The line voltage type supported as an input to this Power Supply"""

    manufacturer = base.Field('Manufacturer')
    """This is the manufacturer of this power supply"""

    model = base.Field('Model')
    """The model number for this Power Supply"""

    name = base.Field('Name')
    """Name of the Power Supply"""

    part_number = base.Field('PartNumber')
    """The part number for this Power Supply"""

    power_capacity_watts = base.Field('PowerCapacityWatts',
                                      adapter=utils.int_or_none)
    """The maximum capacity of this Power Supply"""

    power_supply_type = base.MappedField('PowerSupplyType',
                                         pow_cons.PowerSupplyType)
    """The Power Supply type (AC or DC)"""

    serial_number = base.Field('SerialNumber')
    """The serial number for this Power Supply"""

    spare_part_number = base.Field('SparePartNumber')
    """The spare part number for this Power Supply"""

    status = common.StatusField('Status')
    """Status of the sensor"""


class Power(base.ResourceBase):
    """This class represents a Power resource."""

    identity = base.Field('Id', required=True)
    """Identifier of the resource"""

    name = base.Field('Name', required=True)
    """The name of the resource"""

    power_supplies = PowerSupplyListField('PowerSupplies', default=[])
    """Details of a power supplies associated with this system or device"""
