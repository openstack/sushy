#    Copyright (c) 2021 Anexia Internetdienstleistungs GmbH
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
from sushy.resources.system.network import adapter
from sushy.resources.system.network import device_function
from sushy.resources.system.network import port
from sushy.tests.unit import base


class NetworkAdapterTestCase(base.TestCase):

    def setUp(self):
        super(NetworkAdapterTestCase, self).setUp()
        self.conn = mock.Mock()
        with open('sushy/tests/unit/json_samples/network_adapter.json') as f:
            self.json_doc = json.load(f)

        self.conn.get.return_value.json.return_value = self.json_doc

        self.adapter = adapter.NetworkAdapter(
            self.conn, '/redfish/v1/Chassis/System.Embedded.1/NetworkAdapters/'
                       'NIC.Integrated.1',
            redfish_version='1.0.2')

    def test__parse_attributes(self):
        self.adapter._parse_attributes(self.json_doc)
        self.assertEqual('1.0.2', self.adapter.redfish_version)
        self.assertEqual('NIC.Integrated.1', self.adapter.identity)
        self.assertEqual('Network Adapter View', self.adapter.name)
        self.assertEqual('Network Adapter View', self.adapter.description)
        self.assertEqual('0R887V', self.adapter.part_number)
        self.assertEqual('IL7403101N00ZJ', self.adapter.serial_number)
        self.assertEqual('Mellanox Technologies', self.adapter.manufacturer)
        self.assertEqual('MLNX 25GbE 2P ConnectX4LX RNDC', self.adapter.model)
        self.assertEqual(res_cons.STATE_ENABLED, self.adapter.status.state)
        self.assertEqual(res_cons.HEALTH_OK, self.adapter.status.health)
        self.assertEqual(res_cons.HEALTH_OK, self.adapter.status.health_rollup)

    def test_network_ports(self):
        self.conn.get.return_value.json.reset_mock()
        with open('sushy/tests/unit/'
                  'json_samples/network_port_collection.json') as f:
            self.conn.get.return_value.json.return_value = json.load(f)
        actual_network_ports = self.adapter.network_ports
        self.assertIsInstance(actual_network_ports,
                              port.NetworkPortCollection)
        self.conn.get.return_value.json.assert_called_once_with()

    def test_network_ports_cached(self):
        self.conn.get.return_value.json.reset_mock()
        with open('sushy/tests/unit/'
                  'json_samples/network_port_collection.json') as f:
            self.conn.get.return_value.json.return_value = json.load(f)
        actual_ports = self.adapter.network_ports
        self.conn.get.return_value.json.reset_mock()
        self.assertIs(actual_ports,
                      self.adapter.network_ports)
        self.conn.get.return_value.json.assert_not_called()

    def test_network_ports_refresh(self):
        with open('sushy/tests/unit/'
                  'json_samples/network_port_collection.json') as f:
            self.conn.get.return_value.json.return_value = json.load(f)
        ports = self.adapter.network_ports
        self.assertIsInstance(ports, port.NetworkPortCollection)

        with open('sushy/tests/unit/'
                  'json_samples/network_adapter.json') as f:
            self.conn.get.return_value.json.return_value = json.load(f)

        self.adapter.invalidate()
        self.adapter.refresh(force=False)

        self.assertTrue(ports._is_stale)

        with open('sushy/tests/unit/'
                  'json_samples/network_port_collection.json') as f:
            self.conn.get.return_value.json.return_value = json.load(f)
        self.assertIsInstance(self.adapter.network_ports,
                              port.NetworkPortCollection)

    def test_network_device_functions(self):
        self.conn.get.return_value.json.reset_mock()
        with open('sushy/tests/unit/json_samples/'
                  'network_device_function_collection.json') as f:
            self.conn.get.return_value.json.return_value = json.load(f)
        actual_functions = self.adapter.network_device_functions
        self.assertIsInstance(actual_functions,
                              device_function.NetworkDeviceFunctionCollection)
        self.conn.get.return_value.json.assert_called_once_with()

    def test_network_device_functions_cached(self):
        self.conn.get.return_value.json.reset_mock()
        with open('sushy/tests/unit/json_samples/'
                  'network_device_function_collection.json') as f:
            self.conn.get.return_value.json.return_value = json.load(f)
        actual_functions = self.adapter.network_device_functions
        self.conn.get.return_value.json.reset_mock()
        self.assertIs(actual_functions,
                      self.adapter.network_device_functions)
        self.conn.get.return_value.json.assert_not_called()

    def test_network_device_functions_refresh(self):
        with open('sushy/tests/unit/json_samples/'
                  'network_device_function_collection.json') as f:
            self.conn.get.return_value.json.return_value = json.load(f)
        functions = self.adapter.network_device_functions
        self.assertIsInstance(functions,
                              device_function.NetworkDeviceFunctionCollection)

        with open('sushy/tests/unit/json_samples/'
                  'network_adapter.json') as f:
            self.conn.get.return_value.json.return_value = json.load(f)

        self.adapter.invalidate()
        self.adapter.refresh(force=False)

        self.assertTrue(functions._is_stale)

        with open('sushy/tests/unit/json_samples/'
                  'network_device_function_collection.json') as f:
            self.conn.get.return_value.json.return_value = json.load(f)
        self.assertIsInstance(self.adapter.network_device_functions,
                              device_function.NetworkDeviceFunctionCollection)


class NetworkAdapterCollectionTestCase(base.TestCase):

    def setUp(self):
        super(NetworkAdapterCollectionTestCase, self).setUp()
        self.conn = mock.Mock()
        with open('sushy/tests/unit/json_samples/'
                  'network_adapter_collection.json') as f:
            self.json_doc = json.load(f)

        self.conn.get.return_value.json.return_value = self.json_doc

        self.adapter_col = adapter.NetworkAdapterCollection(
            self.conn, '/redfish/v1/Chassis/System.Embedded.1/NetworkAdapters',
            redfish_version='1.0.2')

    def test__parse_attributes(self):
        self.adapter_col._parse_attributes(self.json_doc)
        self.assertEqual('1.0.2', self.adapter_col.redfish_version)
        self.assertEqual('Network Adapter Collection', self.adapter_col.name)
        self.assertEqual(('/redfish/v1/Chassis/System.Embedded.1/'
                          'NetworkAdapters/NIC.Integrated.1',),
                         self.adapter_col.members_identities)

    @mock.patch.object(adapter, 'NetworkAdapter', autospec=True)
    def test_get_member(self, mock_interface):
        self.adapter_col.get_member(
            '/redfish/v1/Chassis/System.Embedded.1/'
            'NetworkAdapters/NIC.Integrated.1'
        )
        mock_interface.assert_called_once_with(
            self.adapter_col._conn,
            '/redfish/v1/Chassis/System.Embedded.1/'
            'NetworkAdapters/NIC.Integrated.1',
            redfish_version=self.adapter_col.redfish_version,
            registries=None, root=self.adapter_col.root)

    @mock.patch.object(adapter, 'NetworkAdapter', autospec=True)
    def test_get_members(self, mock_interface):
        members = self.adapter_col.get_members()
        calls = [
            mock.call(self.adapter_col._conn,
                      '/redfish/v1/Chassis/System.Embedded.1/'
                      'NetworkAdapters/NIC.Integrated.1',
                      redfish_version=self.adapter_col.redfish_version,
                      registries=None, root=self.adapter_col.root),
        ]
        mock_interface.assert_has_calls(calls)
        self.assertIsInstance(members, list)
        self.assertEqual(1, len(members))
