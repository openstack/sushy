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
from sushy.resources.system import port
from sushy.tests.unit import base


class PortTestCase(base.TestCase):

    def setUp(self):
        super().setUp()
        self.conn = mock.Mock()
        with open('sushy/tests/unit/json_samples/port.json') as f:
            self.json_doc = json.load(f)

        self.conn.get.return_value.json.return_value = self.json_doc

        self.port = port.Port(
            self.conn, '/redfish/v1/Chassis/System.Embedded.1/NetworkAdapters/'
                       'NIC.Integrated.1/Ports/NIC.Integrated.1-1',
            redfish_version='1.0.2')

    def test__parse_attributes(self):
        self.port._parse_attributes(self.json_doc)
        self.assertEqual('1.0.2', self.port.redfish_version)
        self.assertEqual('NIC.Integrated.1-1', self.port.identity)
        self.assertEqual('Instance of Port for NIC',
                         self.port.description)
        self.assertEqual(res_cons.State.ENABLED, self.port.status.state)
        self.assertEqual(res_cons.Health.OK, self.port.status.health)
        self.assertEqual(res_cons.Health.OK, self.port.status.health_rollup)
        self.assertEqual(['01:02:03:04:05:06'],
                         self.port.ethernet.associated_mac_addresses)
        self.assertEqual('0A:1B:2C:3D:4E:5F:6A:7B:8C:9D:0E:1F:2A',
                         self.port.ethernet.lldp_receive.port_id)
        self.assertEqual(net_cons.FlowControl.NONE,
                         self.port.ethernet.flow_control_configuration)
        self.assertEqual(net_cons.FlowControl.NONE,
                         self.port.ethernet.flow_control_status)
        self.assertEqual(net_cons.PortLinkStatus.LINKUP, self.port.link_status)

    def test_lldp_receive_all_fields(self):
        """Test all enhanced LLDP fields are parsed correctly"""
        self.port._parse_attributes(self.json_doc)

        lldp = self.port.ethernet.lldp_receive

        # Test TLV Type 1 - Chassis ID with subtype
        self.assertEqual('c4:7e:e0:e4:55:3f', lldp.chassis_id)
        self.assertEqual(net_cons.IEEE802IdSubtype.MAC_ADDR,
                         lldp.chassis_id_subtype)

        # Test TLV Type 2 - Port ID with subtype
        self.assertEqual('0A:1B:2C:3D:4E:5F:6A:7B:8C:9D:0E:1F:2A',
                         lldp.port_id)
        self.assertEqual(net_cons.IEEE802IdSubtype.IF_NAME,
                         lldp.port_id_subtype)

        # Test TLV Type 5 - System Name
        self.assertEqual('switch-00.example.com', lldp.system_name)

        # Test TLV Type 6 - System Description
        self.assertEqual('Test Software, Version 00.00.00',
                         lldp.system_description)

        # Test TLV Type 7 - System Capabilities
        self.assertIsNotNone(lldp.system_capabilities)
        self.assertEqual(2, len(lldp.system_capabilities))
        self.assertIn(net_cons.LLDPSystemCapabilities.BRIDGE,
                      lldp.system_capabilities)
        self.assertIn(net_cons.LLDPSystemCapabilities.ROUTER,
                      lldp.system_capabilities)

        # Test TLV Type 8 - Management Addresses
        self.assertEqual('192.168.1.1', lldp.management_address_ipv4)
        self.assertEqual('fe80::1', lldp.management_address_ipv6)
        self.assertEqual('c4:7e:e0:e4:55:40', lldp.management_address_mac)
        self.assertEqual(100, lldp.management_vlan_id)

    def test_lldp_receive_minimal_data(self):
        """Test LLDP with minimal data (only mandatory fields)"""
        minimal_doc = self.json_doc.copy()
        minimal_doc['Ethernet']['LLDPReceive'] = {
            "ChassisId": "aa:bb:cc:dd:ee:ff",
            "PortId": "port-1"
        }

        self.port._parse_attributes(minimal_doc)
        lldp = self.port.ethernet.lldp_receive

        # Mandatory fields present
        self.assertEqual('aa:bb:cc:dd:ee:ff', lldp.chassis_id)
        self.assertEqual('port-1', lldp.port_id)

        # Optional fields None
        self.assertIsNone(lldp.chassis_id_subtype)
        self.assertIsNone(lldp.port_id_subtype)
        self.assertIsNone(lldp.system_name)
        self.assertIsNone(lldp.system_description)
        self.assertIsNone(lldp.system_capabilities)
        self.assertIsNone(lldp.management_address_ipv4)

    def test_lldp_receive_empty(self):
        """Test empty LLDPReceive (Dell scenario)"""
        empty_doc = self.json_doc.copy()
        empty_doc['Ethernet']['LLDPReceive'] = {}

        self.port._parse_attributes(empty_doc)
        lldp = self.port.ethernet.lldp_receive

        # All fields should be None
        self.assertIsNone(lldp.chassis_id)
        self.assertIsNone(lldp.port_id)
        self.assertIsNone(lldp.system_name)


class PortCollectionTestCase(base.TestCase):

    def setUp(self):
        super().setUp()
        self.conn = mock.Mock()
        with open('sushy/tests/unit/json_samples/'
                  'port_collection.json') as f:
            self.json_doc = json.load(f)

        self.conn.get.return_value.json.return_value = self.json_doc

        self.port_col = port.PortCollection(
            self.conn, '/redfish/v1/Chassis/System.Embedded.1/NetworkAdapters/'
                       'NIC.Integrated.1/Ports',
            redfish_version='1.0.2')

    def test__parse_attributes(self):
        self.port_col._parse_attributes(self.json_doc)
        self.assertEqual((
            '/redfish/v1/Chassis/System.Embedded.1/NetworkAdapters/'
            'NIC.Integrated.1/Ports/NIC.Integrated.1-1',
            '/redfish/v1/Chassis/System.Embedded.1/NetworkAdapters/'
            'NIC.Integrated.1/Ports/NIC.Integrated.1-2',
            '/redfish/v1/Chassis/System.Embedded.1/NetworkAdapters/'
            'NIC.Integrated.1/Ports/NIC.Integrated.1-3',
            '/redfish/v1/Chassis/System.Embedded.1/NetworkAdapters/'
            'NIC.Integrated.1/Ports/NIC.Integrated.1-4'
        ),
            self.port_col.members_identities)

    @mock.patch.object(port, 'Port', autospec=True)
    def test_get_member(self, Port_mock):
        self.port_col.get_member(
            '/redfish/v1/Chassis/System.Embedded.1/NetworkAdapters/'
            'NIC.Integrated.1/Ports/NIC.Integrated.1-1'
        )
        Port_mock.assert_called_once_with(
            self.port_col._conn,
            '/redfish/v1/Chassis/System.Embedded.1/NetworkAdapters/'
            'NIC.Integrated.1/Ports/NIC.Integrated.1-1',
            redfish_version=self.port_col.redfish_version, registries=None,
            root=self.port_col.root)

    @mock.patch.object(port, 'Port', autospec=True)
    def test_get_members(self, Port_mock):
        members = self.port_col.get_members()
        Port_mock.assert_has_calls([
            mock.call(
                self.port_col._conn,
                '/redfish/v1/Chassis/System.Embedded.1/NetworkAdapters/'
                'NIC.Integrated.1/Ports/NIC.Integrated.1-1',
                redfish_version=self.port_col.redfish_version, registries=None,
                root=self.port_col.root
            ),
            mock.call(
                self.port_col._conn,
                '/redfish/v1/Chassis/System.Embedded.1/NetworkAdapters/'
                'NIC.Integrated.1/Ports/NIC.Integrated.1-2',
                redfish_version=self.port_col.redfish_version, registries=None,
                root=self.port_col.root
            ),
            mock.call(
                self.port_col._conn,
                '/redfish/v1/Chassis/System.Embedded.1/NetworkAdapters/'
                'NIC.Integrated.1/Ports/NIC.Integrated.1-3',
                redfish_version=self.port_col.redfish_version, registries=None,
                root=self.port_col.root
            ),
            mock.call(
                self.port_col._conn,
                '/redfish/v1/Chassis/System.Embedded.1/NetworkAdapters/'
                'NIC.Integrated.1/Ports/NIC.Integrated.1-4',
                redfish_version=self.port_col.redfish_version, registries=None,
                root=self.port_col.root
            ),
        ])
        self.assertIsInstance(members, list)
        self.assertEqual(4, len(members))
