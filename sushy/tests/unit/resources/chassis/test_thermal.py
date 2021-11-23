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

from sushy.resources.chassis.thermal import constants as the_cons
from sushy.resources.chassis.thermal import thermal
from sushy.resources import constants as res_cons
from sushy.tests.unit import base


class ThermalTestCase(base.TestCase):

    def setUp(self):
        super(ThermalTestCase, self).setUp()
        self.conn = mock.Mock()
        with open('sushy/tests/unit/json_samples/thermal.json') as f:
            self.json_doc = json.load(f)

        self.conn.get.return_value.json.return_value = self.json_doc

        self.thermal = thermal.Thermal(
            self.conn, '/redfish/v1/Chassis/Blade1/Thermal',
            redfish_version='1.5.0')

    def test__parse_attributes(self):
        self.thermal._parse_attributes(self.json_doc)
        self.assertEqual('1.5.0', self.thermal.redfish_version)
        self.assertEqual('Thermal', self.thermal.identity)
        self.assertEqual('Blade Thermal', self.thermal.name)

        self.assertEqual('0', self.thermal.fans[0].identity)
        self.assertEqual('CPU Fan', self.thermal.fans[0].name)
        self.assertEqual('CPU', self.thermal.fans[0].physical_context)
        self.assertEqual(res_cons.State.ENABLED,
                         self.thermal.fans[0].status.state)
        self.assertEqual(res_cons.Health.OK,
                         self.thermal.fans[0].status.health)
        self.assertEqual(6000, self.thermal.fans[0].reading)
        self.assertEqual(the_cons.FanReadingUnit.RPM,
                         self.thermal.fans[0].reading_units)
        self.assertEqual(2000, self.thermal.fans[0].lower_threshold_fatal)
        self.assertEqual(0, self.thermal.fans[0].min_reading_range)
        self.assertEqual(10000, self.thermal.fans[0].max_reading_range)

        self.assertEqual('0', self.thermal.temperatures[0].identity)
        self.assertEqual('CPU Temp', self.thermal.temperatures[0].name)
        self.assertEqual(res_cons.State.ENABLED,
                         self.thermal.temperatures[0].status.state)
        self.assertEqual(res_cons.Health.OK,
                         self.thermal.temperatures[0].status.health)
        self.assertEqual(62, self.thermal.temperatures[0].reading_celsius)
        self.assertEqual(
            75,
            self.thermal.temperatures[0].upper_threshold_non_critical
        )
        self.assertEqual(
            90,
            self.thermal.temperatures[0].upper_threshold_critical
        )
        self.assertEqual(
            95,
            self.thermal.temperatures[0].upper_threshold_fatal
        )
        self.assertEqual(0,
                         self.thermal.temperatures[0].min_reading_range_temp)
        self.assertEqual(120,
                         self.thermal.temperatures[0].max_reading_range_temp)
        self.assertEqual('CPU', self.thermal.temperatures[0].physical_context)

    def test__parse_attributes_return(self):
        attributes = self.thermal._parse_attributes(self.json_doc)

        # Test that various types are returned correctly
        self.assertEqual([{'identity': '0',
                           'indicator_led': None,
                           'lower_threshold_critical': None,
                           'lower_threshold_fatal': 2000,
                           'lower_threshold_non_critical': None,
                           'manufacturer': None,
                           'max_reading_range': 10000,
                           'min_reading_range': 0,
                           'model': None,
                           'name': 'CPU Fan',
                           'part_number': None,
                           'physical_context': 'CPU',
                           'reading': 6000,
                           'reading_units': the_cons.FanReadingUnit.RPM,
                           'serial_number': None,
                           'status':
                           {'health': res_cons.Health.OK,
                            'health_rollup': None,
                            'state': res_cons.State.ENABLED},
                           'upper_threshold_critical': None,
                           'upper_threshold_fatal': None,
                           'upper_threshold_non_critical': None}],
                         attributes.get('fans'))
        self.assertEqual([{'identity': '0',
                           'lower_threshold_critical': None,
                           'lower_threshold_fatal': None,
                           'lower_threshold_non_critical': None,
                           'max_allowable_operating_value': None,
                           'max_reading_range_temp': 120,
                           'min_allowable_operating_value': None,
                           'min_reading_range_temp': 0,
                           'name': 'CPU Temp',
                           'physical_context': 'CPU',
                           'reading_celsius': 62,
                           'sensor_number': None,
                           'status': {'health': res_cons.Health.OK,
                                      'health_rollup': None,
                                      'state': res_cons.State.ENABLED},
                           'upper_threshold_critical': 90,
                           'upper_threshold_fatal': 95,
                           'upper_threshold_non_critical': 75}],
                         attributes.get('temperatures'))
