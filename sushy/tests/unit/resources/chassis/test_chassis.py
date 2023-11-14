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
from sushy.resources.system.network import adapter
from sushy.resources.system import system
from sushy.tests.unit import base


class ChassisTestCase(base.TestCase):

    def setUp(self):
        super(ChassisTestCase, self).setUp()
        self.conn = mock.Mock()
        with open('sushy/tests/unit/json_samples/chassis.json') as f:
            self.json_doc = json.load(f)

        self.conn.get.return_value.json.return_value = self.json_doc
        self.conn.get.return_value.headers = {'ETag': 'd37f7bcd528e4d59'}

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
        self.assertEqual(sushy.ChassisType.BLADE, self.chassis.chassis_type)
        self.assertEqual('Contoso', self.chassis.manufacturer)
        self.assertEqual('SX1000', self.chassis.model)
        self.assertEqual('529QB9450R6', self.chassis.serial_number)
        self.assertEqual('6914260', self.chassis.sku)
        self.assertEqual('166480-S23', self.chassis.part_number)
        self.assertEqual('FFFFFFFF-FFFF-FFFF-FFFF-FFFFFFFFFFFF',
                         self.chassis.uuid)
        self.assertEqual(sushy.IndicatorLED.OFF,
                         self.chassis.indicator_led)
        self.assertEqual(sushy.PowerState.ON, self.chassis.power_state)
        self.assertEqual(sushy.State.ENABLED, self.chassis.status.state)
        self.assertEqual(44.45, self.chassis.height_mm)
        self.assertEqual(431.8, self.chassis.width_mm)
        self.assertEqual(711, self.chassis.depth_mm)
        self.assertEqual(15.31, self.chassis.weight_kg)
        self.assertEqual(sushy.Health.OK, self.chassis.status.health)
        self.assertEqual(sushy.IntrusionSensor.NORMAL,
                         self.chassis.physical_security.intrusion_sensor)
        self.assertEqual(123,
                         self.chassis.physical_security.intrusion_sensor_number
                         )
        self.assertEqual(sushy.IntrusionSensorReArm.MANUAL,
                         self.chassis.physical_security.intrusion_sensor_re_arm
                         )

    def test__parse_attributes_return(self):
        attributes = self.chassis._parse_attributes(self.json_doc)

        # Test that various types are returned correctly
        self.assertEqual('Blade', attributes.get('name'))
        self.assertEqual(sushy.IndicatorLED.OFF,
                         attributes.get('indicator_led'))
        self.assertEqual(sushy.PowerState.ON, attributes.get('power_state'))
        self.assertEqual({'intrusion_sensor': sushy.IntrusionSensor.NORMAL,
                          'intrusion_sensor_number': 123,
                          'intrusion_sensor_re_arm':
                          sushy.IntrusionSensorReArm.MANUAL},
                         attributes.get('physical_security'))

    def test_get_allowed_reset_chasis_values(self):
        # | GIVEN |
        expected = {sushy.ResetType.POWER_CYCLE,
                    sushy.ResetType.PUSH_POWER_BUTTON,
                    sushy.ResetType.FORCE_ON, sushy.ResetType.NMI,
                    sushy.ResetType.FORCE_RESTART,
                    sushy.ResetType.GRACEFUL_RESTART, sushy.ResetType.ON,
                    sushy.ResetType.FORCE_OFF,
                    sushy.ResetType.GRACEFUL_SHUTDOWN}
        # | WHEN |
        values = self.chassis.get_allowed_reset_chassis_values()
        # | THEN |
        self.assertEqual(expected, values)
        self.assertIsInstance(values, set)

    def test_get_allowed_reset_chassis_values_for_no_values_set(self):
        # | GIVEN |
        self.chassis._actions.reset.allowed_values = []
        expected = {sushy.ResetType.POWER_CYCLE,
                    sushy.ResetType.PUSH_POWER_BUTTON,
                    sushy.ResetType.FORCE_ON, sushy.ResetType.NMI,
                    sushy.ResetType.FORCE_RESTART,
                    sushy.ResetType.GRACEFUL_RESTART, sushy.ResetType.ON,
                    sushy.ResetType.FORCE_OFF,
                    sushy.ResetType.GRACEFUL_SHUTDOWN,
                    sushy.ResetType.SUSPEND,
                    sushy.ResetType.RESUME,
                    sushy.ResetType.PAUSE}
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
        self.chassis.reset_chassis(sushy.ResetType.GRACEFUL_RESTART)
        self.chassis._conn.post.assert_called_once_with(
            '/redfish/v1/Chassis/Blade1/Actions/Chassis.Reset',
            data={'ResetType': 'GracefulRestart'})

    def test_reset_chassis_with_invalid_value(self):
        self.assertRaises(exceptions.InvalidParameterValueError,
                          self.chassis.reset_chassis, 'invalid-value')

    def test_set_indicator_led(self):
        with mock.patch.object(
                self.chassis, 'invalidate', autospec=True) as invalidate_mock:
            self.chassis.set_indicator_led(sushy.IndicatorLED.BLINKING)
            self.chassis._conn.patch.assert_called_once_with(
                '/redfish/v1/Chassis/Blade1',
                data={'IndicatorLED': 'Blinking'},
                etag='d37f7bcd528e4d59')

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

    def test_network_adapters(self):
        self.conn.get.return_value.json.reset_mock()
        with open('sushy/tests/unit/'
                  'json_samples/network_adapter_collection.json') as f:
            self.conn.get.return_value.json.return_value = json.load(f)
        actual_adapters = self.chassis.network_adapters
        self.assertIsInstance(actual_adapters,
                              adapter.NetworkAdapterCollection)
        self.conn.get.return_value.json.assert_called_once_with()

    def test_network_adapters_cached(self):
        self.conn.get.return_value.json.reset_mock()
        with open('sushy/tests/unit/'
                  'json_samples/network_adapter_collection.json') as f:
            self.conn.get.return_value.json.return_value = json.load(f)
        actual_adapters = self.chassis.network_adapters
        self.conn.get.return_value.json.reset_mock()
        self.assertIs(actual_adapters,
                      self.chassis.network_adapters)
        self.conn.get.return_value.json.assert_not_called()

    def test_network_adapters_refresh(self):
        with open('sushy/tests/unit/'
                  'json_samples/network_adapter_collection.json') as f:
            self.conn.get.return_value.json.return_value = json.load(f)
        adapters = self.chassis.network_adapters
        self.assertIsInstance(adapters, adapter.NetworkAdapterCollection)

        with open('sushy/tests/unit/'
                  'json_samples/chassis.json') as f:
            self.conn.get.return_value.json.return_value = json.load(f)

        self.chassis.invalidate()
        self.chassis.refresh(force=False)

        self.assertTrue(adapters._is_stale)

        with open('sushy/tests/unit/'
                  'json_samples/network_adapter_collection.json') as f:
            self.conn.get.return_value.json.return_value = json.load(f)
        self.assertIsInstance(self.chassis.network_adapters,
                              adapter.NetworkAdapterCollection)


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
            redfish_version=self.chassis.redfish_version, registries=None,
            root=self.chassis.root)

    @mock.patch.object(chassis, 'Chassis', autospec=True)
    def test_get_members(self, chassis_mock):
        members = self.chassis.get_members()
        calls = [
            mock.call(self.chassis._conn, '/redfish/v1/Chassis/MultiBladeEncl',
                      redfish_version=self.chassis.redfish_version,
                      registries=None,
                      root=self.chassis.root),
            mock.call(self.chassis._conn, '/redfish/v1/Chassis/Blade1',
                      redfish_version=self.chassis.redfish_version,
                      registries=None,
                      root=self.chassis.root),
            mock.call(self.chassis._conn, '/redfish/v1/Chassis/Blade2',
                      redfish_version=self.chassis.redfish_version,
                      registries=None,
                      root=self.chassis.root),
            mock.call(self.chassis._conn, '/redfish/v1/Chassis/Blade3',
                      redfish_version=self.chassis.redfish_version,
                      registries=None,
                      root=self.chassis.root),
            mock.call(self.chassis._conn, '/redfish/v1/Chassis/Blade4',
                      redfish_version=self.chassis.redfish_version,
                      registries=None,
                      root=self.chassis.root)
        ]
        chassis_mock.assert_has_calls(calls)
        self.assertIsInstance(members, list)
        self.assertEqual(5, len(members))
