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

from sushy.resources import constants as res_cons
from sushy.resources.registry import message_registry
from sushy.resources import settings
from sushy.tests.unit import base


class SettingsFieldTestCase(base.TestCase):

    def setUp(self):
        super(SettingsFieldTestCase, self).setUp()
        with open('sushy/tests/unit/json_samples/settings.json') as f:
            self.json = json.load(f)

        self.settings = settings.SettingsField()

        conn = mock.Mock()
        with open('sushy/tests/unit/json_samples/message_registry.json') as f:
            conn.get.return_value.json.return_value = json.load(f)
        registry = message_registry.MessageRegistry(
            conn, '/redfish/v1/Registries/Test',
            redfish_version='1.0.2')
        self.registries = {'Test.1.0': registry}

    @mock.patch.object(settings, 'LOG', autospec=True)
    def test__load(self, mock_LOG):
        instance = self.settings._load(self.json, mock.Mock())

        self.assertEqual('9234ac83b9700123cc32',
                         instance._etag)
        self.assertEqual('2016-03-07T14:44:30-05:00',
                         instance.time)
        self.assertEqual('/redfish/v1/Systems/437XR1138R2/BIOS/Settings',
                         instance._settings_object_idref.resource_uri)
        self.assertEqual('Test.1.0.Failed',
                         instance.messages[0].message_id)
        self.assertEqual('Settings %1 update failed due to invalid value',
                         instance.messages[0].message)
        self.assertEqual(res_cons.Severity.CRITICAL,
                         instance.messages[0].severity)
        self.assertEqual('Fix the value and try again',
                         instance.messages[0].resolution)
        self.assertEqual('arg1',
                         instance.messages[0].message_args[0])
        self.assertEqual('#/Attributes/ProcTurboMode',
                         instance.messages[0]._related_properties[0])
        self.assertEqual('/redfish/v1/Systems/437XR1138R2/BIOS/Settings',
                         instance._settings_object_idref.resource_uri)
        self.assertEqual([res_cons.ApplyTime.ON_RESET,
                          res_cons.ApplyTime.IN_MAINTENANCE_WINDOW_ON_RESET],
                         instance._supported_apply_times)
        self.assertIsNone(instance.maintenance_window)
        mock_LOG.warning.assert_called_once()
        mock_LOG.reset_mock()
        self.assertIsNone(instance.operation_apply_time_support)
        mock_LOG.warning.assert_called_once()

    def test_commit(self):
        conn = mock.Mock()
        instance = self.settings._load(self.json, conn)
        instance.commit(conn, {'Attributes': {'key': 'value'}})
        conn.patch.assert_called_once_with(
            '/redfish/v1/Systems/437XR1138R2/BIOS/Settings',
            data={'Attributes': {'key': 'value'}},
            etag='9234ac83b9700123cc32')

    def test_get_status_failure(self):
        instance = self.settings._load(self.json, mock.Mock())

        status = instance.get_status(self.registries)
        self.assertEqual(status.status,
                         settings.UPDATE_FAILURE)
        self.assertEqual(status.messages[0].severity,
                         res_cons.Severity.CRITICAL)
        self.assertEqual(status.messages[0].message,
                         'The property arg1 broke everything.')

    def test_get_status_success(self):
        instance = self.settings._load(self.json, mock.Mock())
        instance.messages[0].message_id = 'Test.1.0.Success'
        instance.messages[0].severity = res_cons.Severity.OK
        status = instance.get_status(self.registries)
        self.assertEqual(status.status,
                         settings.UPDATE_SUCCESS)
        self.assertEqual(status.messages[0].severity, res_cons.Severity.OK)
        self.assertEqual(status.messages[0].message,
                         'Everything done successfully.')

    def test_get_status_noupdates(self):
        instance = self.settings._load(self.json, mock.Mock())
        instance.time = None
        status = instance.get_status(self.registries)
        self.assertEqual(status.status,
                         settings.NO_UPDATES)
        self.assertIsNone(status.messages)
