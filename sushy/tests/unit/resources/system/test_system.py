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
from unittest import mock

from dateutil import parser

import sushy
from sushy import exceptions
from sushy.resources.chassis import chassis
from sushy.resources import constants as res_cons
from sushy.resources.manager import manager
from sushy.resources.oem import fake
from sushy.resources.system import bios
from sushy.resources.system import processor
from sushy.resources.system import secure_boot
from sushy.resources.system import simple_storage
from sushy.resources.system import system
from sushy.tests.unit import base


class SystemTestCase(base.TestCase):

    def setUp(self):
        super(SystemTestCase, self).setUp()
        self.conn = mock.Mock()
        self.conn.get.return_value.headers = {'Allow': 'GET,HEAD'}
        with open('sushy/tests/unit/json_samples/system.json') as f:
            self.json_doc = json.load(f)

        self.conn.get.return_value.json.return_value = self.json_doc

        self.sys_inst = system.System(
            self.conn, '/redfish/v1/Systems/437XR1138R2',
            redfish_version='1.0.2')
        self.sys_inst._get_etag = mock.Mock()
        self.sys_inst._get_etag.return_value = '81802dbf61beb0bd'

    def test__parse_attributes(self):
        self.sys_inst._parse_attributes(self.json_doc)
        self.assertEqual('1.0.2', self.sys_inst.redfish_version)
        self.assertEqual('Chicago-45Z-2381', self.sys_inst.asset_tag)
        self.assertEqual('P79 v1.45 (12/06/2017)', self.sys_inst.bios_version)
        self.assertEqual('Web Front End node', self.sys_inst.description)
        self.assertEqual('web483', self.sys_inst.hostname)
        self.assertEqual('437XR1138R2', self.sys_inst.identity)
        self.assertEqual(sushy.IndicatorLED.OFF,
                         self.sys_inst.indicator_led)
        self.assertEqual('Contoso', self.sys_inst.manufacturer)
        self.assertEqual('WebFrontEnd483', self.sys_inst.name)
        self.assertEqual('224071-J23', self.sys_inst.part_number)
        self.assertEqual('437XR1138R2', self.sys_inst.serial_number)
        self.assertEqual('8675309', self.sys_inst.sku)
        self.assertEqual(sushy.SystemType.PHYSICAL, self.sys_inst.system_type)
        self.assertEqual('38947555-7742-3448-3784-823347823834',
                         self.sys_inst.uuid)
        self.assertEqual(res_cons.State.ENABLED, self.sys_inst.status.state)
        self.assertEqual(res_cons.Health.OK, self.sys_inst.status.health)
        self.assertEqual(res_cons.Health.OK,
                         self.sys_inst.status.health_rollup)
        self.assertEqual(sushy.PowerState.ON, self.sys_inst.power_state)
        self.assertEqual(96, self.sys_inst.memory_summary.size_gib)
        self.assertEqual("OK", self.sys_inst.memory_summary.health)
        self.assertIsNotNone(self.sys_inst.maintenance_window)
        self.assertEqual(1, self.sys_inst.maintenance_window
                         .maintenance_window_duration_in_seconds)
        self.assertEqual(parser.parse('2016-03-07T14:44:30-05:05'),
                         self.sys_inst.maintenance_window
                         .maintenance_window_start_time)
        for oem_vendor in self.sys_inst.oem_vendors:
            self.assertIn(oem_vendor, ('Contoso', 'Chipwise'))

    def test__parse_attributes_return(self):
        attributes = self.sys_inst._parse_attributes(self.json_doc)

        # Test that various types are returned correctly
        self.assertEqual('Chicago-45Z-2381', attributes.get('asset_tag'))
        self.assertEqual(sushy.IndicatorLED.OFF,
                         attributes.get('indicator_led'))
        self.assertEqual({'health': res_cons.Health.OK,
                          'health_rollup': res_cons.Health.OK,
                          'state': res_cons.State.ENABLED},
                         attributes.get('status'))
        self.assertEqual({'maintenance_window_duration_in_seconds': 1,
                          'maintenance_window_start_time':
                          parser.parse('2016-03-07T14:44:30-05:05')},
                         attributes.get('maintenance_window'))
        self.assertEqual(
            {'reset': {'allowed_values':
                       ['On', 'ForceOff', 'GracefulShutdown',
                        'GracefulRestart', 'ForceRestart', 'Nmi',
                        'ForceOn', 'PushPowerButton'],
                       'operation_apply_time_support':
                       {'_maintenance_window_resource':
                        {'resource_uri':
                         '/redfish/v1/Systems/437XR1138R2'},
                        'maintenance_window_duration_in_seconds': 600,
                        'maintenance_window_start_time':
                        parser.parse('2017-05-03T23:12:37-05:00'),
                        'supported_values':
                        ['Immediate', 'AtMaintenanceWindowStart'],
                        'mapped_supported_values':
                        [res_cons.ApplyTime.IMMEDIATE,
                         res_cons.ApplyTime.AT_MAINTENANCE_WINDOW_START]},
                       'target_uri':
                       '/redfish/v1/Systems/437XR1138R2/Actions/'
                       'ComputerSystem.Reset'}},
            attributes.get('_actions'))

    def test__parse_attributes_missing_actions(self):
        self.sys_inst.json.pop('Actions')
        self.assertRaisesRegex(
            exceptions.MissingAttributeError, 'attribute Actions',
            self.sys_inst._parse_attributes, self.json_doc)

    def test__parse_attributes_missing_boot(self):
        self.sys_inst.json.pop('Boot')
        self.assertRaisesRegex(
            exceptions.MissingAttributeError, 'attribute Boot',
            self.sys_inst._parse_attributes, self.json_doc)

    def test__parse_attributes_missing_reset_target(self):
        self.sys_inst.json['Actions']['#ComputerSystem.Reset'].pop(
            'target')
        self.assertRaisesRegex(
            exceptions.MissingAttributeError,
            'attribute Actions/#ComputerSystem.Reset/target',
            self.sys_inst._parse_attributes, self.json_doc)

    def test__parse_attributes_null_memory_capacity(self):
        self.sys_inst.json['MemorySummary']['TotalSystemMemoryGiB'] = None
        self.sys_inst._parse_attributes(self.json_doc)
        self.assertIsNone(self.sys_inst.memory_summary.size_gib)

    def test__parse_attributes_bad_maintenance_window_time(self):
        self.sys_inst.json['@Redfish.MaintenanceWindow'][
            'MaintenanceWindowStartTime'] = 'bad date'
        self.assertRaisesRegex(
            exceptions.MalformedAttributeError,
            '@Redfish.MaintenanceWindow/MaintenanceWindowStartTime',
            self.sys_inst._parse_attributes, self.json_doc)

    def test_get__reset_action_element(self):
        value = self.sys_inst._get_reset_action_element()
        self.assertEqual("/redfish/v1/Systems/437XR1138R2/Actions/"
                         "ComputerSystem.Reset",
                         value.target_uri)
        self.assertEqual(["On",
                          "ForceOff",
                          "GracefulShutdown",
                          "GracefulRestart",
                          "ForceRestart",
                          "Nmi",
                          "ForceOn",
                          "PushPowerButton"
                          ],
                         value.allowed_values)

    def test_get__reset_action_element_missing_reset_action(self):
        self.sys_inst._actions.reset = None
        self.assertRaisesRegex(
            exceptions.MissingActionError, 'action #ComputerSystem.Reset',
            self.sys_inst._get_reset_action_element)

    def test_get_allowed_reset_system_values(self):
        values = self.sys_inst.get_allowed_reset_system_values()
        expected = set([sushy.ResetType.GRACEFUL_SHUTDOWN,
                        sushy.ResetType.GRACEFUL_RESTART,
                        sushy.ResetType.FORCE_RESTART,
                        sushy.ResetType.FORCE_OFF,
                        sushy.ResetType.FORCE_ON,
                        sushy.ResetType.ON,
                        sushy.ResetType.NMI,
                        sushy.ResetType.PUSH_POWER_BUTTON])
        self.assertEqual(expected, values)
        self.assertIsInstance(values, set)

    @mock.patch.object(system.LOG, 'warning', autospec=True)
    def test_get_allowed_reset_system_values_no_values_specified(
            self, mock_log):
        self.sys_inst._actions.reset.allowed_values = {}
        values = self.sys_inst.get_allowed_reset_system_values()
        # Assert it returns all values if it can't get the specific ones
        expected = set([sushy.ResetType.GRACEFUL_SHUTDOWN,
                        sushy.ResetType.GRACEFUL_RESTART,
                        sushy.ResetType.FORCE_RESTART,
                        sushy.ResetType.FORCE_OFF,
                        sushy.ResetType.FORCE_ON,
                        sushy.ResetType.ON,
                        sushy.ResetType.NMI,
                        sushy.ResetType.PUSH_POWER_BUTTON,
                        sushy.ResetType.POWER_CYCLE,
                        sushy.ResetType.SUSPEND,
                        sushy.ResetType.RESUME,
                        sushy.ResetType.PAUSE])
        self.assertEqual(expected, values)
        self.assertIsInstance(values, set)
        self.assertEqual(1, mock_log.call_count)

    def test_reset_action_operation_apply_time_support(self):
        support = self.sys_inst._actions.reset.operation_apply_time_support
        self.assertIsNotNone(support)
        self.assertEqual(['Immediate', 'AtMaintenanceWindowStart'],
                         support.supported_values)
        self.assertEqual([res_cons.ApplyTime.IMMEDIATE,
                          res_cons.ApplyTime.AT_MAINTENANCE_WINDOW_START],
                         support.mapped_supported_values)
        self.assertEqual(parser.parse('2017-05-03T23:12:37-05:00'),
                         support.maintenance_window_start_time)
        self.assertEqual(600, support.maintenance_window_duration_in_seconds)
        self.assertEqual('/redfish/v1/Systems/437XR1138R2',
                         support._maintenance_window_resource.resource_uri)

    def test_reset_system(self):
        self.sys_inst.reset_system(sushy.ResetType.FORCE_OFF)
        self.sys_inst._conn.post.assert_called_once_with(
            '/redfish/v1/Systems/437XR1138R2/Actions/ComputerSystem.Reset',
            data={'ResetType': 'ForceOff'})

    def test_reset_system_invalid_value(self):
        self.assertRaises(exceptions.InvalidParameterValueError,
                          self.sys_inst.reset_system, 'invalid-value')

    def test_get_allowed_system_boot_source_values(self):
        values = self.sys_inst.get_allowed_system_boot_source_values()
        expected = set([sushy.BootSource.NONE,
                        sushy.BootSource.PXE,
                        sushy.BootSource.CD,
                        sushy.BootSource.USB,
                        sushy.BootSource.HDD,
                        sushy.BootSource.BIOS_SETUP,
                        sushy.BootSource.UTILITIES,
                        sushy.BootSource.DIAGS,
                        sushy.BootSource.SD_CARD,
                        sushy.BootSource.UEFI_TARGET,
                        sushy.BootSource.UEFI_HTTP])
        self.assertEqual(expected, values)
        self.assertIsInstance(values, set)

    @mock.patch.object(system.LOG, 'warning', autospec=True)
    def test_get_allowed_system_boot_source_values_no_values_specified(
            self, mock_log):
        self.sys_inst.boot.allowed_values = None
        values = self.sys_inst.get_allowed_system_boot_source_values()
        # Assert it returns all values if it can't get the specific ones
        expected = set([sushy.BootSource.NONE,
                        sushy.BootSource.PXE,
                        sushy.BootSource.CD,
                        sushy.BootSource.USB,
                        sushy.BootSource.HDD,
                        sushy.BootSource.BIOS_SETUP,
                        sushy.BootSource.UTILITIES,
                        sushy.BootSource.DIAGS,
                        sushy.BootSource.SD_CARD,
                        sushy.BootSource.FLOPPY,
                        sushy.BootSource.UEFI_TARGET,
                        sushy.BootSource.UEFI_SHELL,
                        sushy.BootSource.UEFI_HTTP,
                        sushy.BootSource.REMOTE_DRIVE,
                        sushy.BootSource.UEFI_BOOT_NEXT,
                        sushy.BootSource.USB_CD])
        self.assertEqual(expected, values)
        self.assertIsInstance(values, set)
        self.assertEqual(1, mock_log.call_count)

    def test_set_system_boot_options(self):
        self.sys_inst.set_system_boot_options(
            sushy.BootSource.PXE,
            enabled=sushy.BootSourceOverrideEnabled.CONTINUOUS,
            mode=sushy.BootSourceOverrideMode.UEFI)
        self.sys_inst._conn.patch.assert_called_once_with(
            '/redfish/v1/Systems/437XR1138R2',
            data={'Boot': {'BootSourceOverrideEnabled': 'Continuous',
                           'BootSourceOverrideTarget': 'Pxe',
                           'BootSourceOverrideMode': 'UEFI'}},
            etag='81802dbf61beb0bd')

    def test_set_system_boot_options_no_mode_specified(self):
        self.sys_inst.set_system_boot_options(
            sushy.BootSource.HDD,
            enabled=sushy.BootSourceOverrideEnabled.ONCE)
        self.sys_inst._conn.patch.assert_called_once_with(
            '/redfish/v1/Systems/437XR1138R2',
            data={'Boot': {'BootSourceOverrideEnabled': 'Once',
                           'BootSourceOverrideTarget': 'Hdd'}},
            etag='81802dbf61beb0bd')

    def test_set_system_boot_options_no_target_specified(self):
        self.sys_inst.set_system_boot_options(
            enabled=sushy.BootSourceOverrideEnabled.CONTINUOUS,
            mode=sushy.BootSourceOverrideMode.UEFI)
        self.sys_inst._conn.patch.assert_called_once_with(
            '/redfish/v1/Systems/437XR1138R2',
            data={'Boot': {'BootSourceOverrideEnabled': 'Continuous',
                           'BootSourceOverrideMode': 'UEFI'}},
            etag='81802dbf61beb0bd')

    def test_set_system_boot_options_no_freq_specified(self):
        self.sys_inst.set_system_boot_options(
            target=sushy.BootSource.PXE,
            mode=sushy.BootSourceOverrideMode.UEFI)
        self.sys_inst._conn.patch.assert_called_once_with(
            '/redfish/v1/Systems/437XR1138R2',
            data={'Boot': {'BootSourceOverrideTarget': 'Pxe',
                           'BootSourceOverrideMode': 'UEFI'}},
            etag='81802dbf61beb0bd')

    def test_set_system_boot_options_nothing_specified(self):
        self.sys_inst.set_system_boot_options()
        self.sys_inst._conn.patch.assert_not_called()

    def test_set_system_boot_options_invalid_target(self):
        self.assertRaises(exceptions.InvalidParameterValueError,
                          self.sys_inst.set_system_boot_source,
                          'invalid-target')

    def test_set_system_boot_options_invalid_enabled(self):
        with self.assertRaisesRegex(
            exceptions.InvalidParameterValueError,
            '"enabled" value.*{0}'.format(
                list(sushy.BootSourceOverrideEnabled))):

            self.sys_inst.set_system_boot_options(
                sushy.BootSource.HDD,
                enabled='invalid-enabled')

    def test_set_system_boot_options_supermicro_usb_cd_boot(self):
        (self.json_doc["Boot"]
         ["BootSourceOverrideTarget@Redfish.AllowableValues"]).append("UsbCd")
        self.sys_inst._parse_attributes(self.json_doc)

        self.sys_inst.manufacturer = "supermicro"
        self.sys_inst.set_system_boot_options(
            target=sushy.BootSource.CD,
            enabled=sushy.BootSourceOverrideEnabled.ONCE)

        self.sys_inst._conn.patch.assert_called_once_with(
            '/redfish/v1/Systems/437XR1138R2',
            data={'Boot': {'BootSourceOverrideEnabled': 'Once',
                           'BootSourceOverrideTarget': 'UsbCd'}},
            etag='81802dbf61beb0bd')

    def test_set_system_boot_options_supermicro_no_usb_cd_boot(self):

        self.sys_inst.manufacturer = "supermicro"
        self.sys_inst.set_system_boot_options(
            target=sushy.BootSource.CD,
            enabled=sushy.BootSourceOverrideEnabled.ONCE)

        self.sys_inst._conn.patch.assert_called_once_with(
            '/redfish/v1/Systems/437XR1138R2',
            data={'Boot': {'BootSourceOverrideEnabled': 'Once',
                           'BootSourceOverrideTarget': 'Cd'}},
            etag='81802dbf61beb0bd')

    def test_set_system_boot_options_settings_resource_nokia(self):
        with open('sushy/tests/unit/json_samples/settings-nokia.json') as f:
            settings_obj = json.load(f)

        self.json_doc.update(settings_obj)
        self.sys_inst._parse_attributes(self.json_doc)

        with open('sushy/tests/unit/json_samples/'
                  'settings-body-nokia.json') as f:
            settings_body = json.load(f)

        get_settings = mock.MagicMock(headers={'ETag': '"3d7b838291941d"'})
        get_settings.json.return_value = settings_body
        get_system = mock.MagicMock(headers={'ETag': '"222"'})
        self.conn.get.side_effect = [get_settings, get_system]

        self.sys_inst.set_system_boot_options(
            target=sushy.BootSource.CD,
            enabled=sushy.BootSourceOverrideEnabled.ONCE)

        self.sys_inst._conn.patch.assert_called_once_with(
            '/redfish/v1/Systems/Self/SD',
            data={'Boot': {'BootSourceOverrideEnabled': 'Once',
                           'BootSourceOverrideTarget': 'Cd'}},
            etag='"3d7b838291941d"')

    def test_set_system_boot_options_settings_resource(self):
        with open('sushy/tests/unit/json_samples/settings.json') as f:
            settings_obj = json.load(f)

        self.json_doc.update(settings_obj)
        self.sys_inst._parse_attributes(self.json_doc)

        with open('sushy/tests/unit/json_samples/'
                  'settings-body-nokia.json') as f:
            settings_body = json.load(f)

        get_settings = mock.MagicMock(headers={'ETag': '"3d7b838291941d"'})
        get_settings.json.return_value = settings_body
        get_system = mock.MagicMock(headers={'ETag': '"222"'})
        self.conn.get.side_effect = [get_settings, get_system]

        self.conn.get.return_value.json.return_value = settings_body

        self.sys_inst.set_system_boot_options(
            target=sushy.BootSource.CD,
            enabled=sushy.BootSourceOverrideEnabled.ONCE)

        self.sys_inst._conn.patch.assert_called_once_with(
            '/redfish/v1/Systems/437XR1138R2/BIOS/Settings',
            data={'Boot': {'BootSourceOverrideEnabled': 'Once',
                           'BootSourceOverrideTarget': 'Cd'}},
            etag='"3d7b838291941d"')

    def test_set_system_boot_options_settings_resource_lenovo(self):
        self.sys_inst = system.System(
            self.conn, '/redfish/v1/Systems/1',
            redfish_version='1.0.2')

        with open('sushy/tests/unit/json_samples/'
                  'settings-lenovo-se450.json') as f:
            settings_obj = json.load(f)

        self.json_doc.update(settings_obj)
        self.sys_inst._parse_attributes(self.json_doc)

        with open('sushy/tests/unit/json_samples/'
                  'settings-body-lenovo-se450.json') as f:
            settings_body = json.load(f)

        get_settings = mock.MagicMock(headers={'ETag': '"3d7b838291941d"'})
        get_settings.json.return_value = settings_body
        get_system = mock.MagicMock(headers={'ETag': '"222"'})
        self.conn.get.side_effect = [get_settings, get_system]

        self.sys_inst.set_system_boot_options(
            target=sushy.BootSource.CD,
            enabled=sushy.BootSourceOverrideEnabled.ONCE)

        self.sys_inst._conn.patch.assert_called_once_with(
            '/redfish/v1/Systems/1',
            data={'Boot': {'BootSourceOverrideEnabled': 'Once',
                           'BootSourceOverrideTarget': 'Cd'}},
            etag='"222"')

    def test_set_system_boot_options_settings_resource_bootmode_only(self):
        self.sys_inst = system.System(
            self.conn, '/redfish/v1/Systems/1',
            redfish_version='1.0.2')

        with open('sushy/tests/unit/json_samples/'
                  'settings-nokia.json') as f:
            settings_obj = json.load(f)

        self.json_doc.update(settings_obj)
        self.sys_inst._parse_attributes(self.json_doc)

        with open('sushy/tests/unit/json_samples/'
                  'settings-body-bootsourceoverridemode-only.json') as f:
            settings_body = json.load(f)

        get_settings = mock.MagicMock(headers={'ETag': '"3d7b838291941d"'})
        get_settings.json.return_value = settings_body
        get_system = mock.MagicMock(headers={'ETag': '"222"'})
        self.conn.get.side_effect = [get_settings, get_system]

        self.sys_inst.set_system_boot_options(
            mode=sushy.BootSourceOverrideMode.UEFI)

        self.sys_inst._conn.patch.assert_called_with(
            '/redfish/v1/Systems/Self/SD',
            data={'Boot': {'BootSourceOverrideMode': 'UEFI'}},
            etag='"3d7b838291941d"')

    def test_set_system_boot_options_httpbooturi(self):
        self.sys_inst.set_system_boot_options(
            sushy.BootSource.UEFI_HTTP,
            enabled=sushy.BootSourceOverrideEnabled.ONCE,
            mode=sushy.BootSourceOverrideMode.UEFI,
            http_boot_uri='http://test.lan/test_image.iso'
            )
        self.sys_inst._conn.patch.assert_called_once_with(
            '/redfish/v1/Systems/437XR1138R2',
            data={'Boot': {'BootSourceOverrideTarget': 'UefiHttp',
                           'BootSourceOverrideEnabled': 'Once',
                           'BootSourceOverrideMode': 'UEFI',
                           'HttpBootUri': 'http://test.lan/test_image.iso'}},
            etag=mock.ANY)

    def test_set_system_boot_options_httpboot(self):
        self.sys_inst.set_system_boot_options(
            sushy.BootSource.UEFI_HTTP,
            enabled=sushy.BootSourceOverrideEnabled.ONCE,
            mode=sushy.BootSourceOverrideMode.UEFI
            )
        self.sys_inst._conn.patch.assert_called_once_with(
            '/redfish/v1/Systems/437XR1138R2',
            data={'Boot': {'BootSourceOverrideTarget': 'UefiHttp',
                           'BootSourceOverrideEnabled': 'Once',
                           'BootSourceOverrideMode': 'UEFI',
                           'HttpBootUri': None}},
            etag=mock.ANY)

    def test_set_system_boot_options_httpboot_unset(self):
        self.sys_inst._settings = mock.Mock()
        self.sys_inst._settings.resource_uri = 'meow'
        settings_body = json.dumps(
            {'Boot': {'HttpBootUri': 'http://foo.bar'}}
        )

        get_settings = mock.MagicMock()
        get_settings.json.return_value = settings_body
        self.conn.get.side_effect = get_settings

        self.sys_inst.set_system_boot_options(
            sushy.BootSource.HDD,
            mode=sushy.BootSourceOverrideMode.UEFI
            )
        self.sys_inst._conn.patch.assert_called_once_with(
            '/redfish/v1/Systems/437XR1138R2',
            data={'Boot': {'BootSourceOverrideTarget': 'Hdd',
                           'BootSourceOverrideMode': 'UEFI',
                           'HttpBootUri': None}},
            etag=mock.ANY)

    def test_set_system_boot_source(self):
        self.sys_inst.set_system_boot_source(
            sushy.BootSource.PXE,
            enabled=sushy.BootSourceOverrideEnabled.CONTINUOUS,
            mode=sushy.BootSourceOverrideMode.UEFI)
        self.sys_inst._conn.patch.assert_called_once_with(
            '/redfish/v1/Systems/437XR1138R2',
            data={'Boot': {'BootSourceOverrideEnabled': 'Continuous',
                           'BootSourceOverrideTarget': 'Pxe',
                           'BootSourceOverrideMode': 'UEFI'}},
            etag='81802dbf61beb0bd')

    def test_set_system_boot_source_with_etag(self):
        self.conn.get.return_value.headers = {'ETag': '"81802dbf61beb0bd"'}
        self.sys_inst.set_system_boot_source(
            sushy.BOOT_SOURCE_TARGET_PXE,
            enabled=sushy.BOOT_SOURCE_ENABLED_CONTINUOUS,
            mode=sushy.BOOT_SOURCE_MODE_UEFI)
        self.sys_inst._conn.patch.assert_called_once_with(
            '/redfish/v1/Systems/437XR1138R2',
            data={'Boot': {'BootSourceOverrideEnabled': 'Continuous',
                           'BootSourceOverrideTarget': 'Pxe',
                           'BootSourceOverrideMode': 'UEFI'}},
            etag="81802dbf61beb0bd")

    def test_set_system_boot_source_no_mode_specified(self):
        self.sys_inst.set_system_boot_source(
            sushy.BootSource.HDD,
            enabled=sushy.BootSourceOverrideEnabled.ONCE)
        self.sys_inst._conn.patch.assert_called_once_with(
            '/redfish/v1/Systems/437XR1138R2',
            data={'Boot': {'BootSourceOverrideEnabled': 'Once',
                           'BootSourceOverrideTarget': 'Hdd'}},
            etag='81802dbf61beb0bd')

    def test_set_system_boot_unsets_http_boot_uri(self):
        self.sys_inst.set_system_boot_source(
            sushy.BootSource.HDD,
            enabled=sushy.BootSourceOverrideEnabled.ONCE)
        self.sys_inst._conn.patch.assert_called_once_with(
            '/redfish/v1/Systems/437XR1138R2',
            data={'Boot': {'BootSourceOverrideEnabled': 'Once',
                           'BootSourceOverrideTarget': 'Hdd'}},
            etag=mock.ANY)

    def test_set_system_boot_source_invalid_target(self):
        self.assertRaises(exceptions.InvalidParameterValueError,
                          self.sys_inst.set_system_boot_source,
                          'invalid-target')

    def test_set_system_boot_source_invalid_enabled(self):
        with self.assertRaisesRegex(
            exceptions.InvalidParameterValueError,
            '"enabled" value.*{0}'.format(
                list(sushy.BootSourceOverrideEnabled))):

            self.sys_inst.set_system_boot_source(
                sushy.BootSource.HDD,
                enabled='invalid-enabled')

    def test_set_indicator_led(self):
        with mock.patch.object(
                self.sys_inst, 'invalidate', autospec=True) as invalidate_mock:
            self.sys_inst.set_indicator_led(sushy.IndicatorLED.BLINKING)
            self.sys_inst._conn.patch.assert_called_once_with(
                '/redfish/v1/Systems/437XR1138R2',
                data={'IndicatorLED': 'Blinking'},
                etag='81802dbf61beb0bd')

            invalidate_mock.assert_called_once_with()

    def test_set_indicator_led_invalid_state(self):
        self.assertRaises(exceptions.InvalidParameterValueError,
                          self.sys_inst.set_indicator_led,
                          'spooky-glowing')

    def test__get_processor_collection_path_missing_processors_attr(self):
        self.sys_inst._json.pop('Processors')
        self.assertRaisesRegex(
            exceptions.MissingAttributeError, 'attribute Processors',
            self.sys_inst._get_processor_collection_path)

    def test_memory_summary_missing_attr(self):
        # | GIVEN |
        self.sys_inst._json['MemorySummary']['Status'].pop('HealthRollup')
        # | WHEN |
        self.sys_inst._parse_attributes(self.json_doc)
        # | THEN |
        self.assertEqual(96, self.sys_inst.memory_summary.size_gib)
        self.assertIsNone(self.sys_inst.memory_summary.health)

        # | GIVEN |
        self.sys_inst._json['MemorySummary'].pop('Status')
        # | WHEN |
        self.sys_inst._parse_attributes(self.json_doc)
        # | THEN |
        self.assertEqual(96, self.sys_inst.memory_summary.size_gib)
        self.assertIsNone(self.sys_inst.memory_summary.health)

        # | GIVEN |
        self.sys_inst._json['MemorySummary'].pop('TotalSystemMemoryGiB')
        # | WHEN |
        self.sys_inst._parse_attributes(self.json_doc)
        # | THEN |
        self.assertIsNone(self.sys_inst.memory_summary.size_gib)
        self.assertIsNone(self.sys_inst.memory_summary.health)

        # | GIVEN |
        self.sys_inst._json.pop('MemorySummary')
        # | WHEN |
        self.sys_inst._parse_attributes(self.json_doc)
        # | THEN |
        self.assertIsNone(self.sys_inst.memory_summary)

    def test_processors(self):
        # | GIVEN |
        self.conn.get.return_value.json.reset_mock()
        with open('sushy/tests/unit/json_samples/'
                  'processor_collection.json') as f:
            self.conn.get.return_value.json.return_value = json.load(f)
        # | WHEN |
        actual_processors = self.sys_inst.processors
        # | THEN |
        self.assertIsInstance(actual_processors,
                              processor.ProcessorCollection)
        self.conn.get.return_value.json.assert_called_once_with()

        # reset mock
        self.conn.get.return_value.json.reset_mock()
        # | WHEN & THEN |
        # tests for same object on invoking subsequently
        self.assertIs(actual_processors,
                      self.sys_inst.processors)
        self.conn.get.return_value.json.assert_not_called()

    def test_processors_on_refresh(self):
        # | GIVEN |
        with open('sushy/tests/unit/json_samples/'
                  'processor_collection.json') as f:
            self.conn.get.return_value.json.return_value = json.load(f)
        # | WHEN & THEN |
        self.assertIsInstance(self.sys_inst.processors,
                              processor.ProcessorCollection)

        # On refreshing the system instance...
        with open('sushy/tests/unit/json_samples/system.json') as f:
            self.conn.get.return_value.json.return_value = json.load(f)

        self.sys_inst.invalidate()
        self.sys_inst.refresh(force=False)

        # | GIVEN |
        with open('sushy/tests/unit/json_samples/'
                  'processor_collection.json') as f:
            self.conn.get.return_value.json.return_value = json.load(f)
        # | WHEN & THEN |
        self.assertIsInstance(self.sys_inst.processors,
                              processor.ProcessorCollection)

    def _setUp_processor_summary(self):
        self.conn.get.return_value.json.reset_mock()
        with open('sushy/tests/unit/json_samples/'
                  'processor_collection.json') as f:
            self.conn.get.return_value.json.return_value = json.load(f)

        # fetch processors for the first time
        self.sys_inst.processors

        successive_return_values = []
        file_names = ['sushy/tests/unit/json_samples/processor.json',
                      'sushy/tests/unit/json_samples/processor2.json']
        for file_name in file_names:
            with open(file_name) as f:
                successive_return_values.append(json.load(f))

        self.conn.get.return_value.json.side_effect = successive_return_values

    def test_processor_summary(self):
        # | GIVEN |
        self._setUp_processor_summary()
        # | WHEN |
        actual_processor_summary = self.sys_inst.processors.summary
        # | THEN |
        self.assertEqual((16, sushy.ProcessorArchitecture.X86),
                         actual_processor_summary)
        self.assertEqual(16, actual_processor_summary.count)
        self.assertEqual(sushy.ProcessorArchitecture.X86,
                         actual_processor_summary.architecture)

        # reset mock
        self.conn.get.return_value.json.reset_mock()

        # | WHEN & THEN |
        # tests for same object on invoking subsequently
        self.assertIs(actual_processor_summary,
                      self.sys_inst.processors.summary)
        self.conn.get.return_value.json.assert_not_called()

    def test_ethernet_interfaces(self):
        self.conn.get.return_value.json.reset_mock()
        eth_coll_return_value = None
        eth_return_value = None
        with open('sushy/tests/unit/json_samples/'
                  'ethernet_interfaces_collection.json') as f:
            eth_coll_return_value = json.load(f)
        with open('sushy/tests/unit/json_samples/'
                  'ethernet_interfaces.json') as f:
            eth_return_value = json.load(f)

        self.conn.get.return_value.json.side_effect = [eth_coll_return_value,
                                                       eth_return_value]

        actual_macs = self.sys_inst.ethernet_interfaces.summary
        expected_macs = (
            {'12:44:6A:3B:04:11': res_cons.State.ENABLED})
        self.assertEqual(expected_macs, actual_macs)

    def test_bios(self):
        self.conn.get.return_value.json.reset_mock()
        bios_return_value = None
        with open('sushy/tests/unit/json_samples/bios.json') as f:
            bios_return_value = json.load(f)
        self.conn.get.return_value.json.side_effect = [bios_return_value]

        self.assertIsInstance(self.sys_inst.bios, bios.Bios)
        self.assertEqual('BIOS Configuration Current Settings',
                         self.sys_inst.bios.name)

    def test_secure_boot(self):
        self.conn.get.return_value.json.reset_mock()
        with open('sushy/tests/unit/json_samples/secure_boot.json') as f:
            self.conn.get.return_value.json.side_effect = [json.load(f)]

        self.assertIsInstance(self.sys_inst.secure_boot,
                              secure_boot.SecureBoot)
        self.assertEqual('UEFI Secure Boot', self.sys_inst.secure_boot.name)

    def test_simple_storage_for_missing_attr(self):
        self.sys_inst.json.pop('SimpleStorage')
        with self.assertRaisesRegex(
                exceptions.MissingAttributeError, 'attribute SimpleStorage'):
            self.sys_inst.simple_storage

    def test_simple_storage(self):
        # | GIVEN |
        self.conn.get.return_value.json.reset_mock()
        with open('sushy/tests/unit/json_samples/'
                  'simple_storage_collection.json') as f:
            self.conn.get.return_value.json.return_value = json.load(f)
        # | WHEN |
        actual_simple_storage = self.sys_inst.simple_storage
        # | THEN |
        self.assertIsInstance(actual_simple_storage,
                              simple_storage.SimpleStorageCollection)
        self.conn.get.return_value.json.assert_called_once_with()

        # reset mock
        self.conn.get.return_value.json.reset_mock()
        # | WHEN & THEN |
        # tests for same object on invoking subsequently
        self.assertIs(actual_simple_storage,
                      self.sys_inst.simple_storage)
        self.conn.get.return_value.json.assert_not_called()

    def test_simple_storage_on_refresh(self):
        # | GIVEN |
        with open('sushy/tests/unit/json_samples/'
                  'simple_storage_collection.json') as f:
            self.conn.get.return_value.json.return_value = json.load(f)
        # | WHEN & THEN |
        self.assertIsInstance(self.sys_inst.simple_storage,
                              simple_storage.SimpleStorageCollection)

        # On refreshing the system instance...
        with open('sushy/tests/unit/json_samples/system.json') as f:
            self.conn.get.return_value.json.return_value = json.load(f)

        self.sys_inst.invalidate()
        self.sys_inst.refresh(force=False)

        # | GIVEN |
        with open('sushy/tests/unit/json_samples/'
                  'simple_storage_collection.json') as f:
            self.conn.get.return_value.json.return_value = json.load(f)
        # | WHEN & THEN |
        self.assertIsInstance(self.sys_inst.simple_storage,
                              simple_storage.SimpleStorageCollection)

    def test_storage_for_missing_attr(self):
        self.sys_inst.json.pop('SimpleStorage')
        with self.assertRaisesRegex(
                exceptions.MissingAttributeError, 'attribute Storage'):
            self.sys_inst.storage

    def test_storage(self):
        # | GIVEN |
        self.conn.get.return_value.json.reset_mock()
        with open('sushy/tests/unit/json_samples/'
                  'storage_collection.json') as f:
            self.conn.get.return_value.json.return_value = json.load(f)
        # | WHEN |
        actual_storage = self.sys_inst.simple_storage
        # | THEN |
        self.assertIsInstance(actual_storage,
                              simple_storage.SimpleStorageCollection)
        self.conn.get.return_value.json.assert_called_once_with()

        # reset mock
        self.conn.get.return_value.json.reset_mock()
        # | WHEN & THEN |
        # tests for same object on invoking subsequently
        self.assertIs(actual_storage, self.sys_inst.simple_storage)
        self.conn.get.return_value.json.assert_not_called()

    def test_storage_on_refresh(self):
        # | GIVEN |
        with open('sushy/tests/unit/json_samples/'
                  'storage_collection.json') as f:
            self.conn.get.return_value.json.return_value = json.load(f)
        # | WHEN & THEN |
        self.assertIsInstance(self.sys_inst.simple_storage,
                              simple_storage.SimpleStorageCollection)

        # On refreshing the system instance...
        with open('sushy/tests/unit/json_samples/system.json') as f:
            self.conn.get.return_value.json.return_value = json.load(f)

        self.sys_inst.invalidate()
        self.sys_inst.refresh(force=False)

        # | GIVEN |
        with open('sushy/tests/unit/json_samples/'
                  'storage_collection.json') as f:
            self.conn.get.return_value.json.return_value = json.load(f)
        # | WHEN & THEN |
        self.assertIsInstance(self.sys_inst.simple_storage,
                              simple_storage.SimpleStorageCollection)

    def test_managers(self):
        # | GIVEN |
        with open('sushy/tests/unit/json_samples/'
                  'manager.json') as f:
            self.conn.get.return_value.json.return_value = json.load(f)

        # | WHEN & THEN |
        actual_managers = self.sys_inst.managers
        self.assertIsInstance(actual_managers[0], manager.Manager)
        self.assertEqual(
            '/redfish/v1/Managers/BMC', actual_managers[0].path)

    def test_chassis(self):
        # | GIVEN |
        with open('sushy/tests/unit/json_samples/'
                  'chassis.json') as f:
            self.conn.get.return_value.json.return_value = json.load(f)

        # | WHEN & THEN |
        actual_chassis = self.sys_inst.chassis
        self.assertIsInstance(actual_chassis[0], chassis.Chassis)
        self.assertEqual(
            '/redfish/v1/Chassis/1U', actual_chassis[0].path)

    def test_get_oem_extension(self):
        # | WHEN |
        contoso_system_extn_inst = self.sys_inst.get_oem_extension('Contoso')
        # | THEN |
        self.assertIsInstance(contoso_system_extn_inst,
                              fake.FakeOEMSystemExtension)
        self.assertIs(self.sys_inst, contoso_system_extn_inst._parent_resource)
        self.assertEqual('Contoso', contoso_system_extn_inst._vendor_id)


class SystemCollectionTestCase(base.TestCase):

    def setUp(self):
        super(SystemCollectionTestCase, self).setUp()
        self.conn = mock.Mock()
        with open('sushy/tests/unit/json_samples/'
                  'system_collection.json') as f:
            self.json_doc = json.load(f)

        self.conn.get.return_value.json.return_value = self.json_doc

        self.sys_col = system.SystemCollection(
            self.conn, '/redfish/v1/Systems', redfish_version='1.0.2')

    def test__parse_attributes(self):
        self.sys_col._parse_attributes(self.json_doc)
        self.assertEqual('1.0.2', self.sys_col.redfish_version)
        self.assertEqual('Computer System Collection', self.sys_col.name)
        self.assertEqual(('/redfish/v1/Systems/437XR1138R2',),
                         self.sys_col.members_identities)

    @mock.patch.object(system, 'System', autospec=True)
    def test_get_member(self, mock_system):
        self.sys_col.get_member('/redfish/v1/Systems/437XR1138R2')
        mock_system.assert_called_once_with(
            self.sys_col._conn, '/redfish/v1/Systems/437XR1138R2',
            redfish_version=self.sys_col.redfish_version, registries=None,
            root=self.sys_col.root)

    @mock.patch.object(system, 'System', autospec=True)
    def test_get_members(self, mock_system):
        members = self.sys_col.get_members()
        mock_system.assert_called_once_with(
            self.sys_col._conn, '/redfish/v1/Systems/437XR1138R2',
            redfish_version=self.sys_col.redfish_version, registries=None,
            root=self.sys_col.root)
        self.assertIsInstance(members, list)
        self.assertEqual(1, len(members))
