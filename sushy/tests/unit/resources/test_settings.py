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

from dateutil import parser

from sushy import exceptions
from sushy.resources import constants as res_cons
from sushy.resources import settings
from sushy.tests.unit import base


class SettingsFieldTestCase(base.TestCase):

    def setUp(self):
        super(SettingsFieldTestCase, self).setUp()
        with open('sushy/tests/unit/json_samples/settings.json') as f:
            self.json = json.load(f)

        self.settings = settings.SettingsField()

    def test__load(self):
        instance = self.settings._load(self.json, mock.Mock())

        self.assertEqual('9234ac83b9700123cc32',
                         instance._etag)
        self.assertEqual('2016-03-07T14:44:30-05:00',
                         instance.time)
        self.assertEqual('/redfish/v1/Systems/437XR1138R2/BIOS/Settings',
                         instance._settings_object_idref.resource_uri)
        self.assertEqual('Base.1.0.SettingsFailed',
                         instance.messages[0].message_id)
        self.assertEqual('Settings update failed due to invalid value',
                         instance.messages[0].message)
        self.assertEqual(res_cons.SEVERITY_CRITICAL,
                         instance.messages[0].severity)
        self.assertEqual('Fix the value and try again',
                         instance.messages[0].resolution)
        self.assertEqual('arg1',
                         instance.messages[0].message_args[0])
        self.assertEqual('#/Attributes/ProcTurboMode',
                         instance.messages[0]._related_properties[0])
        self.assertEqual('/redfish/v1/Systems/437XR1138R2/BIOS/Settings',
                         instance._settings_object_idref.resource_uri)
        self.assertEqual(
            1,
            instance.
            maintenance_window.maintenance_window_duration_in_seconds)
        self.assertEqual(
            parser.parse('2016-03-07T14:44:30-05:05'),
            instance.maintenance_window.maintenance_window_start_time)
        self.assertEqual(
            1,
            instance.operation_apply_time_support.
            maintenance_window_duration_in_seconds)
        self.assertEqual(
            parser.parse('2016-03-07T14:44:30-05:10'),
            instance.operation_apply_time_support.
            maintenance_window_start_time)
        self.assertIn(
            'Immediate',
            instance.operation_apply_time_support.supported_values)

    def test__load_failure(self):
        self.json[
            '@Redfish.Settings']['MaintenanceWindow'][
                'MaintenanceWindowStartTime'] = 'bad date'
        self.assertRaisesRegex(
            exceptions.MalformedAttributeError,
            '@Redfish.Settings/MaintenanceWindow/MaintenanceWindowStartTime',
            self.settings._load, self.json, mock.Mock())

    def test_commit(self):
        conn = mock.Mock()
        instance = self.settings._load(self.json, conn)
        instance.commit(conn, {'Attributes': {'key': 'value'}})
        conn.patch.assert_called_once_with(
            '/redfish/v1/Systems/437XR1138R2/BIOS/Settings',
            data={'Attributes': {'key': 'value'}})
