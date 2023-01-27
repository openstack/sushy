# All Rights Reserved.
#
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

from sushy.resources.registry import attribute_registry
from sushy.tests.unit import base


class AttributeRegistryTestCase(base.TestCase):

    def setUp(self):
        super(AttributeRegistryTestCase, self).setUp()
        self.conn = mock.Mock()
        with open('sushy/tests/unit/json_samples/'
                  'bios_attribute_registry.json') as f:
            self.json_doc = json.load(f)

        self.conn.get.return_value.json.return_value = self.json_doc

        self.registry = attribute_registry.AttributeRegistry(
            self.conn, '/redfish/v1/Test/Bios/BiosRegistry',
            redfish_version='1.0.2')

    def test__parse_attributes(self):
        self.registry._parse_attributes(self.json_doc)
        self.assertEqual('BiosAttributeRegistryP89.v1_0_0',
                         self.registry.identity)
        self.assertEqual('BIOS Attribute Registry', self.registry.name)
        self.assertEqual('en', self.registry.language)
        self.assertEqual('This is a test of BIOS Attribute Registry',
                         self.registry.description)
        self.assertEqual('1.0.0', self.registry.registry_version)
        self.assertEqual('VendorA', self.registry.owning_entity)
        self.assertEqual([{'FirmwareVersion': '2.0', 'ProductName': 'Ultra 4',
                          'SystemId': 'URGR8'}],
                         self.registry.supported_systems)
        attributes = self.registry.registry_entries.attributes[0]
        self.assertEqual('SystemModelName', attributes.name)
        self.assertEqual('System Model Name', attributes.display_name)
        self.assertEqual(True, attributes.immutable)
        self.assertEqual(True, attributes.read_only)
        self.assertEqual('String', attributes.attribute_type)

        attributes = self.registry.registry_entries.attributes[1]
        self.assertEqual('ProcVirtualization', attributes.name)
        self.assertEqual('Virtualization Technology', attributes.display_name)
        self.assertEqual(False, attributes.immutable)
        self.assertEqual(False, attributes.read_only)
        self.assertEqual(True, attributes.reset_required)
        self.assertEqual('Enumeration', attributes.attribute_type)
        self.assertEqual([{'ValueDisplayName': 'Enabled',
                           'ValueName': 'Enabled'},
                          {'ValueDisplayName': 'Disabled',
                           'ValueName': 'Disabled'}],
                         attributes.allowable_values)

    def test__parse_attributes_zt(self):
        self.conn = mock.Mock()
        with open('sushy/tests/unit/json_samples/'
                  'bios_attribute_registry_zthardware.json') as f:
            self.json_doc = json.load(f)

        self.conn.get.return_value.json.return_value = self.json_doc
        self.registry = attribute_registry.AttributeRegistry(
            self.conn,
            '/redfish/v1/Registries/'
            'BiosAttributeRegistryProt0.208.208.0.json',
            redfish_version='1.0.2')

        self.registry._parse_attributes(self.json_doc)
        self.assertEqual('BiosAttributeRegistryProt0.208.208.0',
                         self.registry.identity)
        self.assertEqual('Prot0 BIOS Attribute Registry', self.registry.name)
        self.assertEqual('en-US', self.registry.language)
        self.assertEqual('This registry defines a representation of '
                         'BIOS Attribute instances',
                         self.registry.description)
        self.assertEqual('208.208.0', self.registry.registry_version)
        self.assertEqual('AMI', self.registry.owning_entity)

        attributes = self.registry.registry_entries.attributes[0]
        self.assertEqual('TCG003', attributes.name)
        self.assertEqual('TPM SUPPORT', attributes.display_name)
        self.assertEqual('Enable', attributes.default_value)
        self.assertIsNone(attributes.immutable)
        self.assertEqual(False, attributes.read_only)
        self.assertEqual('Enumeration', attributes.attribute_type)
        self.assertEqual(True, attributes.reset_required)
        self.assertEqual([{'ValueDisplayName': 'Disable',
                           'ValueName': 'Disable'},
                          {'ValueDisplayName': 'Enable',
                           'ValueName': 'Enable'}],
                         attributes.allowable_values)
