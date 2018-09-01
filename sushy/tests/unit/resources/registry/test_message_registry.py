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

import mock

from sushy.resources import constants as res_cons
from sushy.resources.registry import message_registry
from sushy.tests.unit import base


class MessageRegistryTestCase(base.TestCase):

    def setUp(self):
        super(MessageRegistryTestCase, self).setUp()
        self.conn = mock.Mock()
        with open('sushy/tests/unit/json_samples/message_registry.json') as f:
            self.conn.get.return_value.json.return_value = json.load(f)

        self.registry = message_registry.MessageRegistry(
            self.conn, '/redfish/v1/Registries/Test',
            redfish_version='1.0.2')

    def test__parse_attributes(self):
        self.registry._parse_attributes()
        self.assertEqual('Test.1.0.0', self.registry.identity)
        self.assertEqual('Test Message Registry', self.registry.name)
        self.assertEqual('en', self.registry.language)
        self.assertEqual('This registry defines messages for sushy testing',
                         self.registry.description)
        self.assertEqual('Test', self.registry.registry_prefix)
        self.assertEqual('1.0.0', self.registry.registry_version)
        self.assertEqual('sushy', self.registry.owning_entity)
        self.assertEqual(3, len(self.registry.messages))
        self.assertEqual('Everything OK',
                         self.registry.messages['Success'].description)
        self.assertEqual('Everything done successfully.',
                         self.registry.messages['Success'].message)
        self.assertEqual(res_cons.SEVERITY_OK,
                         self.registry.messages['Success'].severity)
        self.assertEqual(0, self.registry.messages['Success'].number_of_args)
        self.assertEqual(2, len(self.registry.messages['TooBig'].param_types))
        self.assertEqual(res_cons.PARAMTYPE_STRING,
                         self.registry.messages['TooBig'].param_types[0])
        self.assertEqual(res_cons.PARAMTYPE_NUMBER,
                         self.registry.messages['TooBig'].param_types[1])
        self.assertEqual('Panic', self.registry.messages['Failed'].resolution)

    def test__parse_attribtues_unknown_param_type(self):
        self.registry.json['Messages']['Failed']['ParamTypes'] = \
            ['unknown_type']
        self.assertRaisesRegex(KeyError,
                               'unknown_type',
                               self.registry._parse_attributes)
