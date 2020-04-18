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
from sushy.resources.system import ethernet_interface
from sushy.tests.unit import base


class EthernetInterfaceTestCase(base.TestCase):

    def setUp(self):
        super(EthernetInterfaceTestCase, self).setUp()
        self.conn = mock.Mock()
        with open('sushy/tests/unit/json_samples/'
                  'ethernet_interfaces.json') as f:
            self.json_doc = json.load(f)

        self.conn.get.return_value.json.return_value = self.json_doc

        eth_path = ("/redfish/v1/Systems/437XR1138R2/EthernetInterfaces/"
                    "12446A3B0411")
        self.sys_eth = ethernet_interface.EthernetInterface(
            self.conn, eth_path, redfish_version='1.0.2')

    def test__parse_attributes(self):
        self.sys_eth._parse_attributes(self.json_doc)
        self.assertEqual('1.0.2', self.sys_eth.redfish_version)
        self.assertEqual('1', self.sys_eth.identity)
        self.assertEqual('Ethernet Interface', self.sys_eth.name)
        self.assertEqual('System NIC 1', self.sys_eth.description)
        self.assertEqual(
            '12:44:6A:3B:04:11', self.sys_eth.permanent_mac_address)
        self.assertEqual('12:44:6A:3B:04:11', self.sys_eth.mac_address)
        self.assertEqual(res_cons.STATE_ENABLED, self.sys_eth.status.state)
        self.assertEqual(res_cons.HEALTH_OK, self.sys_eth.status.health)
        self.assertEqual(1000, self.sys_eth.speed_mbps)


class EthernetInterfaceCollectionTestCase(base.TestCase):

    def setUp(self):
        super(EthernetInterfaceCollectionTestCase, self).setUp()
        self.conn = mock.Mock()
        with open('sushy/tests/unit/json_samples/'
                  'ethernet_interfaces_collection.json') as f:
            self.json_doc = json.load(f)

        self.conn.get.return_value.json.return_value = self.json_doc

        self.sys_eth_col = ethernet_interface.EthernetInterfaceCollection(
            self.conn, '/redfish/v1/Systems/437XR1138R2/EthernetInterfaces',
            redfish_version='1.0.2')

    def test__parse_attributes(self):
        self.sys_eth_col._parse_attributes(self.json_doc)
        self.assertEqual('1.0.2', self.sys_eth_col.redfish_version)
        self.assertEqual('Ethernet Interface Collection',
                         self.sys_eth_col.name)
        eth_path = ('/redfish/v1/Systems/437XR1138R2/EthernetInterfaces/'
                    '12446A3B0411',)
        self.assertEqual(eth_path, self.sys_eth_col.members_identities)

    @mock.patch.object(ethernet_interface, 'EthernetInterface', autospec=True)
    def test_get_member(self, mock_eth):
        self.sys_eth_col.get_member(
            '/redfish/v1/Systems/437XR1138R2/EthernetInterfaces/'
            '12446A3B0411')
        mock_eth.assert_called_once_with(
            self.sys_eth_col._conn,
            ('/redfish/v1/Systems/437XR1138R2/EthernetInterfaces/'
             '12446A3B0411'),
            self.sys_eth_col.redfish_version, None)

    @mock.patch.object(ethernet_interface, 'EthernetInterface', autospec=True)
    def test_get_members(self, mock_eth):
        members = self.sys_eth_col.get_members()
        eth_path = ("/redfish/v1/Systems/437XR1138R2/EthernetInterfaces/"
                    "12446A3B0411")
        calls = [
            mock.call(self.sys_eth_col._conn, eth_path,
                      self.sys_eth_col.redfish_version, None),
        ]
        mock_eth.assert_has_calls(calls)
        self.assertIsInstance(members, list)
        self.assertEqual(1, len(members))

    def test_summary(self):
        self.conn.get.return_value.json.reset_mock()
        with open('sushy/tests/unit/json_samples/'
                  'ethernet_interfaces.json') as f:
            self.conn.get.return_value.json.return_value = json.load(f)
        expected_summary = {'12:44:6A:3B:04:11': res_cons.STATE_ENABLED}
        actual_summary = self.sys_eth_col.summary
        self.assertEqual(expected_summary, actual_summary)
