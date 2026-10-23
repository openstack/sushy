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

from sushy.resources.manager import constants
from sushy.resources.manager import network_protocol
from sushy.tests.unit import base


class ManagerNetworkProtocolTestCase(base.TestCase):

    def setUp(self):
        super().setUp()
        self.conn = mock.Mock()
        with open('sushy/tests/unit/json_samples/'
                  'manager_network_protocol.json') as f:
            self.json_doc = json.load(f)

        self.conn.get.return_value.json.return_value = self.json_doc

        self.net_proto = network_protocol.ManagerNetworkProtocol(
            self.conn, '/redfish/v1/Managers/BMC/NetworkProtocol',
            redfish_version='1.0.2')

    def test__parse_attributes(self):
        self.net_proto._parse_attributes(self.json_doc)
        self.assertEqual('NetworkProtocol', self.net_proto.identity)
        self.assertEqual('Manager Network Protocol', self.net_proto.name)
        self.assertEqual('Manager Network Service',
                         self.net_proto.description)
        self.assertEqual('web483', self.net_proto.hostname)
        self.assertEqual('web483.contoso.com', self.net_proto.fqdn)

    def test_dhcp(self):
        self.assertTrue(self.net_proto.dhcp.protocol_enabled)
        self.assertIsNone(self.net_proto.dhcp.port)

    def test_dhcpv6(self):
        self.assertTrue(self.net_proto.dhcpv6.protocol_enabled)
        self.assertIsNone(self.net_proto.dhcpv6.port)

    def test_ntp(self):
        self.assertTrue(self.net_proto.ntp.protocol_enabled)
        self.assertEqual(123, self.net_proto.ntp.port)
        self.assertEqual(['ntp1.contoso.com', 'ntp2.contoso.com'],
                         self.net_proto.ntp.ntp_servers)

    def test_ssh(self):
        self.assertTrue(self.net_proto.ssh.protocol_enabled)
        self.assertEqual(22, self.net_proto.ssh.port)

    def test_ipmi(self):
        self.assertTrue(self.net_proto.ipmi.protocol_enabled)
        self.assertEqual(623, self.net_proto.ipmi.port)

    def test_set_dhcpv4_enabled(self):
        self.net_proto.refresh = mock.Mock()
        self.net_proto.set_protocol_enabled(
            constants.NetworkProtocolType.DHCPv4, False)
        self.conn.patch.assert_called_once_with(
            '/redfish/v1/Managers/BMC/NetworkProtocol',
            data={'DHCP': {'ProtocolEnabled': False}})

    def test_set_ipmi_enabled(self):
        self.net_proto.refresh = mock.Mock()
        self.net_proto.set_protocol_enabled(
            constants.NetworkProtocolType.IPMI, False)
        self.conn.patch.assert_called_once_with(
            '/redfish/v1/Managers/BMC/NetworkProtocol',
            data={'IPMI': {'ProtocolEnabled': False}})
