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
from sushy.resources.system.network import constants as net_cons
from sushy.resources.system.network import device_function
from sushy.tests.unit import base


class NetworkDeviceFunctionTestCase(base.TestCase):

    def setUp(self):
        super(NetworkDeviceFunctionTestCase, self).setUp()
        self.conn = mock.Mock()
        with open('sushy/tests/unit/json_samples/'
                  'network_device_function.json') as f:
            self.json_doc = json.load(f)

        self.conn.get.return_value.json.return_value = self.json_doc

        self.function = device_function.NetworkDeviceFunction(
            self.conn,
            '/redfish/v1/Chassis/Blade1/NetworkAdapters/'
            'NIC.Integrated.1/NetworkDeviceFunctions/NIC.Integrated.1-2-1',
            redfish_version='1.0.2')

    def test__parse_attributes(self):
        self.function._parse_attributes(self.json_doc)
        self.assertEqual('1.0.2', self.function.redfish_version)
        self.assertEqual('NIC.Integrated.1-2-1', self.function.identity)
        self.assertEqual('NetworkDeviceFunction', self.function.name)
        self.assertEqual('NetworkDeviceFunction', self.function.description)
        self.assertEqual(res_cons.State.ENABLED, self.function.status.state)
        self.assertEqual(res_cons.Health.OK, self.function.status.health)
        self.assertEqual(res_cons.Health.OK,
                         self.function.status.health_rollup)
        self.assertEqual(self.function.type,
                         net_cons.NetworkDeviceTechnology.ETHERNET)
        self.assertEqual([
            net_cons.NetworkDeviceTechnology.DISABLED,
            net_cons.NetworkDeviceTechnology.ETHERNET,
            net_cons.NetworkDeviceTechnology.iSCSI,
        ], self.function.capabilities)
        self.assertEqual(1,
                         len(self.function.fibre_channel.boot_targets))
        self.assertEqual('ABCEDFG',
                         self.function.fibre_channel.boot_targets[0].wwpn)
        self.assertEqual('1234',
                         self.function.fibre_channel.boot_targets[0].lun_id)
        self.assertIsNone(
            self.function.fibre_channel.boot_targets[0].priority
        )
        self.assertEqual(127, self.function.max_virtual_functions)
        self.assertEqual('01:01:01:01:01:D1',
                         self.function.ethernet.mac_address)
        self.assertEqual('01:01:01:01:01:D1',
                         self.function.ethernet.permanent_mac_address)
        self.assertEqual(1234,
                         self.function.ethernet.mtu_size)
        self.assertEqual(1,
                         self.function.ethernet.vlan.vlan_id)
        self.assertTrue(self.function.ethernet.vlan.vlan_enabled)
        self.assertEqual(net_cons.NetworkAuthenticationMethod.NONE,
                         self.function.iscsi_boot.authentication_method)
        self.assertEqual(net_cons.IPAddressType.IPV4,
                         self.function.iscsi_boot.ip_address_type)
        self.assertEqual('0.0.0.0',
                         self.function.iscsi_boot.initiator_ip_address)
        self.assertEqual('0.0.0.0',
                         self.function.iscsi_boot.initiator_default_gateway)
        self.assertEqual('0.0.0.0',
                         self.function.iscsi_boot.initiator_netmask)
        self.assertEqual('0.0.0.0',
                         self.function.iscsi_boot.primary_dns)
        self.assertEqual('0.0.0.0',
                         self.function.iscsi_boot.primary_dns)
        self.assertEqual(0, self.function.iscsi_boot.primary_lun)
        self.assertEqual('0.0.0.0',
                         self.function.iscsi_boot.primary_target_ip_address)
        self.assertEqual(3260,
                         self.function.iscsi_boot.primary_target_tcp_port)
        self.assertFalse(self.function.iscsi_boot.secondary_vlan_enabled)
        self.assertEqual(1,
                         self.function.iscsi_boot.secondary_vlan_id)
        self.assertEqual(123,
                         self.function.iscsi_boot.secondary_target_tcp_port)


class NetworkDeviceFunctionCollectionTestCase(base.TestCase):

    def setUp(self):
        super(NetworkDeviceFunctionCollectionTestCase, self).setUp()
        self.conn = mock.Mock()
        with open('sushy/tests/unit/json_samples/'
                  'network_device_function_collection.json') as f:
            self.json_doc = json.load(f)

        self.conn.get.return_value.json.return_value = self.json_doc

        self.function_col = device_function.NetworkDeviceFunctionCollection(
            self.conn, '/redfish/v1/Chassis/System.Embedded.1/NetworkAdapters/'
                       'NIC.Integrated.1/NetworkDeviceFunctions',
            redfish_version='1.0.2')

    def test__parse_attributes(self):
        self.function_col._parse_attributes(self.json_doc)
        self.assertEqual((
            '/redfish/v1/Chassis/System.Embedded.1/NetworkAdapters/'
            'NIC.Integrated.1/NetworkDeviceFunctions/NIC.Integrated.1-1-1',
            '/redfish/v1/Chassis/System.Embedded.1/NetworkAdapters/'
            'NIC.Integrated.1/NetworkDeviceFunctions/NIC.Integrated.1-2-1'
        ),
            self.function_col.members_identities)

    @mock.patch.object(device_function, 'NetworkDeviceFunction', autospec=True)
    def test_get_member(self, device_function_mock):
        self.function_col.get_member(
            '/redfish/v1/Chassis/System.Embedded.1/NetworkAdapters/'
            'NIC.Integrated.1/NetworkDeviceFunctions/NIC.Integrated.1-1-1',
        )
        device_function_mock.assert_called_once_with(
            self.function_col._conn,
            '/redfish/v1/Chassis/System.Embedded.1/NetworkAdapters/'
            'NIC.Integrated.1/NetworkDeviceFunctions/NIC.Integrated.1-1-1',
            redfish_version=self.function_col.redfish_version,
            registries=None,
            root=self.function_col.root)

    @mock.patch.object(device_function, 'NetworkDeviceFunction', autospec=True)
    def test_get_members(self, device_function_mock):
        members = self.function_col.get_members()
        device_function_mock.assert_has_calls([
            mock.call(
                self.function_col._conn,
                '/redfish/v1/Chassis/System.Embedded.1/NetworkAdapters/'
                'NIC.Integrated.1/NetworkDeviceFunctions/NIC.Integrated.1-1-1',
                redfish_version=self.function_col.redfish_version,
                registries=None,
                root=self.function_col.root
            ),
            mock.call(
                self.function_col._conn,
                '/redfish/v1/Chassis/System.Embedded.1/NetworkAdapters/'
                'NIC.Integrated.1/NetworkDeviceFunctions/NIC.Integrated.1-2-1',
                redfish_version=self.function_col.redfish_version,
                registries=None,
                root=self.function_col.root
            ),
        ])
        self.assertIsInstance(members, list)
        self.assertEqual(2, len(members))
