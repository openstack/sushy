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

import datetime
from http import client as http_client
import json
from unittest import mock

from dateutil import parser

from sushy import exceptions
from sushy.resources import constants as res_cons
from sushy.resources.registry import message_registry
from sushy.resources import settings
from sushy.resources.system import bios
from sushy.tests.unit import base


class BiosTestCase(base.TestCase):

    def setUp(self):
        super(BiosTestCase, self).setUp()
        self.conn = mock.Mock()
        with open('sushy/tests/unit/json_samples/bios.json') as f:
            self.bios_json = json.load(f)
        with open('sushy/tests/unit/json_samples/bios_settings.json') as f:
            self.bios_settings_json = json.load(f)

        self.conn.get.return_value.json.side_effect = [
            self.bios_json,
            self.bios_settings_json,
            self.bios_settings_json]

        conn = mock.Mock()
        with open('sushy/tests/unit/json_samples/message_registry.json') as f:
            conn.get.return_value.json.return_value = json.load(f)
            registry = message_registry.MessageRegistry(
                conn, '/redfish/v1/Registries/Test',
                redfish_version='1.0.2')

        self.sys_bios = bios.Bios(
            self.conn, '/redfish/v1/Systems/437XR1138R2/BIOS',
            registries={'Test.1.0': registry},
            redfish_version='1.0.2')

    def test__parse_attributes(self):
        self.sys_bios._parse_attributes(self.bios_json)
        self.assertEqual('1.0.2', self.sys_bios.redfish_version)
        self.assertEqual('BIOS', self.sys_bios.identity)
        self.assertEqual('BIOS Configuration Current Settings',
                         self.sys_bios.name)
        self.assertIsNone(self.sys_bios.description)
        self.assertEqual('BiosAttributeRegistryP89.v1_0_0',
                         self.sys_bios._attribute_registry)
        self.assertEqual('', self.sys_bios.attributes['AdminPhone'])
        self.assertEqual('Uefi', self.sys_bios.attributes['BootMode'])
        self.assertEqual(0, self.sys_bios.attributes['ProcCoreDisable'])
        self.assertEqual([res_cons.APPLY_TIME_ON_RESET,
                          res_cons.APPLY_TIME_MAINT_RESET],
                         self.sys_bios.supported_apply_times)
        self.assertEqual(600, self.sys_bios.maintenance_window
                         .maintenance_window_duration_in_seconds)
        self.assertEqual(parser.parse('2020-09-01T04:30:00-06:00'),
                         self.sys_bios.maintenance_window
                         .maintenance_window_start_time)
        # testing here if settings subfield parsed by checking ETag,
        # other settings fields tested in specific settings test
        self.assertEqual('9234ac83b9700123cc32',
                         self.sys_bios._settings._etag)
        self.assertEqual('(404) 555-1212',
                         self.sys_bios.pending_attributes['AdminPhone'])
        self.assertEqual(settings.UPDATE_FAILURE,
                         self.sys_bios.update_status.status)

    def test__parse_attributes_return(self):
        attributes = self.sys_bios._parse_attributes(self.bios_json)

        # Test that various types are returned correctly
        self.assertEqual('BIOS Configuration Current Settings',
                         attributes.get('name'))
        self.assertEqual({'AdminPhone': '',
                          'BootMode': 'Uefi',
                          'EmbeddedSata': 'Raid',
                          'NicBoot1': 'NetworkBoot',
                          'NicBoot2': 'Disabled',
                          'PowerProfile': 'MaxPerf',
                          'ProcCoreDisable': 0,
                          'ProcHyperthreading': 'Enabled',
                          'ProcTurboMode': 'Enabled',
                          'UsbControl': 'UsbEnabled'},
                         attributes.get('attributes'))
        self.assertEqual({'maintenance_window_duration_in_seconds': 600,
                         'maintenance_window_start_time':
                          parser.parse('2020-09-01T04:30:00-06:00')},
                         attributes.get('maintenance_window'))

    def test_set_attribute(self):
        self.sys_bios.set_attribute('ProcTurboMode', 'Disabled')
        self.sys_bios._conn.patch.assert_called_once_with(
            '/redfish/v1/Systems/437XR1138R2/BIOS/Settings',
            data={'Attributes': {'ProcTurboMode': 'Disabled'}})

    def test_set_attribute_apply_time(self):
        self.sys_bios.set_attribute('ProcTurboMode', 'Disabled',
                                    res_cons.APPLY_TIME_ON_RESET)
        self.sys_bios._conn.patch.assert_called_once_with(
            '/redfish/v1/Systems/437XR1138R2/BIOS/Settings',
            data={'Attributes': {'ProcTurboMode': 'Disabled'},
                  '@Redfish.SettingsApplyTime': {
                      '@odata.type': '#Settings.v1_0_0.PreferredApplyTime',
                      'ApplyTime': 'OnReset'}})

    def test_set_attribute_apply_time_with_maintenance_window(self):
        self.sys_bios.set_attribute('ProcTurboMode', 'Disabled',
                                    res_cons.APPLY_TIME_MAINT_RESET,
                                    datetime.datetime(2020, 9, 1, 4, 30, 0),
                                    600)
        self.sys_bios._conn.patch.assert_called_once_with(
            '/redfish/v1/Systems/437XR1138R2/BIOS/Settings',
            data={'Attributes': {'ProcTurboMode': 'Disabled'},
                  '@Redfish.SettingsApplyTime': {
                      '@odata.type': '#Settings.v1_0_0.PreferredApplyTime',
                      'ApplyTime': 'InMaintenanceWindowOnReset',
                      'MaintenanceWindowStartTime': '2020-09-01T04:30:00',
                      'MaintenanceWindowDurationInSeconds': 600}})

    def test_set_attribute_on_refresh(self):
        self.conn.get.reset_mock()
        # make it to instantiate pending attributes
        self.sys_bios.pending_attributes
        self.assertTrue(self.conn.get.called)

        self.conn.get.reset_mock()

        self.sys_bios.pending_attributes
        self.assertFalse(self.conn.get.called)

        self.sys_bios.set_attribute('ProcTurboMode', 'Disabled')
        # make it to refresh pending attributes on next retrieval
        self.sys_bios.pending_attributes
        self.assertTrue(self.conn.get.called)

    def test_set_attributes(self):
        self.sys_bios.set_attributes({'ProcTurboMode': 'Disabled',
                                      'UsbControl': 'UsbDisabled'})
        self.sys_bios._conn.patch.assert_called_once_with(
            '/redfish/v1/Systems/437XR1138R2/BIOS/Settings',
            data={'Attributes': {'ProcTurboMode': 'Disabled',
                                 'UsbControl': 'UsbDisabled'}})

    def test_set_attributes_apply_time(self):
        self.sys_bios.set_attributes({'ProcTurboMode': 'Disabled',
                                      'UsbControl': 'UsbDisabled'},
                                     res_cons.APPLY_TIME_IMMEDIATE)
        self.sys_bios._conn.patch.assert_called_once_with(
            '/redfish/v1/Systems/437XR1138R2/BIOS/Settings',
            data={'Attributes': {'ProcTurboMode': 'Disabled',
                                 'UsbControl': 'UsbDisabled'},
                  '@Redfish.SettingsApplyTime': {
                      '@odata.type': '#Settings.v1_0_0.PreferredApplyTime',
                      'ApplyTime': 'Immediate'}})

    def test_set_attributes_apply_time_with_maintenance_window(self):
        self.sys_bios.set_attributes({'ProcTurboMode': 'Disabled',
                                      'UsbControl': 'UsbDisabled'},
                                     res_cons.APPLY_TIME_MAINT_START,
                                     datetime.datetime(2020, 9, 1, 4, 30, 0),
                                     600)
        self.sys_bios._conn.patch.assert_called_once_with(
            '/redfish/v1/Systems/437XR1138R2/BIOS/Settings',
            data={'Attributes': {'ProcTurboMode': 'Disabled',
                                 'UsbControl': 'UsbDisabled'},
                  '@Redfish.SettingsApplyTime': {
                      '@odata.type': '#Settings.v1_0_0.PreferredApplyTime',
                      'ApplyTime': 'AtMaintenanceWindowStart',
                      'MaintenanceWindowStartTime': '2020-09-01T04:30:00',
                      'MaintenanceWindowDurationInSeconds': 600}})

    def test_set_attributes_apply_time_missing(self):
        self.assertRaises(ValueError,
                          self.sys_bios.set_attributes,
                          {'ProcTurboMode': 'Disabled',
                           'UsbControl': 'UsbDisabled'},
                          maint_window_start_time=datetime.datetime.now(),
                          maint_window_duration=600)

    def test_set_attributes_maint_window_start_time_missing(self):
        self.assertRaises(ValueError,
                          self.sys_bios.set_attributes,
                          {'ProcTurboMode': 'Disabled',
                           'UsbControl': 'UsbDisabled'},
                          res_cons.APPLY_TIME_MAINT_START,
                          maint_window_duration=600)

    def test_set_attributes_maint_window_duration_missing(self):
        self.assertRaises(ValueError,
                          self.sys_bios.set_attributes,
                          {'ProcTurboMode': 'Disabled',
                           'UsbControl': 'UsbDisabled'},
                          res_cons.APPLY_TIME_MAINT_START,
                          datetime.datetime.now())

    def test_set_attributes_on_refresh(self):
        self.conn.get.reset_mock()
        # make it to instantiate pending attributes
        self.sys_bios.pending_attributes
        self.assertTrue(self.conn.get.called)

        self.conn.get.reset_mock()

        self.sys_bios.pending_attributes
        self.assertFalse(self.conn.get.called)

        self.sys_bios.set_attributes({'ProcTurboMode': 'Disabled',
                                      'UsbControl': 'UsbDisabled'})
        # make it to refresh pending attributes on next retrieval
        self.sys_bios.pending_attributes
        self.assertTrue(self.conn.get.called)

    def test_apply_time_settings(self):
        self.conn.get.reset_mock()
        apply_time_settings = self.sys_bios.apply_time_settings
        self.assertIsNotNone(apply_time_settings)
        self.assertEqual('OnReset', apply_time_settings.apply_time)
        self.assertEqual(['OnReset', 'Immediate', 'AtMaintenanceWindowStart',
                         'InMaintenanceWindowOnReset'],
                         apply_time_settings.apply_time_allowable_values)
        self.assertEqual(parser.parse('2017-05-03T23:12:37-05:00'),
                         apply_time_settings.maintenance_window_start_time)
        self.assertEqual(600, apply_time_settings.
                         maintenance_window_duration_in_seconds)

    def test__get_reset_bios_action_element(self):
        value = self.sys_bios._get_reset_bios_action_element()
        self.assertEqual('/redfish/v1/Systems/437XR1138R2/BIOS/Actions/'
                         'Bios.ResetBios',
                         value.target_uri)

    def test_reset_bios_missing_action(self):
        self.sys_bios._actions.reset_bios = None
        self.assertRaisesRegex(
            exceptions.MissingActionError, '#Bios.ResetBios',
            self.sys_bios.reset_bios)

    def test__parse_attributes_missing_reset_bios_target(self):
        self.sys_bios.json['Actions']['#Bios.ResetBios'].pop(
            'target')
        self.assertRaisesRegex(
            exceptions.MissingAttributeError,
            'attribute Actions/#Bios.ResetBios/target',
            self.sys_bios._parse_attributes, self.bios_json)

    def test_reset_bios(self):
        self.sys_bios.reset_bios()
        self.sys_bios._conn.post.assert_called_once_with(
            '/redfish/v1/Systems/437XR1138R2/BIOS/Actions/Bios.ResetBios')

    def test_reset_bios_handle_http_error_415(self):

        target_uri = (
            '/redfish/v1/Systems/437XR1138R2/BIOS/Actions/Bios.ResetBios')
        self.conn.post.side_effect = [exceptions.HTTPError(
            method='POST', url=target_uri, response=mock.MagicMock(
                status_code=http_client.UNSUPPORTED_MEDIA_TYPE)), '200']
        post_calls = [
            mock.call(target_uri), mock.call(target_uri, data={})]
        self.sys_bios.reset_bios()
        self.sys_bios._conn.post.assert_has_calls(post_calls)

    def test_reset_bios_handle_http_error_400(self):

        target_uri = (
            '/redfish/v1/Systems/437XR1138R2/BIOS/Actions/Bios.ResetBios')
        self.conn.post.side_effect = [exceptions.HTTPError(
            method='POST', url=target_uri, response=mock.MagicMock(
                status_code=http_client.BAD_REQUEST)), '200']
        post_calls = [
            mock.call(target_uri), mock.call(target_uri, data={})]
        self.sys_bios.reset_bios()
        self.sys_bios._conn.post.assert_has_calls(post_calls)

    def test_reset_bios_handle_http_error_405(self):

        target_uri = (
            '/redfish/v1/Systems/437XR1138R2/BIOS/Actions/Bios.ResetBios')
        self.conn.post.side_effect = exceptions.HTTPError(
            method='POST', url=target_uri, response=mock.MagicMock(
                status_code=http_client.METHOD_NOT_ALLOWED))
        self.assertRaises(
            exceptions.HTTPError,
            self.sys_bios.reset_bios)
        self.sys_bios._conn.post.assert_called_once_with(target_uri)

    def test__get_change_password_element(self):
        value = self.sys_bios._get_change_password_element()
        self.assertEqual("/redfish/v1/Systems/437XR1138R2/BIOS/Actions/"
                         "Bios.ChangePassword",
                         value.target_uri)

    def test_change_password_missing_action(self):
        self.sys_bios._actions.change_password = None
        self.assertRaisesRegex(
            exceptions.MissingActionError, '#Bios.ChangePassword',
            self.sys_bios.change_password, 'newpassword',
                                           'oldpassword',
                                           'adminpassword')

    def test__parse_attributes_missing_change_password_target(self):
        self.sys_bios.json['Actions']['#Bios.ChangePassword'].pop(
            'target')
        self.assertRaisesRegex(
            exceptions.MissingAttributeError,
            'attribute Actions/#Bios.ChangePassword/target',
            self.sys_bios._parse_attributes, self.bios_json)

    def test_change_password(self):
        self.sys_bios.change_password('newpassword',
                                      'oldpassword',
                                      'adminpassword')
        self.sys_bios._conn.post.assert_called_once_with(
            '/redfish/v1/Systems/437XR1138R2/BIOS/Actions/Bios.ChangePassword',
            data={'OldPassword': 'oldpassword',
                  'NewPassword': 'newpassword',
                  'PasswordName': 'adminpassword'})
