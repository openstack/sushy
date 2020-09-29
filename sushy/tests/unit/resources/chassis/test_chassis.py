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


import sushy
from sushy import exceptions
from sushy.resources.chassis import chassis
from sushy.resources.manager import manager
from sushy.resources.system import system
from sushy.tests.unit import base


class ChassisTestCase(base.TestCase):

    def setUp(self):
        super(ChassisTestCase, self).setUp()
        self.conn = mock.Mock()
        with open('sushy/tests/unit/json_samples/chassis.json') as f:
            self.json_doc = json.load(f)

        self.conn.get.return_value.json.return_value = self.json_doc

        self.chassis = chassis.Chassis(self.conn, '/redfish/v1/Chassis/Blade1',
                                       redfish_version='1.8.0')

    def test__parse_attributes(self):
        # | WHEN |
        self.chassis._parse_attributes(self.json_doc)
        # | THEN |
        self.assertEqual('1.8.0', self.chassis.redfish_version)
        self.assertEqual('Blade1', self.chassis.identity)
        self.assertEqual('Blade', self.chassis.name)
        self.assertEqual('Test description', self.chassis.description)
        self.assertEqual('45Z-2381', self.chassis.asset_tag)
        self.assertEqual(sushy.CHASSIS_TYPE_BLADE,
                         self.chassis.chassis_type)
        self.assertEqual('Contoso', self.chassis.manufacturer)
        self.assertEqual('SX1000', self.chassis.model)
        self.assertEqual('529QB9450R6', self.chassis.serial_number)
        self.assertEqual('6914260', self.chassis.sku)
        self.assertEqual('166480-S23', self.chassis.part_number)
        self.assertEqual('FFFFFFFF-FFFF-FFFF-FFFF-FFFFFFFFFFFF',
                         self.chassis.uuid)
        self.assertEqual(sushy.INDICATOR_LED_OFF,
                         self.chassis.indicator_led)
        self.assertEqual(sushy.POWER_STATE_ON,
                         self.chassis.power_state)
        self.assertEqual(sushy.STATE_ENABLED, self.chassis.status.state)
        self.assertEqual(44.45, self.chassis.height_mm)
        self.assertEqual(431.8, self.chassis.width_mm)
        self.assertEqual(711, self.chassis.depth_mm)
        self.assertEqual(15.31, self.chassis.weight_kg)
        self.assertEqual(sushy.HEALTH_OK, self.chassis.status.health)
        self.assertEqual(sushy.CHASSIS_INTRUSION_SENSOR_NORMAL,
                         self.chassis.physical_security.intrusion_sensor)
        self.assertEqual(123,
                         self.chassis.physical_security.intrusion_sensor_number
                         )
        self.assertEqual(sushy.CHASSIS_INTRUSION_SENSOR_RE_ARM_MANUAL,
                         self.chassis.physical_security.intrusion_sensor_re_arm
                         )

    def test__parse_attributes_return(self):
        attributes = self.chassis._parse_attributes(self.json_doc)

        # Test that various types are returned correctly
        self.assertEqual('Blade', attributes.get('name'))
        self.assertEqual(sushy.INDICATOR_LED_OFF,
                         attributes.get('indicator_led'))
        self.assertEqual(sushy.POWER_STATE_ON, attributes.get('power_state'))
        self.assertEqual({'intrusion_sensor':
                          sushy.CHASSIS_INTRUSION_SENSOR_NORMAL,
                          'intrusion_sensor_number':
                          123,
                          'intrusion_sensor_re_arm':
                          'manual re arm chassis intrusion sensor'},
                         attributes.get('physical_security'))

    def test_get_allowed_reset_chasis_values(self):
        # | GIVEN |
        expected = {sushy.RESET_TYPE_POWER_CYCLE,
                    sushy.RESET_TYPE_PUSH_POWER_BUTTON,
                    sushy.RESET_TYPE_FORCE_ON, sushy.RESET_TYPE_NMI,
                    sushy.RESET_TYPE_FORCE_RESTART,
                    sushy.RESET_TYPE_GRACEFUL_RESTART, sushy.RESET_TYPE_ON,
                    sushy.RESET_TYPE_FORCE_OFF,
                    sushy.RESET_TYPE_GRACEFUL_SHUTDOWN}
        # | WHEN |
        values = self.chassis.get_allowed_reset_chassis_values()
        # | THEN |
        self.assertEqual(expected, values)
        self.assertIsInstance(values, set)

    def test_get_allowed_reset_chassis_values_for_no_values_set(self):
        # | GIVEN |
        self.chassis._actions.reset.allowed_values = []
        expected = {sushy.RESET_TYPE_POWER_CYCLE,
                    sushy.RESET_TYPE_PUSH_POWER_BUTTON,
                    sushy.RESET_TYPE_FORCE_ON, sushy.RESET_TYPE_NMI,
                    sushy.RESET_TYPE_FORCE_RESTART,
                    sushy.RESET_TYPE_GRACEFUL_RESTART, sushy.RESET_TYPE_ON,
                    sushy.RESET_TYPE_FORCE_OFF,
                    sushy.RESET_TYPE_GRACEFUL_SHUTDOWN}
        # | WHEN |
        values = self.chassis.get_allowed_reset_chassis_values()
        # | THEN |
        self.assertEqual(expected, values)
        self.assertIsInstance(values, set)

    def test_get_allowed_reset_chassis_values_missing_action_reset_attr(self):
        # | GIVEN |
        self.chassis._actions.reset = None
        # | WHEN & THEN |
        self.assertRaisesRegex(
            exceptions.MissingActionError, 'action #Chassis.Reset')

    def test_reset_chassis(self):
        self.chassis.reset_chassis(sushy.RESET_TYPE_GRACEFUL_RESTART)
        self.chassis._conn.post.assert_called_once_with(
            '/redfish/v1/Chassis/Blade1/Actions/Chassis.Reset',
            data={'ResetType': 'GracefulRestart'})

    def test_reset_chassis_with_invalid_value(self):
        self.assertRaises(exceptions.InvalidParameterValueError,
                          self.chassis.reset_chassis, 'invalid-value')

    def test_set_indicator_led(self):
        with mock.patch.object(
                self.chassis, 'invalidate', autospec=True) as invalidate_mock:
            self.chassis.set_indicator_led(sushy.INDICATOR_LED_BLINKING)
            self.chassis._conn.patch.assert_called_once_with(
                '/redfish/v1/Chassis/Blade1',
                data={'IndicatorLED': 'Blinking'})

            invalidate_mock.assert_called_once_with()

    def test_set_indicator_led_invalid_state(self):
        self.assertRaises(exceptions.InvalidParameterValueError,
                          self.chassis.set_indicator_led,
                          'spooky-glowing')

    def test_managers(self):
        # | GIVEN |
        with open('sushy/tests/unit/json_samples/'
                  'manager.json') as f:
            self.conn.get.return_value.json.return_value = json.load(f)

        # | WHEN & THEN |
        actual_managers = self.chassis.managers
        self.assertIsInstance(actual_managers[0], manager.Manager)
        self.assertEqual(
            '/redfish/v1/Managers/Blade1BMC', actual_managers[0].path)

    def test_systems(self):
        # | GIVEN |
        with open('sushy/tests/unit/json_samples/'
                  'system.json') as f:
            self.conn.get.return_value.json.return_value = json.load(f)

        # | WHEN & THEN |
        actual_systems = self.chassis.systems
        self.assertIsInstance(actual_systems[0], system.System)
        self.assertEqual(
            '/redfish/v1/Systems/529QB9450R6', actual_systems[0].path)


class ChassisCollectionTestCase(base.TestCase):

    def setUp(self):
        super(ChassisCollectionTestCase, self).setUp()
        self.conn = mock.Mock()
        with open('sushy/tests/unit/json_samples/'
                  'chassis_collection.json') as f:
            self.conn.get.return_value.json.return_value = json.load(f)
        self.chassis = chassis.ChassisCollection(
            self.conn, '/redfish/v1/Chassis', redfish_version='1.5.0')

    @mock.patch.object(chassis, 'Chassis', autospec=True)
    def test_get_member(self, chassis_mock):
        self.chassis.get_member('/redfish/v1/Chassis/MultiBladeEncl')
        chassis_mock.assert_called_once_with(
            self.chassis._conn, '/redfish/v1/Chassis/MultiBladeEncl',
            self.chassis.redfish_version, None)

    @mock.patch.object(chassis, 'Chassis', autospec=True)
    def test_get_members(self, chassis_mock):
        members = self.chassis.get_members()
        calls = [
            mock.call(self.chassis._conn, '/redfish/v1/Chassis/MultiBladeEncl',
                      self.chassis.redfish_version, None),
            mock.call(self.chassis._conn, '/redfish/v1/Chassis/Blade1',
                      self.chassis.redfish_version, None),
            mock.call(self.chassis._conn, '/redfish/v1/Chassis/Blade2',
                      self.chassis.redfish_version, None),
            mock.call(self.chassis._conn, '/redfish/v1/Chassis/Blade3',
                      self.chassis.redfish_version, None),
            mock.call(self.chassis._conn, '/redfish/v1/Chassis/Blade4',
                      self.chassis.redfish_version, None)
        ]
        chassis_mock.assert_has_calls(calls)
        self.assertIsInstance(members, list)
        self.assertEqual(5, len(members))
