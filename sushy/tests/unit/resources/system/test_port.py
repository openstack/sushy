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
