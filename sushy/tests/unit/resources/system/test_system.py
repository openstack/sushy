# Copyright 2017 Red Hat, Inc.
# All Rights Reserved.
#
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

import json

import mock

import sushy
from sushy import exceptions
from sushy.resources.system import system
from sushy.tests.unit import base


class SystemTestCase(base.TestCase):

    def setUp(self):
        super(SystemTestCase, self).setUp()
        self.conn = mock.Mock()
        with open('sushy/tests/unit/json_samples/system.json', 'r') as f:
            self.conn.get.return_value.json.return_value = json.loads(f.read())

        self.sys_inst = system.System(
            self.conn, '/redfish/v1/Systems/437XR1138R2',
            redfish_version='1.0.2')

    def test__parse_attributes(self):
        self.sys_inst._parse_attributes()
        self.assertEqual('1.0.2', self.sys_inst.redfish_version)
        self.assertEqual('Chicago-45Z-2381', self.sys_inst.asset_tag)
        self.assertEqual('P79 v1.33 (02/28/2015)', self.sys_inst.bios_version)
        self.assertEqual('Web Front End node', self.sys_inst.description)
        self.assertEqual('web483', self.sys_inst.hostname)
        self.assertEqual('437XR1138R2', self.sys_inst.identity)
        self.assertEqual('Off', self.sys_inst.indicator_led)
        self.assertEqual('Contoso', self.sys_inst.manufacturer)
        self.assertEqual('WebFrontEnd483', self.sys_inst.name)
        self.assertEqual('224071-J23', self.sys_inst.part_number)
        self.assertEqual('437XR1138R2', self.sys_inst.serial_number)
        self.assertEqual('8675309', self.sys_inst.sku)
        self.assertEqual('Physical', self.sys_inst.system_type)
        self.assertEqual('38947555-7742-3448-3784-823347823834',
                         self.sys_inst.uuid)
        self.assertEqual(sushy.SYSTEM_POWER_STATE_ON,
                         self.sys_inst.power_state)

    def test_get__reset_action_element(self):
        value = self.sys_inst._get_reset_action_element()
        expected = {
            "target": "/redfish/v1/Systems/437XR1138R2/Actions/"
                      "ComputerSystem.Reset",
            "ResetType@Redfish.AllowableValues": [
                "On",
                "ForceOff",
                "GracefulShutdown",
                "GracefulRestart",
                "ForceRestart",
                "Nmi",
                "ForceOn"
            ]}
        self.assertEqual(expected, value)

    def test_get__reset_action_element_missing_actions_attr(self):
        self.sys_inst._json.pop('Actions')
        self.assertRaisesRegex(
            exceptions.MissingAttributeError, 'attribute Actions',
            self.sys_inst._get_reset_action_element)

    def test_get__reset_action_element_missing_reset_action(self):
        action = '#ComputerSystem.Reset'
        self.sys_inst._json['Actions'].pop(action)
        self.assertRaisesRegex(
            exceptions.MissingActionError, 'action %s' % action,
            self.sys_inst._get_reset_action_element)

    def test_get_allowed_reset_system_values(self):
        values = self.sys_inst.get_allowed_reset_system_values()
        expected = set([sushy.RESET_GRACEFUL_SHUTDOWN,
                        sushy.RESET_GRACEFUL_RESTART,
                        sushy.RESET_FORCE_RESTART,
                        sushy.RESET_FORCE_OFF,
                        sushy.RESET_FORCE_ON,
                        sushy.RESET_ON,
                        sushy.RESET_NMI])
        self.assertEqual(expected, values)
        self.assertIsInstance(values, set)

    @mock.patch.object(system.LOG, 'warning', autospec=True)
    @mock.patch.object(system.System, '_get_reset_action_element',
                       autospec=True)
    def test_get_allowed_reset_system_values_no_values_specified(
            self, mock_get_reset_action, mock_log):
        mock_get_reset_action.return_value = {}
        values = self.sys_inst.get_allowed_reset_system_values()
        # Assert it returns all values if it can't get the specific ones
        expected = set([sushy.RESET_GRACEFUL_SHUTDOWN,
                        sushy.RESET_GRACEFUL_RESTART,
                        sushy.RESET_FORCE_RESTART,
                        sushy.RESET_FORCE_OFF,
                        sushy.RESET_FORCE_ON,
                        sushy.RESET_ON,
                        sushy.RESET_NMI,
                        sushy.RESET_PUSH_POWER_BUTTON])
        self.assertEqual(expected, values)
        self.assertIsInstance(values, set)
        self.assertEqual(1, mock_log.call_count)

    def test__get_reset_system_path(self):
        value = self.sys_inst._get_reset_system_path()
        expected = (
            '/redfish/v1/Systems/437XR1138R2/Actions/ComputerSystem.Reset')
        self.assertEqual(expected, value)

    @mock.patch.object(system.System, '_get_reset_action_element',
                       autospec=True)
    def test__get_reset_system_path_missing_target_attr(
            self, mock_get_reset_action):
        mock_get_reset_action.return_value = {}
        self.assertRaisesRegex(
            exceptions.MissingAttributeError,
            'attribute Actions/ComputerSystem.Reset/target',
            self.sys_inst._get_reset_system_path)

    def test_reset_system(self):
        self.sys_inst.reset_system(sushy.RESET_FORCE_OFF)
        self.sys_inst._conn.post.assert_called_once_with(
            '/redfish/v1/Systems/437XR1138R2/Actions/ComputerSystem.Reset',
            data={'ResetType': 'ForceOff'})

    def test_reset_system_invalid_value(self):
        self.assertRaises(exceptions.InvalidParameterValueError,
                          self.sys_inst.reset_system, 'invalid-value')

    def test_get_allowed_system_boot_source_values(self):
        values = self.sys_inst.get_allowed_system_boot_source_values()
        expected = set([sushy.BOOT_SOURCE_TARGET_NONE,
                        sushy.BOOT_SOURCE_TARGET_PXE,
                        sushy.BOOT_SOURCE_TARGET_CD,
                        sushy.BOOT_SOURCE_TARGET_USB,
                        sushy.BOOT_SOURCE_TARGET_HDD,
                        sushy.BOOT_SOURCE_TARGET_BIOS_SETUP,
                        sushy.BOOT_SOURCE_TARGET_UTILITIES,
                        sushy.BOOT_SOURCE_TARGET_DIAGS,
                        sushy.BOOT_SOURCE_TARGET_SD_CARD,
                        sushy.BOOT_SOURCE_TARGET_UEFI_TARGET])
        self.assertEqual(expected, values)
        self.assertIsInstance(values, set)

    def test_get_allowed_system_boot_source_values_missing_boot_attr(self):
        self.sys_inst._json.pop('Boot')
        self.assertRaisesRegex(
            exceptions.MissingAttributeError, 'attribute Boot',
            self.sys_inst.get_allowed_system_boot_source_values)

    @mock.patch.object(system.LOG, 'warning', autospec=True)
    def test_get_allowed_system_boot_source_values_no_values_specified(
            self, mock_log):
        self.sys_inst._json['Boot'].pop(
            'BootSourceOverrideTarget@Redfish.AllowableValues')
        values = self.sys_inst.get_allowed_system_boot_source_values()
        # Assert it returns all values if it can't get the specific ones
        expected = set([sushy.BOOT_SOURCE_TARGET_NONE,
                        sushy.BOOT_SOURCE_TARGET_PXE,
                        sushy.BOOT_SOURCE_TARGET_CD,
                        sushy.BOOT_SOURCE_TARGET_USB,
                        sushy.BOOT_SOURCE_TARGET_HDD,
                        sushy.BOOT_SOURCE_TARGET_BIOS_SETUP,
                        sushy.BOOT_SOURCE_TARGET_UTILITIES,
                        sushy.BOOT_SOURCE_TARGET_DIAGS,
                        sushy.BOOT_SOURCE_TARGET_SD_CARD,
                        sushy.BOOT_SOURCE_TARGET_FLOPPY,
                        sushy.BOOT_SOURCE_TARGET_UEFI_TARGET,
                        sushy.BOOT_SOURCE_TARGET_UEFI_SHELL,
                        sushy.BOOT_SOURCE_TARGET_UEFI_HTTP])
        self.assertEqual(expected, values)
        self.assertIsInstance(values, set)
        self.assertEqual(1, mock_log.call_count)

    def test_set_system_boot_source(self):
        self.sys_inst.set_system_boot_source(
            sushy.BOOT_SOURCE_TARGET_PXE,
            enabled=sushy.BOOT_SOURCE_ENABLED_CONTINUOUS,
            mode=sushy.BOOT_SOURCE_MODE_UEFI)
        self.sys_inst._conn.patch.assert_called_once_with(
            '/redfish/v1/Systems/437XR1138R2',
            data={'Boot': {'BootSourceOverrideEnabled': 'Continuous',
                           'BootSourceOverrideTarget': 'Pxe',
                           'BootSourceOverrideMode': 'UEFI'}})

    def test_set_system_boot_source_no_mode_specified(self):
        self.sys_inst.set_system_boot_source(
            sushy.BOOT_SOURCE_TARGET_HDD,
            enabled=sushy.BOOT_SOURCE_ENABLED_ONCE)
        self.sys_inst._conn.patch.assert_called_once_with(
            '/redfish/v1/Systems/437XR1138R2',
            data={'Boot': {'BootSourceOverrideEnabled': 'Once',
                           'BootSourceOverrideTarget': 'Hdd'}})

    def test_set_system_boot_source_invalid_target(self):
        self.assertRaises(exceptions.InvalidParameterValueError,
                          self.sys_inst.set_system_boot_source,
                          'invalid-target')

    def test_set_system_boot_source_invalid_enabled(self):
        self.assertRaises(exceptions.InvalidParameterValueError,
                          self.sys_inst.set_system_boot_source,
                          sushy.BOOT_SOURCE_TARGET_HDD,
                          enabled='invalid-enabled')


class SystemCollectionTestCase(base.TestCase):

    def setUp(self):
        super(SystemCollectionTestCase, self).setUp()
        self.conn = mock.Mock()
        with open('sushy/tests/unit/json_samples/'
                  'system_collection.json', 'r') as f:
            self.conn.get.return_value.json.return_value = json.loads(f.read())
        self.sys_col = system.SystemCollection(
            self.conn, '/redfish/v1/Systems', redfish_version='1.0.2')

    def test__parse_attributes(self):
        self.sys_col._parse_attributes()
        self.assertEqual('1.0.2', self.sys_col.redfish_version)
        self.assertEqual('Computer System Collection', self.sys_col.name)
        self.assertEqual(('/redfish/v1/Systems/437XR1138R2',),
                         self.sys_col.members_identities)

    @mock.patch.object(system, 'System', autospec=True)
    def test_get_member(self, mock_system):
        self.sys_col.get_member('/redfish/v1/Systems/437XR1138R2')
        mock_system.assert_called_once_with(
            self.sys_col._conn, '/redfish/v1/Systems/437XR1138R2',
            redfish_version=self.sys_col.redfish_version)

    @mock.patch.object(system, 'System', autospec=True)
    def test_get_members(self, mock_system):
        members = self.sys_col.get_members()
        mock_system.assert_called_once_with(
            self.sys_col._conn, '/redfish/v1/Systems/437XR1138R2',
            redfish_version=self.sys_col.redfish_version)
        self.assertIsInstance(members, list)
        self.assertEqual(1, len(members))
