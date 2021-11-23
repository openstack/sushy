# -*- coding: utf-8 -*-

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

import json
from unittest import mock

from sushy.resources.chassis.power import constants as pow_cons
from sushy.resources.chassis.power import power
from sushy.resources import constants as res_cons
from sushy.tests.unit import base


class PowerTestCase(base.TestCase):

    def setUp(self):
        super(PowerTestCase, self).setUp()
        self.conn = mock.Mock()
        with open('sushy/tests/unit/json_samples/power.json') as f:
            self.json_doc = json.load(f)

        self.conn.get.return_value.json.return_value = self.json_doc

        self.power = power.Power(
            self.conn, '/redfish/v1/Chassis/MultiBladeEnc1/Power',
            redfish_version='1.5.0')

    def test__parse_attributes(self):
        self.power._parse_attributes(self.json_doc)
        self.assertEqual('1.5.0', self.power.redfish_version)
        self.assertEqual('Power', self.power.identity)
        self.assertEqual('Quad Blade Chassis Power', self.power.name)

        self.assertEqual('0', self.power.power_supplies[0].identity)
        self.assertEqual('Power Supply 0', self.power.power_supplies[0].name)
        self.assertEqual(res_cons.State.ENABLED,
                         self.power.power_supplies[0].status.state)
        self.assertEqual(res_cons.Health.OK,
                         self.power.power_supplies[0].status.health)
        self.assertEqual(pow_cons.PowerSupplyType.AC,
                         self.power.power_supplies[0].power_supply_type)
        self.assertEqual(pow_cons.LineInputVoltageType.AC_240V,
                         self.power.power_supplies[0].line_input_voltage_type)
        self.assertEqual(220, self.power.power_supplies[0].line_input_voltage)
        self.assertEqual(1450,
                         self.power.power_supplies[0].power_capacity_watts)
        self.assertEqual(
            pow_cons.PowerInputType.AC,
            self.power.power_supplies[0].input_ranges[0].input_type
        )
        self.assertEqual(
            185,
            self.power.power_supplies[0].input_ranges[0].minimum_voltage
        )
        self.assertEqual(
            250,
            self.power.power_supplies[0].input_ranges[0].maximum_voltage
        )
        self.assertEqual(
            47,
            self.power.power_supplies[0].input_ranges[0].minimum_frequency_hz
        )
        self.assertEqual(
            63,
            self.power.power_supplies[0].input_ranges[0].maximum_frequency_hz
        )
        self.assertEqual(
            1450,
            self.power.power_supplies[0].input_ranges[0].output_wattage
        )
        self.assertEqual(650,
                         self.power.power_supplies[0].last_power_output_watts)
        self.assertEqual('325457-A06', self.power.power_supplies[0].model)
        self.assertEqual('Cyberdyne',
                         self.power.power_supplies[0].manufacturer)
        self.assertEqual('2.20',
                         self.power.power_supplies[0].firmware_version)
        self.assertEqual('1S0000523',
                         self.power.power_supplies[0].serial_number)
        self.assertEqual('425-591-654',
                         self.power.power_supplies[0].part_number)
        self.assertEqual('425-591-654',
                         self.power.power_supplies[0].spare_part_number)

        self.assertEqual('1', self.power.power_supplies[1].identity)
        self.assertEqual('Power Supply 1', self.power.power_supplies[1].name)
        self.assertEqual(res_cons.State.ENABLED,
                         self.power.power_supplies[1].status.state)
        self.assertEqual(res_cons.Health.OK,
                         self.power.power_supplies[1].status.health)
        self.assertEqual(pow_cons.PowerSupplyType.AC,
                         self.power.power_supplies[1].power_supply_type)
        self.assertEqual(pow_cons.LineInputVoltageType.AC_240V,
                         self.power.power_supplies[1].line_input_voltage_type)
        self.assertEqual(222, self.power.power_supplies[1].line_input_voltage)
        self.assertEqual(1450,
                         self.power.power_supplies[1].power_capacity_watts)
        self.assertEqual(
            pow_cons.PowerInputType.AC,
            self.power.power_supplies[1].input_ranges[0].input_type
        )
        self.assertEqual(
            185,
            self.power.power_supplies[1].input_ranges[0].minimum_voltage
        )
        self.assertEqual(
            250,
            self.power.power_supplies[1].input_ranges[0].maximum_voltage
        )
        self.assertEqual(
            47,
            self.power.power_supplies[1].input_ranges[0].minimum_frequency_hz
        )
        self.assertEqual(
            63,
            self.power.power_supplies[1].input_ranges[0].maximum_frequency_hz
        )
        self.assertEqual(
            1450,
            self.power.power_supplies[1].input_ranges[0].output_wattage
        )
        self.assertEqual(635,
                         self.power.power_supplies[1].last_power_output_watts)
        self.assertEqual('325457-A06', self.power.power_supplies[1].model)
        self.assertEqual('Cyberdyne',
                         self.power.power_supplies[1].manufacturer)
        self.assertEqual('2.20',
                         self.power.power_supplies[1].firmware_version)
        self.assertEqual('1S0000524',
                         self.power.power_supplies[1].serial_number)
        self.assertEqual('425-591-654',
                         self.power.power_supplies[1].part_number)
        self.assertEqual('425-591-654',
                         self.power.power_supplies[1].spare_part_number)

    def test__parse_attributes_return(self):
        attributes = self.power._parse_attributes(self.json_doc)

        # Test that various types are returned correctly
        self.assertEqual('Quad Blade Chassis Power', attributes.get('name'))
        self.assertEqual([{'firmware_version': '2.20',
                           'identity': '0',
                           'indicator_led': None,
                           'input_ranges':
                           [{'input_type': pow_cons.PowerInputType.AC,
                             'maximum_frequency_hz': 63,
                             'maximum_voltage': 250,
                             'minimum_frequency_hz': 47,
                             'minimum_voltage': 185,
                             'output_wattage': 1450}],
                           'last_power_output_watts': 650,
                           'line_input_voltage': 220,
                           'line_input_voltage_type':
                           pow_cons.LineInputVoltageType.AC_240V,
                           'manufacturer': 'Cyberdyne',
                           'model': '325457-A06',
                           'name': 'Power Supply 0',
                           'part_number': '425-591-654',
                           'power_capacity_watts': 1450,
                           'power_supply_type': pow_cons.PowerSupplyType.AC,
                           'serial_number': '1S0000523',
                           'spare_part_number': '425-591-654',
                           'status': {'health': res_cons.Health.OK,
                                      'health_rollup': None,
                                      'state': res_cons.State.ENABLED}},
                          {'firmware_version': '2.20',
                           'identity': '1',
                           'indicator_led': None,
                           'input_ranges':
                           [{'input_type': pow_cons.PowerInputType.AC,
                             'maximum_frequency_hz': 63,
                             'maximum_voltage': 250,
                             'minimum_frequency_hz': 47,
                             'minimum_voltage': 185,
                             'output_wattage': 1450}],
                           'last_power_output_watts': 635,
                           'line_input_voltage': 222,
                           'line_input_voltage_type':
                           pow_cons.LineInputVoltageType.AC_240V,
                           'manufacturer': 'Cyberdyne',
                           'model': '325457-A06',
                           'name': 'Power Supply 1',
                           'part_number': '425-591-654',
                           'power_capacity_watts': 1450,
                           'power_supply_type': pow_cons.PowerSupplyType.AC,
                           'serial_number': '1S0000524',
                           'spare_part_number': '425-591-654',
                           'status': {'health': res_cons.Health.OK,
                                      'health_rollup': None,
                                      'state': res_cons.State.ENABLED}}],
                         attributes.get('power_supplies'))
