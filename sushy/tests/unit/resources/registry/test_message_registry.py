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

from sushy import exceptions
from sushy.resources import base as sushy_base
from sushy.resources import constants as res_cons
from sushy.resources.registry import attribute_registry
from sushy.resources.registry import constants as reg_cons
from sushy.resources.registry import message_registry
from sushy.tests.unit import base


class MessageRegistryTestCase(base.TestCase):

    def setUp(self):
        super(MessageRegistryTestCase, self).setUp()
        self.conn = mock.Mock()
        with open('sushy/tests/unit/json_samples/message_registry.json') as f:
            self.json_doc = json.load(f)

        self.conn.get.return_value.json.return_value = self.json_doc

        self.registry = message_registry.MessageRegistry(
            self.conn, '/redfish/v1/Registries/Test',
            redfish_version='1.0.2')

    def test__parse_attributes(self):
        self.registry._parse_attributes(self.json_doc)
        self.assertEqual('Test.1.1.1', self.registry.identity)
        self.assertEqual('Test Message Registry', self.registry.name)
        self.assertEqual('en', self.registry.language)
        self.assertEqual('This registry defines messages for sushy testing',
                         self.registry.description)
        self.assertEqual('Test', self.registry.registry_prefix)
        self.assertEqual('1.1.1', self.registry.registry_version)
        self.assertEqual('sushy', self.registry.owning_entity)
        self.assertEqual(4, len(self.registry.messages))
        self.assertEqual('Everything OK',
                         self.registry.messages['Success'].description)
        self.assertEqual('Everything done successfully.',
                         self.registry.messages['Success'].message)
        self.assertEqual(res_cons.Severity.OK,
                         self.registry.messages['Success'].severity)
        self.assertEqual(0, self.registry.messages['Success'].number_of_args)
        self.assertEqual(2, len(self.registry.messages['TooBig'].param_types))
        self.assertEqual(reg_cons.MessageParamType.STRING,
                         self.registry.messages['TooBig'].param_types[0])
        self.assertEqual(reg_cons.MessageParamType.NUMBER,
                         self.registry.messages['TooBig'].param_types[1])
        self.assertEqual('Panic', self.registry.messages['Failed'].resolution)
        self.assertEqual(
            2, len(self.registry.messages['MissingThings'].param_types))
        self.assertEqual(res_cons.Severity.WARNING,
                         self.registry.messages['MissingThings'].severity)
        self.assertEqual(
            res_cons.PARAMTYPE_STRING,
            self.registry.messages['MissingThings'].param_types[0])
        self.assertEqual(
            res_cons.PARAMTYPE_NUMBER,
            self.registry.messages['MissingThings'].param_types[1])
        self.assertEqual(
            'Try Later', self.registry.messages['MissingThings'].resolution)

    def test__parse_attributes_return(self):
        attributes = self.registry._parse_attributes(self.json_doc)

        self.assertEqual({'Failed':
                          {'description': 'Nothing is OK',
                           'message': 'The property %1 broke everything.',
                           'number_of_args': 1,
                           'param_types': [reg_cons.MessageParamType.STRING],
                           'resolution': 'Panic',
                           'severity': res_cons.Severity.CRITICAL},
                          'MissingThings':
                          {'description': '',
                           'message':
                           "Property's %1 value cannot be less than %2.",
                           'number_of_args': 2,
                           'param_types': [reg_cons.MessageParamType.STRING,
                                           reg_cons.MessageParamType.NUMBER],
                           'resolution': 'Try Later',
                           'severity': res_cons.Severity.WARNING},
                          'Success':
                          {'description': 'Everything OK',
                           'message': 'Everything done successfully.',
                           'number_of_args': 0, 'param_types': None,
                           'resolution': 'None',
                           'severity': res_cons.Severity.OK},
                          'TooBig':
                          {'description': 'Value too big',
                           'message':
                           "Property's %1 value cannot be greater than %2.",
                           'number_of_args': 2,
                           'param_types': [reg_cons.MessageParamType.STRING,
                                           reg_cons.MessageParamType.NUMBER],
                           'resolution': 'Try again',
                           'severity': res_cons.Severity.WARNING}},
                         attributes.get('messages'))

    def test__parse_attributes_missing_msg_desc(self):
        self.json_doc['Messages']['Success'].pop('Description')
        self.registry._parse_attributes(self.json_doc)
        self.assertEqual('', self.registry.messages['Success'].description)

    def test__parse_attributes_missing_msg_severity(self):
        self.json_doc['Messages']['Success'].pop('Severity')
        self.registry._parse_attributes(self.json_doc)
        self.assertEqual(res_cons.Severity.WARNING,
                         self.registry.messages['Success'].severity)

    def test__parse_attributes_unknown_param_type(self):
        self.registry.json['Messages']['Failed']['ParamTypes'] = \
            ['unknown_type']
        self.assertRaisesRegex(exceptions.MalformedAttributeError,
                               'unknown_type',
                               self.registry._parse_attributes, self.json_doc)

    def test_parse_message(self):
        conn = mock.Mock()
        with open('sushy/tests/unit/json_samples/message_registry.json') as f:
            conn.get.return_value.json.return_value = json.load(f)
        registry = message_registry.MessageRegistry(
            conn, '/redfish/v1/Registries/Test',
            redfish_version='1.0.2')
        registries = {'Test.1.0.0': registry}
        message_field = sushy_base.MessageListField('Foo')
        message_field.message_id = 'Test.1.0.0.TooBig'
        message_field.message_args = ['arg1', 10]
        message_field.severity = None
        message_field.resolution = None

        parsed_msg = message_registry.parse_message(registries, message_field)

        self.assertEqual('Try again', parsed_msg.resolution)
        self.assertEqual(res_cons.Severity.WARNING, parsed_msg.severity)
        self.assertEqual('Property\'s arg1 value cannot be greater than 10.',
                         parsed_msg.message)

    def test_parse_message_with_severity_resolution_no_args(self):
        conn = mock.Mock()
        with open('sushy/tests/unit/json_samples/message_registry.json') as f:
            conn.get.return_value.json.return_value = json.load(f)
        registry = message_registry.MessageRegistry(
            conn, '/redfish/v1/Registries/Test',
            redfish_version='1.0.2')
        registries = {'Test.1.0.0': registry}
        message_field = sushy_base.MessageListField('Foo')
        message_field.message_id = 'Test.1.0.0.Success'
        message_field.severity = res_cons.Severity.OK
        message_field.resolution = 'Do nothing'

        parsed_msg = message_registry.parse_message(registries, message_field)

        self.assertEqual('Do nothing', parsed_msg.resolution)
        self.assertEqual(res_cons.Severity.OK, parsed_msg.severity)
        self.assertEqual('Everything done successfully.',
                         parsed_msg.message)

    def test_parse_message_bad_registry(self):
        conn = mock.Mock()
        with open('sushy/tests/unit/json_samples/message_registry.json') as f:
            conn.get.return_value.json.return_value = json.load(f)
        registry = message_registry.MessageRegistry(
            conn, '/redfish/v1/Registries/Test',
            redfish_version='1.0.2')
        registries = {'Test.1.0.0': registry}
        message_field = sushy_base.MessageListField('Foo')
        message_field.message_id = 'BadRegistry.TooBig'

        parsed_msg = message_registry.parse_message(registries, message_field)

        self.assertEqual(message_field, parsed_msg)

    def test_parse_message_bad_message_key_existing_message(self):
        conn = mock.Mock()
        with open('sushy/tests/unit/json_samples/message_registry.json') as f:
            conn.get.return_value.json.return_value = json.load(f)
        registry = message_registry.MessageRegistry(
            conn, '/redfish/v1/Registries/Test',
            redfish_version='1.0.2')
        registries = {'Test.1.0.0': registry}
        message_field = sushy_base.MessageListField('Foo')
        message_field.message_id = 'Test.1.0.0.BadMessageKey'
        message_field.message = 'Message'

        parsed_msg = message_registry.parse_message(registries, message_field)

        self.assertEqual(message_field.message, 'Message')
        self.assertEqual(message_field.message, parsed_msg.message)

    def test_parse_message_bad_message_key_no_existing_message(self):
        conn = mock.Mock()
        with open('sushy/tests/unit/json_samples/message_registry.json') as f:
            conn.get.return_value.json.return_value = json.load(f)
        registry = message_registry.MessageRegistry(
            conn, '/redfish/v1/Registries/Test',
            redfish_version='1.0.2')
        registries = {'Test.1.0.0': registry}
        message_field = sushy_base.MessageListField('Foo')
        message_field.message_id = 'Test.1.0.0.BadMessageKey'
        message_field.message = None

        parsed_msg = message_registry.parse_message(registries, message_field)

        self.assertEqual(message_field.message, 'unknown')
        self.assertEqual(message_field.message, parsed_msg.message)

    def test_parse_message_fallback_to_messages(self):
        conn = mock.Mock()
        with open('sushy/tests/unit/json_samples/message_registry.json') as f:
            conn.get.return_value.json.return_value = json.load(f)
        registry = message_registry.MessageRegistry(
            conn, '/redfish/v1/Registries/Test',
            redfish_version='1.0.2')
        registries = {'Messages': registry}
        message_field = sushy_base.MessageListField('Foo')
        message_field.message_id = 'Success'
        message_field.severity = res_cons.Severity.OK
        message_field.resolution = 'Do nothing'

        parsed_msg = message_registry.parse_message(registries, message_field)

        self.assertEqual('Do nothing', parsed_msg.resolution)
        self.assertEqual(res_cons.Severity.OK, parsed_msg.severity)
        self.assertEqual('Everything done successfully.',
                         parsed_msg.message)

    def test_parse_message_fallback_to_basemessages(self):
        conn = mock.Mock()
        with open('sushy/tests/unit/json_samples/message_registry.json') as f:
            conn.get.return_value.json.return_value = json.load(f)
        registry = message_registry.MessageRegistry(
            conn, '/redfish/v1/Registries/Test',
            redfish_version='1.0.2')
        registries = {'BaseMessages': registry}
        message_field = sushy_base.MessageListField('Foo')
        message_field.message_id = 'Success'
        message_field.severity = res_cons.Severity.OK
        message_field.resolution = 'Do nothing'

        parsed_msg = message_registry.parse_message(registries, message_field)

        self.assertEqual('Do nothing', parsed_msg.resolution)
        self.assertEqual(res_cons.Severity.OK, parsed_msg.severity)
        self.assertEqual('Everything done successfully.',
                         parsed_msg.message)

    def test_parse_message_fallback_failed(self):
        conn = mock.Mock()
        with open('sushy/tests/unit/json_samples/message_registry.json') as f:
            conn.get.return_value.json.return_value = json.load(f)
        registry = message_registry.MessageRegistry(
            conn, '/redfish/v1/Registries/Test',
            redfish_version='1.0.2')
        registries = {'Test.1.0.0': registry}
        message_field = sushy_base.MessageListField('Foo')
        message_field.message_id = 'BadMessageKey'
        message_field.message = None

        parsed_msg = message_registry.parse_message(registries, message_field)

        self.assertEqual(message_field.message, 'unknown')
        self.assertEqual(message_field.message, parsed_msg.message)

    def test_parse_message_not_enough_args(self):
        conn = mock.Mock()
        with open('sushy/tests/unit/json_samples/message_registry.json') as f:
            conn.get.return_value.json.return_value = json.load(f)
        registry = message_registry.MessageRegistry(
            conn, '/redfish/v1/Registries/Test',
            redfish_version='1.0.2')
        registries = {'Test.1.0.0': registry}
        message_field = sushy_base.MessageListField('Foo')
        message_field.message_id = 'Test.1.0.0.TooBig'
        message_field.message_args = ['arg1']
        message_field.severity = None
        message_field.resolution = None

        parsed_msg = message_registry.parse_message(registries, message_field)

        self.assertEqual('Try again', parsed_msg.resolution)
        self.assertEqual(res_cons.Severity.WARNING, parsed_msg.severity)
        self.assertEqual('Property\'s arg1 value cannot be greater than '
                         'unknown.', parsed_msg.message)

    def test_parse_message_multiple_registries(self):
        conn = mock.Mock()
        with open('sushy/tests/unit/json_samples/message_registry.json') as f:
            conn.get.return_value.json.return_value = json.load(f)
        msg_registry = message_registry.MessageRegistry(
            conn, '/redfish/v1/Registries/Test',
            redfish_version='1.0.2')
        attr_registry = attribute_registry.AttributeRegistry(
            self.conn, '/redfish/v1/Test/Bios/BiosRegistry',
            redfish_version='1.0.2')
        registries = {'Test.1.0.2': attr_registry,
                      'Test.1.0.0': msg_registry}
        message_field = sushy_base.MessageListField('Foo')
        message_field.message_id = 'Test.1.0.0.TooBig'
        message_field.message_args = ['arg1', 10]
        message_field.severity = None
        message_field.resolution = None

        parsed_msg = message_registry.parse_message(registries, message_field)

        self.assertEqual('Try again', parsed_msg.resolution)
        self.assertEqual(res_cons.Severity.WARNING, parsed_msg.severity)
        self.assertEqual('Property\'s arg1 value cannot be greater than 10.',
                         parsed_msg.message)
