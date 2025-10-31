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
from sushy.resources.system import constants as sys_cons
from sushy.resources.system import pcie_device
from sushy.tests.unit import base


class PCIeDeviceTestCase(base.TestCase):

    def setUp(self):
        super().setUp()
        self.conn = mock.Mock()
        with open('sushy/tests/unit/json_samples/pcie_device.json') as f:
            self.json_doc = json.load(f)

        self.conn.get.return_value.json.return_value = self.json_doc

        self.pcie_dev = pcie_device.PCIeDevice(
            self.conn,
            '/redfish/v1/Chassis/System.Embedded.1/PCIeDevices/196-0',
            redfish_version='1.0.2')

    def test__parse_attributes(self):
        self.pcie_dev._parse_attributes(self.json_doc)
        self.assertEqual('1.0.2', self.pcie_dev.redfish_version)
        self.assertEqual('196-0', self.pcie_dev.identity)
        self.assertEqual('BCM957414A4142CC 10Gb/25Gb Ethernet PCIe',
                         self.pcie_dev.name)
        self.assertEqual('BCM957414A4142CC 10Gb/25Gb Ethernet PCIe',
                         self.pcie_dev.description)
        self.assertEqual('Broadcom Inc. and subsidiaries',
                         self.pcie_dev.manufacturer)
        self.assertEqual(sys_cons.PCIeDeviceType.MULTI_FUNCTION,
                         self.pcie_dev.device_type)
        self.assertEqual('224.1.102.0', self.pcie_dev.firmware_version)
        self.assertIsNone(self.pcie_dev.asset_tag)
        self.assertIsNone(self.pcie_dev.serial_number)
        self.assertIsNone(self.pcie_dev.model)
        self.assertIsNone(self.pcie_dev.part_number)
        self.assertIsNone(self.pcie_dev.sku)

    def test_pcie_interface(self):
        pcie_if = self.pcie_dev.pcie_interface
        self.assertEqual('Gen5', pcie_if.pcie_type)
        self.assertEqual('Gen5', pcie_if.max_pcie_type)
        self.assertEqual(8, pcie_if.lanes_in_use)
        self.assertEqual(8, pcie_if.max_lanes)

    def test_slot_information(self):
        slot = self.pcie_dev.slot
        self.assertEqual(sys_cons.SlotType.HALF_LENGTH, slot.slot_type)
        self.assertEqual('Gen5', slot.pcie_type)
        self.assertEqual(8, slot.lanes)
        self.assertIsNotNone(slot.location)
        self.assertIsNone(slot.lane_splitting)
        self.assertIsNone(slot.hot_pluggable)

    def test_status_field(self):
        status = self.pcie_dev.status
        self.assertEqual(res_cons.State.ENABLED, status.state)
        self.assertEqual(res_cons.Health.OK, status.health)
        self.assertEqual(res_cons.Health.OK, status.health_rollup)

    def test_links_field(self):
        links = self.pcie_dev.links
        self.assertIsNotNone(links)


class PCIeDeviceOnboardTestCase(base.TestCase):

    def setUp(self):
        super().setUp()
        self.conn = mock.Mock()
        with open('sushy/tests/unit/json_samples/'
                  'pcie_device_onboard.json') as f:
            self.json_doc = json.load(f)

        self.conn.get.return_value.json.return_value = self.json_doc

        self.onboard_dev = pcie_device.PCIeDevice(
            self.conn,
            '/redfish/v1/Chassis/System.Embedded.1/PCIeDevices/128-1',
            redfish_version='1.0.2')

    def test_onboard_device_attributes(self):
        self.assertEqual('128-1', self.onboard_dev.identity)
        self.assertEqual('Advanced Micro Devices, Inc. [AMD]',
                         self.onboard_dev.name)
        self.assertEqual('Advanced Micro Devices, Inc. [AMD]',
                         self.onboard_dev.manufacturer)
        self.assertEqual(sys_cons.PCIeDeviceType.MULTI_FUNCTION,
                         self.onboard_dev.device_type)
        self.assertEqual('', self.onboard_dev.firmware_version)

    def test_onboard_device_empty_slot(self):
        slot = self.onboard_dev.slot
        self.assertIsNotNone(slot)
        # Empty slot object should have None values
        self.assertIsNone(slot.slot_type)
        self.assertIsNone(slot.lanes)
        self.assertIsNone(slot.pcie_type)


class PCIeDeviceCollectionTestCase(base.TestCase):

    def setUp(self):
        super().setUp()
        self.conn = mock.Mock()
        with open('sushy/tests/unit/json_samples/'
                  'pcie_device_collection.json') as f:
            self.json_doc = json.load(f)

        self.conn.get.return_value.json.return_value = self.json_doc

        self.collection = pcie_device.PCIeDeviceCollection(
            self.conn, '/redfish/v1/Chassis/System.Embedded.1/PCIeDevices',
            redfish_version='1.0.2')

    def test__parse_attributes(self):
        self.collection._parse_attributes(self.json_doc)
        self.assertEqual('1.0.2', self.collection.redfish_version)
        self.assertEqual('PCIe Device Collection', self.collection.name)
        self.assertEqual(
            ('/redfish/v1/Chassis/System.Embedded.1/PCIeDevices/196-0',
             '/redfish/v1/Chassis/System.Embedded.1/PCIeDevices/65-0'),
            self.collection.members_identities)

    @mock.patch.object(pcie_device, 'PCIeDevice', autospec=True)
    def test_get_member(self, mock_pcie_device):
        self.collection.get_member(
            '/redfish/v1/Chassis/System.Embedded.1/'
            'PCIeDevices/196-0')
        mock_pcie_device.assert_called_once_with(
            self.collection._conn,
            '/redfish/v1/Chassis/System.Embedded.1/'
            'PCIeDevices/196-0',
            redfish_version=self.collection.redfish_version,
            registries=None, root=self.collection.root)

    @mock.patch.object(pcie_device, 'PCIeDevice', autospec=True)
    def test_get_members(self, mock_pcie_device):
        members = self.collection.get_members()
        calls = [
            mock.call(self.collection._conn,
                      '/redfish/v1/Chassis/System.Embedded.1/'
                      'PCIeDevices/196-0',
                      redfish_version=self.collection.redfish_version,
                      registries=None, root=self.collection.root),
            mock.call(self.collection._conn,
                      '/redfish/v1/Chassis/System.Embedded.1/'
                      'PCIeDevices/65-0',
                      redfish_version=self.collection.redfish_version,
                      registries=None, root=self.collection.root)
        ]
        mock_pcie_device.assert_has_calls(calls)
        self.assertIsInstance(members, list)
        self.assertEqual(2, len(members))


class PCIeFunctionTestCase(base.TestCase):

    def setUp(self):
        super().setUp()
        self.conn = mock.Mock()
        with open('sushy/tests/unit/json_samples/pcie_function.json') as f:
            self.json_doc = json.load(f)

        self.conn.get.return_value.json.return_value = self.json_doc

        self.pcie_func = pcie_device.PCIeFunction(
            self.conn,
            '/redfish/v1/Chassis/System.Embedded.1/PCIeDevices/196-0/'
            'PCIeFunctions/196-0-1',
            redfish_version='1.0.2')

    def test__parse_attributes(self):
        self.pcie_func._parse_attributes(self.json_doc)
        self.assertEqual('1.0.2', self.pcie_func.redfish_version)
        self.assertEqual('196-0-1', self.pcie_func.identity)
        self.assertEqual('BCM957414A4142CC 10Gb/25Gb Ethernet PCIe',
                         self.pcie_func.name)
        self.assertEqual('BCM957414A4142CC 10Gb/25Gb Ethernet PCIe',
                         self.pcie_func.description)

    def test_function_properties(self):
        self.assertEqual(1, self.pcie_func.function_id)
        self.assertEqual(sys_cons.FunctionType.PHYSICAL,
                         self.pcie_func.function_type)
        self.assertEqual(sys_cons.FunctionProtocol.PCIE,
                         self.pcie_func.function_protocol)
        self.assertEqual(sys_cons.DeviceClass.NETWORK_CONTROLLER,
                         self.pcie_func.device_class)
        self.assertTrue(self.pcie_func.enabled)

    def test_device_identification_fields(self):
        self.assertEqual('0x16d7', self.pcie_func.device_id)
        self.assertEqual('0x14e4', self.pcie_func.vendor_id)
        self.assertEqual('0x1402', self.pcie_func.subsystem_id)
        self.assertEqual('0x14e4', self.pcie_func.subsystem_vendor_id)
        self.assertEqual('0x01', self.pcie_func.revision_id)
        self.assertEqual('0x000002', self.pcie_func.class_code)

    def test_pci_addressing_fields(self):
        self.assertEqual('0x03', self.pcie_func.bus_number)
        self.assertEqual('0x00', self.pcie_func.device_number)
        self.assertEqual('0x01', self.pcie_func.function_number)
        self.assertEqual('0x0000', self.pcie_func.segment_number)

    def test_status_field(self):
        status = self.pcie_func.status
        self.assertEqual(res_cons.State.ENABLED, status.state)
        self.assertEqual(res_cons.Health.OK, status.health)
        self.assertEqual(res_cons.Health.OK, status.health_rollup)

    def test_links_field(self):
        links = self.pcie_func.links
        self.assertIsNotNone(links)


class PCIeFunctionCollectionTestCase(base.TestCase):

    def setUp(self):
        super().setUp()
        self.conn = mock.Mock()
        with open('sushy/tests/unit/json_samples/'
                  'pcie_function_collection.json') as f:
            self.json_doc = json.load(f)

        self.conn.get.return_value.json.return_value = self.json_doc

        self.collection = pcie_device.PCIeFunctionCollection(
            self.conn,
            '/redfish/v1/Chassis/System.Embedded.1/PCIeDevices/196-0/'
            'PCIeFunctions',
            redfish_version='1.0.2')

    def test__parse_attributes(self):
        self.collection._parse_attributes(self.json_doc)
        self.assertEqual('1.0.2', self.collection.redfish_version)
        self.assertEqual('PCIeFunction Collection', self.collection.name)
        self.assertEqual(
            ('/redfish/v1/Chassis/System.Embedded.1/PCIeDevices/196-0/'
             'PCIeFunctions/196-0-0',
             '/redfish/v1/Chassis/System.Embedded.1/PCIeDevices/196-0/'
             'PCIeFunctions/196-0-1'),
            self.collection.members_identities)

    def test_function_count_property(self):
        with mock.patch.object(
            self.collection, 'get_members', autospec=True,
            return_value=[mock.Mock(), mock.Mock()]):
            self.assertEqual(2, self.collection.function_count)

    @mock.patch.object(pcie_device, 'PCIeFunction', autospec=True)
    def test_get_member(self, mock_pcie_function):
        self.collection.get_member(
            '/redfish/v1/Chassis/System.Embedded.1/PCIeDevices/196-0/'
            'PCIeFunctions/196-0-1')
        mock_pcie_function.assert_called_once_with(
            self.collection._conn,
            '/redfish/v1/Chassis/System.Embedded.1/PCIeDevices/196-0/'
            'PCIeFunctions/196-0-1',
            redfish_version=self.collection.redfish_version,
            registries=None, root=self.collection.root)

    @mock.patch.object(pcie_device, 'PCIeFunction', autospec=True)
    def test_get_members(self, mock_pcie_function):
        members = self.collection.get_members()
        calls = [
            mock.call(self.collection._conn,
                      '/redfish/v1/Chassis/System.Embedded.1/PCIeDevices/'
                      '196-0/PCIeFunctions/196-0-0',
                      redfish_version=self.collection.redfish_version,
                      registries=None, root=self.collection.root),
            mock.call(self.collection._conn,
                      '/redfish/v1/Chassis/System.Embedded.1/PCIeDevices/'
                      '196-0/PCIeFunctions/196-0-1',
                      redfish_version=self.collection.redfish_version,
                      registries=None, root=self.collection.root)
        ]
        mock_pcie_function.assert_has_calls(calls)
        self.assertIsInstance(members, list)
        self.assertEqual(2, len(members))


class PCIeDeviceFunctionsTestCase(base.TestCase):

    def setUp(self):
        super().setUp()
        self.conn = mock.Mock()
        with open('sushy/tests/unit/json_samples/pcie_device.json') as f:
            self.json_doc = json.load(f)

        self.conn.get.return_value.json.return_value = self.json_doc

        self.pcie_dev = pcie_device.PCIeDevice(
            self.conn,
            '/redfish/v1/Chassis/System.Embedded.1/PCIeDevices/196-0',
            redfish_version='1.0.2')

    @mock.patch.object(pcie_device, 'PCIeFunctionCollection', autospec=True)
    def test_pcie_functions_property(self, mock_collection):
        # Test normal case with PCIeFunctions present
        _ = self.pcie_dev.pcie_functions
        mock_collection.assert_called_once_with(
            self.pcie_dev._conn,
            '/redfish/v1/Chassis/System.Embedded.1/PCIeDevices/196-0/'
            'PCIeFunctions',
            redfish_version=self.pcie_dev.redfish_version,
            registries=self.pcie_dev.registries,
            root=self.pcie_dev.root)

    @mock.patch.object(pcie_device, 'PCIeFunctionCollection', autospec=True)
    @mock.patch('sushy.utils.get_sub_resource_path_by', autospec=True)
    def test_pcie_functions_missing_attribute(
        self, mock_get_path, mock_collection):
        from sushy import exceptions
        # Simulate MissingAttributeError when PCIeFunctions is not supported
        mock_get_path.side_effect = exceptions.MissingAttributeError(
            attribute='PCIeFunctions', resource=self.pcie_dev._path)

        _ = self.pcie_dev.pcie_functions
        # Should create empty collection

        mock_collection.assert_called_once_with(
            self.pcie_dev._conn, "/empty",
            redfish_version=self.pcie_dev.redfish_version,
            registries=self.pcie_dev.registries,
            root=self.pcie_dev.root)
