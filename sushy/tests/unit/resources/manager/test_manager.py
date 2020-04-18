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
from sushy.resources.manager import virtual_media
from sushy.resources.system import system
from sushy.tests.unit import base


class ManagerTestCase(base.TestCase):

    def setUp(self):
        super(ManagerTestCase, self).setUp()
        self.conn = mock.Mock()
        with open('sushy/tests/unit/json_samples/manager.json') as f:
            self.json_doc = json.load(f)

        self.conn.get.return_value.json.return_value = self.json_doc

        self.manager = manager.Manager(self.conn, '/redfish/v1/Managers/BMC',
                                       redfish_version='1.0.2')

    def test__parse_attributes(self):
        # | WHEN |
        self.manager._parse_attributes(self.json_doc)
        # | THEN |
        self.assertEqual('1.0.2', self.manager.redfish_version)
        self.assertEqual('1.00', self.manager.firmware_version)
        self.assertFalse(self.manager.auto_dst_enabled)
        self.assertEqual(True, self.manager.graphical_console.service_enabled)
        self.assertEqual(
            2, self.manager.graphical_console.max_concurrent_sessions)
        self.assertEqual(True, self.manager.serial_console.service_enabled)
        self.assertEqual(
            1, self.manager.serial_console.max_concurrent_sessions)
        self.assertEqual(True, self.manager.command_shell.service_enabled)
        self.assertEqual(
            4, self.manager.command_shell.max_concurrent_sessions)
        self.assertEqual('Contoso BMC', self.manager.description)
        self.assertEqual('BMC', self.manager.identity)
        self.assertEqual('Manager', self.manager.name)
        self.assertEqual('Joo Janta 200', self.manager.model)
        self.assertEqual(sushy.MANAGER_TYPE_BMC, self.manager.manager_type)
        self.assertEqual('58893887-8974-2487-2389-841168418919',
                         self.manager.uuid)

    def test_get_supported_graphical_console_types(self):
        # | GIVEN |
        expected = set([sushy.GRAPHICAL_CONSOLE_KVMIP])
        # | WHEN |
        values = self.manager.get_supported_graphical_console_types()
        # | THEN |
        self.assertEqual(expected, values)
        self.assertIsInstance(values, set)

    def test_get_supported_graphical_console_types_for_no_connect_types(self):
        # | GIVEN |
        graphical_console = self.manager.graphical_console
        expected = set([sushy.GRAPHICAL_CONSOLE_KVMIP,
                        sushy.GRAPHICAL_CONSOLE_OEM])

        for val in [None, []]:
            graphical_console.connect_types_supported = val
            # | WHEN |
            values = self.manager.get_supported_graphical_console_types()
            # | THEN |
            self.assertEqual(expected, values)
            self.assertIsInstance(values, set)

    def test_get_supported_graphical_console_types_missing_graphcon_attr(self):
        # | GIVEN |
        self.manager.graphical_console = None
        expected = set([sushy.GRAPHICAL_CONSOLE_KVMIP,
                        sushy.GRAPHICAL_CONSOLE_OEM])
        # | WHEN |
        values = self.manager.get_supported_graphical_console_types()
        # | THEN |
        self.assertEqual(expected, values)
        self.assertIsInstance(values, set)

    def test_get_supported_serial_console_types(self):
        # | GIVEN |
        expected = set([sushy.SERIAL_CONSOLE_SSH,
                        sushy.SERIAL_CONSOLE_TELNET,
                        sushy.SERIAL_CONSOLE_IPMI])
        # | WHEN |
        values = self.manager.get_supported_serial_console_types()
        # | THEN |
        self.assertEqual(expected, values)
        self.assertIsInstance(values, set)

    def test_get_supported_serial_console_types_for_no_connect_types(self):
        # | GIVEN |
        serial_console = self.manager.serial_console
        expected = set([sushy.SERIAL_CONSOLE_SSH,
                        sushy.SERIAL_CONSOLE_TELNET,
                        sushy.SERIAL_CONSOLE_IPMI,
                        sushy.SERIAL_CONSOLE_OEM])

        for val in [None, []]:
            serial_console.connect_types_supported = val
            # | WHEN |
            values = self.manager.get_supported_serial_console_types()
            # | THEN |
            self.assertEqual(expected, values)
            self.assertIsInstance(values, set)

    def test_get_supported_serial_console_types_missing_serialcon_attr(self):
        # | GIVEN |
        self.manager.serial_console = None
        expected = set([sushy.SERIAL_CONSOLE_SSH,
                        sushy.SERIAL_CONSOLE_TELNET,
                        sushy.SERIAL_CONSOLE_IPMI,
                        sushy.SERIAL_CONSOLE_OEM])
        # | WHEN |
        values = self.manager.get_supported_serial_console_types()
        # | THEN |
        self.assertEqual(expected, values)
        self.assertIsInstance(values, set)

    def test_get_supported_command_shell_types(self):
        # | GIVEN |
        expected = set([sushy.COMMAND_SHELL_SSH,
                        sushy.COMMAND_SHELL_TELNET])
        # | WHEN |
        values = self.manager.get_supported_command_shell_types()
        # | THEN |
        self.assertEqual(expected, values)
        self.assertIsInstance(values, set)

    def test_get_supported_command_shell_types_for_no_connect_types(self):
        # | GIVEN |
        command_shell = self.manager.command_shell
        expected = set([sushy.COMMAND_SHELL_SSH,
                        sushy.COMMAND_SHELL_TELNET,
                        sushy.COMMAND_SHELL_IPMI,
                        sushy.COMMAND_SHELL_OEM])

        for val in [None, []]:
            command_shell.connect_types_supported = val
            # | WHEN |
            values = self.manager.get_supported_command_shell_types()
            # | THEN |
            self.assertEqual(expected, values)
            self.assertIsInstance(values, set)

    def test_get_supported_command_shell_types_missing_cmdshell_attr(self):
        # | GIVEN |
        self.manager.command_shell = None
        expected = set([sushy.COMMAND_SHELL_SSH,
                        sushy.COMMAND_SHELL_TELNET,
                        sushy.COMMAND_SHELL_IPMI,
                        sushy.COMMAND_SHELL_OEM])
        # | WHEN |
        values = self.manager.get_supported_command_shell_types()
        # | THEN |
        self.assertEqual(expected, values)
        self.assertIsInstance(values, set)

    def test_get_allowed_reset_manager_values(self):
        # | GIVEN |
        expected = set([sushy.RESET_MANAGER_GRACEFUL_RESTART,
                        sushy.RESET_MANAGER_FORCE_RESTART])
        # | WHEN |
        values = self.manager.get_allowed_reset_manager_values()
        # | THEN |
        self.assertEqual(expected, values)
        self.assertIsInstance(values, set)

    def test_get_allowed_reset_manager_values_for_no_values_set(self):
        # | GIVEN |
        self.manager._actions.reset.allowed_values = []
        expected = set([sushy.RESET_MANAGER_GRACEFUL_RESTART,
                        sushy.RESET_MANAGER_FORCE_RESTART])
        # | WHEN |
        values = self.manager.get_allowed_reset_manager_values()
        # | THEN |
        self.assertEqual(expected, values)
        self.assertIsInstance(values, set)

    def test_get_allowed_reset_manager_values_missing_action_reset_attr(self):
        # | GIVEN |
        self.manager._actions.reset = None
        # | WHEN & THEN |
        self.assertRaisesRegex(
            exceptions.MissingActionError, 'action #Manager.Reset',
            self.manager.get_allowed_reset_manager_values)

    def test_reset_manager(self):
        self.manager.reset_manager(sushy.RESET_MANAGER_GRACEFUL_RESTART)
        self.manager._conn.post.assert_called_once_with(
            '/redfish/v1/Managers/BMC/Actions/Manager.Reset',
            data={'ResetType': 'GracefulRestart'})

    def test_reset_manager_with_invalid_value(self):
        self.assertRaises(exceptions.InvalidParameterValueError,
                          self.manager.reset_manager, 'invalid-value')

    def test_virtual_media(self):
        # | GIVEN |
        with open('sushy/tests/unit/json_samples/'
                  'virtual_media_collection.json') as f:
            virtual_media_collection_return_value = json.load(f)

        with open('sushy/tests/unit/json_samples/'
                  'virtual_media.json') as f:
            virtual_media_return_value = json.load(f)

        self.conn.get.return_value.json.side_effect = [
            virtual_media_collection_return_value, virtual_media_return_value]

        # | WHEN |
        actual_virtual_media = self.manager.virtual_media

        # | THEN |
        self.assertIsInstance(actual_virtual_media,
                              virtual_media.VirtualMediaCollection)
        self.assertEqual(actual_virtual_media.name, 'Virtual Media Services')

        member = actual_virtual_media.get_member(
            '/redfish/v1/Managers/BMC/VirtualMedia/Floppy1')

        self.assertEqual(member.image_name, "Sardine2.1.43.35.6a")
        self.assertTrue(member.inserted)
        self.assertFalse(member.write_protected)

    def test_virtual_media_on_refresh(self):
        # | GIVEN |
        with open('sushy/tests/unit/json_samples/'
                  'virtual_media_collection.json') as f:
            self.conn.get.return_value.json.return_value = json.load(f)

        # | WHEN & THEN |
        vrt_media = self.manager.virtual_media
        self.assertIsInstance(vrt_media, virtual_media.VirtualMediaCollection)

        # On refreshing the manager instance...
        with open('sushy/tests/unit/json_samples/manager.json', 'r') as f:
            self.conn.get.return_value.json.return_value = json.loads(f.read())

        self.manager.invalidate()
        self.manager.refresh(force=False)

        # | WHEN & THEN |
        self.assertTrue(vrt_media._is_stale)

        # | GIVEN |
        with open('sushy/tests/unit/json_samples/'
                  'virtual_media_collection.json') as f:
            self.conn.get.return_value.json.return_value = json.load(f)

        # | WHEN & THEN |
        self.assertIsInstance(self.manager.virtual_media,
                              virtual_media.VirtualMediaCollection)
        self.assertFalse(vrt_media._is_stale)

    def test_systems(self):
        # | GIVEN |
        with open('sushy/tests/unit/json_samples/'
                  'system.json') as f:
            self.conn.get.return_value.json.return_value = json.load(f)

        # | WHEN & THEN |
        actual_systems = self.manager.systems
        self.assertIsInstance(actual_systems[0], system.System)
        self.assertEqual(
            '/redfish/v1/Systems/437XR1138R2', actual_systems[0].path)

    def test_chassis(self):
        # | GIVEN |
        with open('sushy/tests/unit/json_samples/'
                  'chassis.json') as f:
            self.conn.get.return_value.json.return_value = json.load(f)

        # | WHEN & THEN |
        actual_chassis = self.manager.chassis
        self.assertIsInstance(actual_chassis[0], chassis.Chassis)
        self.assertEqual(
            '/redfish/v1/Chassis/1U', actual_chassis[0].path)


class ManagerCollectionTestCase(base.TestCase):

    def setUp(self):
        super(ManagerCollectionTestCase, self).setUp()
        self.conn = mock.Mock()
        with open('sushy/tests/unit/json_samples/'
                  'manager_collection.json') as f:
            self.conn.get.return_value.json.return_value = json.load(f)
        self.managers = manager.ManagerCollection(
            self.conn, '/redfish/v1/Managers', redfish_version='1.0.2')

    @mock.patch.object(manager, 'Manager', autospec=True)
    def test_get_member(self, Manager_mock):
        self.managers.get_member('/redfish/v1/Managers/BMC')
        Manager_mock.assert_called_once_with(
            self.managers._conn, '/redfish/v1/Managers/BMC',
            self.managers.redfish_version, None)

    @mock.patch.object(manager, 'Manager', autospec=True)
    def test_get_members(self, Manager_mock):
        members = self.managers.get_members()
        Manager_mock.assert_called_once_with(
            self.managers._conn, '/redfish/v1/Managers/BMC',
            self.managers.redfish_version, None)
        self.assertIsInstance(members, list)
        self.assertEqual(1, len(members))
