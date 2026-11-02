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

from sushy.resources import constants as res_cons
from sushy.resources.manager import constants as mgr_cons
from sushy.resources.manager import host_interface
from sushy.resources.manager import network_protocol
from sushy.tests.unit import base


class HostInterfaceTestCase(base.TestCase):

    def setUp(self):
        super().setUp()
        self.conn = mock.Mock()
        with open('sushy/tests/unit/json_samples/'
                  'host_interface.json') as f:
            self.json_doc = json.load(f)

        self.conn.get.return_value.json.return_value = self.json_doc

        self.host_iface = host_interface.HostInterface(
            self.conn,
            '/redfish/v1/Managers/BMC/HostInterfaces/Host.1',
            redfish_version='1.0.2')

    def test__parse_attributes(self):
        self.host_iface._parse_attributes(self.json_doc)
        self.assertEqual('Host.1', self.host_iface.identity)
        self.assertEqual('Managed Host Interface 1', self.host_iface.name)
        self.assertEqual('Management for Host Interface',
                         self.host_iface.description)
        self.assertEqual(mgr_cons.HostInterfaceType.NETWORK_HOST_INTERFACE,
                         self.host_iface.host_interface_type)
        self.assertTrue(self.host_iface.interface_enabled)
        self.assertFalse(self.host_iface.externally_accessible)
        self.assertEqual(
            [mgr_cons.AuthenticationMode.BASIC_AUTH,
             mgr_cons.AuthenticationMode.REDFISH_SESSION_AUTH],
            self.host_iface.authentication_modes)
        self.assertEqual('ReadOnly', self.host_iface.auth_none_role_id)

    def test_status(self):
        self.assertEqual(res_cons.State.ENABLED,
                         self.host_iface.status.state)
        self.assertEqual(res_cons.Health.OK,
                         self.host_iface.status.health)

    def test_credential_bootstrapping(self):
        cred = self.host_iface.credential_bootstrapping
        self.assertFalse(cred.enabled)
        self.assertTrue(cred.enable_after_reset)
        self.assertEqual('Administrator', cred.role_id)
        self.assertTrue(cred.expiration_window_enabled)
        self.assertEqual(30, cred.expiration_window_minutes)

    def test_network_protocol(self):
        with open('sushy/tests/unit/json_samples/'
                  'manager_network_protocol.json') as f:
            self.conn.get.return_value.json.return_value = json.load(f)

        net_proto = self.host_iface.network_protocol
        self.assertIsInstance(
            net_proto, network_protocol.ManagerNetworkProtocol)
        self.assertEqual('NetworkProtocol', net_proto.identity)

    def test_systems(self):
        with open('sushy/tests/unit/json_samples/system.json') as f:
            self.conn.get.return_value.json.return_value = json.load(f)

        systems = self.host_iface.systems
        self.assertEqual(1, len(systems))
        self.assertEqual(
            '/redfish/v1/Systems/System.Embedded.1', systems[0].path)

    def test_set_interface_enabled(self):
        self.host_iface.set_interface_enabled(False)
        self.conn.patch.assert_called_once_with(
            '/redfish/v1/Managers/BMC/HostInterfaces/Host.1',
            data={'InterfaceEnabled': False})


class HostInterfaceCollectionTestCase(base.TestCase):

    def setUp(self):
        super().setUp()
        self.conn = mock.Mock()
        with open('sushy/tests/unit/json_samples/'
                  'host_interface_collection.json') as f:
            self.conn.get.return_value.json.return_value = json.load(f)
        self.host_iface_col = host_interface.HostInterfaceCollection(
            self.conn, '/redfish/v1/Managers/BMC/HostInterfaces',
            redfish_version='1.0.2')

    def test__parse_attributes(self):
        self.assertEqual('Host Interface Collection',
                         self.host_iface_col.name)

    @mock.patch.object(host_interface, 'HostInterface', autospec=True)
    def test_get_member(self, mock_host_iface):
        self.host_iface_col.get_member(
            '/redfish/v1/Managers/BMC/HostInterfaces/Host.1')
        mock_host_iface.assert_called_once_with(
            self.host_iface_col._conn,
            '/redfish/v1/Managers/BMC/HostInterfaces/Host.1',
            redfish_version=self.host_iface_col.redfish_version,
            registries=None, root=self.host_iface_col.root)

    @mock.patch.object(host_interface, 'HostInterface', autospec=True)
    def test_get_members(self, mock_host_iface):
        members = self.host_iface_col.get_members()
        mock_host_iface.assert_called_once_with(
            self.host_iface_col._conn,
            '/redfish/v1/Managers/BMC/HostInterfaces/Host.1',
            redfish_version=self.host_iface_col.redfish_version,
            registries=None, root=self.host_iface_col.root)
        self.assertIsInstance(members, list)
        self.assertEqual(1, len(members))

    def test_disable_all(self):
        mock_member = mock.Mock(spec=host_interface.HostInterface)
        mock_member2 = mock.Mock(spec=host_interface.HostInterface)
        with mock.patch.object(
                self.host_iface_col, 'get_members', autospec=True,
                return_value=[mock_member, mock_member2]) as mock_get:
            self.host_iface_col.disable_all()
            mock_get.assert_called_once()
            mock_member.set_interface_enabled.assert_called_once_with(False)
            mock_member2.set_interface_enabled.assert_called_once_with(False)
