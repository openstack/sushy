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
from sushy.resources import ipaddresses as ip_cons
from sushy.resources.system import ethernet_interface
from sushy.tests.unit import base


class ManagerEthernetInterfaceTestCase(base.TestCase):

    def setUp(self):
        super().setUp()
        self.conn = mock.Mock()
        with open('sushy/tests/unit/json_samples/'
                  'manager_ethernet_interfaces.json') as f:
            self.json_doc = json.load(f)

        self.conn.get.return_value.json.return_value = self.json_doc

        self.eth = ethernet_interface.EthernetInterface(
            self.conn, '/redfish/v1/Managers/1/EthernetInterfaces/1',
            redfish_version='1.0.2')

    def test_basic_attributes(self):
        self.assertEqual('1', self.eth.identity)
        self.assertEqual('web483', self.eth.host_name)
        self.assertEqual('web483.contoso.com', self.eth.fqdn)
        self.assertEqual('f82f:ff01:1bb0:7750::1',
                         self.eth.ipv6_default_gateway)
        self.assertTrue(self.eth.auto_neg)
        self.assertTrue(self.eth.full_duplex)
        self.assertEqual(1500, self.eth.mtu_size)
        self.assertTrue(self.eth.interface_enabled)

    def test_name_servers(self):
        self.assertEqual(['names.contoso.com'], self.eth.name_servers)
        self.assertEqual(['10.1.1.100'], self.eth.static_name_servers)

    def test_dhcpv4(self):
        self.assertFalse(self.eth.dhcpv4.dhcp_enabled)
        self.assertFalse(self.eth.dhcpv4.use_dns_servers)
        self.assertFalse(self.eth.dhcpv4.use_domain_name)
        self.assertFalse(self.eth.dhcpv4.use_gateway)
        self.assertFalse(self.eth.dhcpv4.use_ntp_servers)
        self.assertFalse(self.eth.dhcpv4.use_static_routes)

    def test_dhcpv6(self):
        self.assertEqual(ip_cons.DHCPv6OperatingMode.DISABLED,
                         self.eth.dhcpv6.operating_mode)
        self.assertFalse(self.eth.dhcpv6.use_dns_servers)
        self.assertFalse(self.eth.dhcpv6.use_domain_name)
        self.assertFalse(self.eth.dhcpv6.use_ntp_servers)
        self.assertFalse(self.eth.dhcpv6.use_rapid_commit)

    def test_ipv4_addresses(self):
        self.assertEqual(1, len(self.eth.ipv4_addresses))
        addr = self.eth.ipv4_addresses[0]
        self.assertEqual('192.168.0.5', addr.address)
        self.assertEqual('255.255.252.0', addr.subnet_mask)
        self.assertEqual('192.168.0.1', addr.gateway)
        self.assertEqual(ip_cons.IPv4AddressOrigin.STATIC,
                         addr.address_origin)

    def test_ipv4_static_addresses(self):
        self.assertEqual(1, len(self.eth.ipv4_static_addresses))
        addr = self.eth.ipv4_static_addresses[0]
        self.assertEqual('192.168.0.5', addr.address)
        self.assertEqual('255.255.252.0', addr.subnet_mask)
        self.assertEqual('192.168.0.1', addr.gateway)

    def test_ipv6_addresses(self):
        self.assertEqual(1, len(self.eth.ipv6_addresses))
        addr = self.eth.ipv6_addresses[0]
        self.assertEqual('f82f:ff01:1bb0:7750::2', addr.address)
        self.assertEqual(64, addr.prefix_length)
        self.assertEqual(ip_cons.IPv6AddressOrigin.STATIC,
                         addr.address_origin)
        self.assertEqual(ip_cons.AddressState.PREFERRED,
                         addr.address_state)

    def test_ipv6_static_addresses(self):
        self.assertEqual(1, len(self.eth.ipv6_static_addresses))
        addr = self.eth.ipv6_static_addresses[0]
        self.assertEqual('f82f:ff01:1bb0:7750::2', addr.address)
        self.assertEqual(64, addr.prefix_length)

    def test_ipv6_static_default_gateways(self):
        self.assertEqual(1, len(self.eth.ipv6_static_default_gateways))
        gw = self.eth.ipv6_static_default_gateways[0]
        self.assertEqual('f82f:ff01:1bb0:7750::1', gw.address)
        self.assertEqual(64, gw.prefix_length)

    def test_set_static_name_servers(self):
        self.eth.refresh = mock.Mock()
        self.eth.set_static_name_servers(['10.0.0.1', '10.0.0.2'])
        self.conn.patch.assert_called_once_with(
            '/redfish/v1/Managers/1/EthernetInterfaces/1',
            data={'StaticNameServers': ['10.0.0.1', '10.0.0.2']})

    def test_set_dhcpv4_enabled(self):
        self.eth.refresh = mock.Mock()
        self.eth.set_dhcpv4_enabled(True)
        self.conn.patch.assert_called_once_with(
            '/redfish/v1/Managers/1/EthernetInterfaces/1',
            data={'DHCPv4': {'DHCPEnabled': True}})

    def test_set_dhcpv6_operating_mode(self):
        self.eth.refresh = mock.Mock()
        self.eth.set_dhcpv6_operating_mode(
            sushy.DHCPv6OperatingMode.ENABLED)
        self.conn.patch.assert_called_once_with(
            '/redfish/v1/Managers/1/EthernetInterfaces/1',
            data={'DHCPv6': {'OperatingMode': 'Enabled'}})

    def test_set_ipv4_static_addresses(self):
        self.eth.refresh = mock.Mock()
        addrs = [{'Address': '10.0.0.5', 'SubnetMask': '255.255.255.0',
                  'Gateway': '10.0.0.1'}]
        self.eth.set_ipv4_static_addresses(addrs)
        self.conn.patch.assert_called_once_with(
            '/redfish/v1/Managers/1/EthernetInterfaces/1',
            data={'IPv4StaticAddresses': addrs})

    def test_set_ipv6_static_addresses(self):
        self.eth.refresh = mock.Mock()
        addrs = [{'Address': 'fd00::1', 'PrefixLength': 64}]
        self.eth.set_ipv6_static_addresses(addrs)
        self.conn.patch.assert_called_once_with(
            '/redfish/v1/Managers/1/EthernetInterfaces/1',
            data={'IPv6StaticAddresses': addrs})
