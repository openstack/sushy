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
# http://redfish.dmtf.org/schemas/v1/Thermal.v1_3_0.json

from sushy.resources import base
from sushy.resources.chassis.thermal import constants as the_cons
from sushy.resources import common
from sushy.resources import constants as res_cons
from sushy import utils


class Sensor(base.ListField):
    """The sensor device/s associated with Thermal."""

    identity = base.Field('MemberId', required=True)
    """Identifier of the Sensor"""

    lower_threshold_critical = base.Field('LowerThresholdCritical',
                                          adapter=utils.int_or_none)
    """Below normal range but not yet fatal"""

    lower_threshold_fatal = base.Field('LowerThresholdFatal',
                                       adapter=utils.int_or_none)
    """Below normal range and is fatal"""

    lower_threshold_non_critical = base.Field('LowerThresholdNonCritical',
                                              adapter=utils.int_or_none)
    """Below normal range"""

    name = base.Field('Name')
    """The name of this sensor"""

    physical_context = base.Field('PhysicalContext')
    """Area or device associated with this sensor"""

    status = common.StatusField('Status')
    """Status of the sensor"""

    upper_threshold_critical = base.Field('UpperThresholdCritical',
                                          adapter=utils.int_or_none)
    """Above normal range but not yet fatal"""

    upper_threshold_fatal = base.Field('UpperThresholdFatal',
                                       adapter=utils.int_or_none)
    """Above normal range and is fatal"""

    upper_threshold_non_critical = base.Field('UpperThresholdNonCritical',
                                              adapter=utils.int_or_none)
    """Above normal range"""


class FansListField(Sensor):
    """The Fan device/s associated with Thermal."""

    indicator_led = base.MappedField('IndicatorLED', res_cons.IndicatorLED)
    """The state of the indicator LED, used to identify the fan"""

    manufacturer = base.Field('Manufacturer')
    """This is the manufacturer of this Fan"""

    max_reading_range = base.Field('MaxReadingRange',
                                   adapter=utils.int_or_none)
    """Maximum value for Reading"""

    min_reading_range = base.Field('MinReadingRange',
                                   adapter=utils.int_or_none)
    """Minimum value for Reading"""

    model = base.Field('Model')
    """The model of this Fan"""

    part_number = base.Field('PartNumber')
    """Part number of this Fan"""

    reading = base.Field('Reading', adapter=utils.int_or_none)
    """Current Fan Speed"""

    reading_units = base.MappedField('ReadingUnits', the_cons.FanReadingUnit)
    """Units in which the reading and thresholds are measured"""

    serial_number = base.Field('SerialNumber')
    """Serial number of this Fan"""


class TemperaturesListField(Sensor):
    """The Temperature device/s associated with Thermal."""

    max_allowable_operating_value = base.Field('MaxAllowableOperatingValue',
                                               adapter=utils.int_or_none)
    """Maximum allowable operating temperature for this equipment"""

    min_allowable_operating_value = base.Field('MinAllowableOperatingValue',
                                               adapter=utils.int_or_none)
    """Minimum allowable operating temperature for this equipment"""

    max_reading_range_temp = base.Field('MaxReadingRangeTemp')
    """Maximum value for ReadingCelsius"""

    min_reading_range_temp = base.Field('MinReadingRangeTemp')
    """Minimum value for ReadingCelsius"""

    reading_celsius = base.Field('ReadingCelsius')
    """Temperature"""

    sensor_number = base.Field('SensorNumber', adapter=utils.int_or_none)
    """A numerical identifier to represent the temperature sensor"""


class Thermal(base.ResourceBase):
    """This class represents a Thermal resource."""

    identity = base.Field('Id')
    """Identifier of the resource"""

    name = base.Field('Name')
    """The name of the resource"""

    status = common.StatusField('Status')
    """Status of the resource"""

    fans = FansListField('Fans', default=[])
    """A tuple of Fan identities"""

    temperatures = TemperaturesListField('Temperatures', default=[])
    """A tuple of Temperature identities"""
