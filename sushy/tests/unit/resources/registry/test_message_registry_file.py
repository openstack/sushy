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

from sushy.resources.base import FieldData
from sushy.resources.registry import message_registry_file
from sushy.tests.unit import base


class MessageRegistryFileTestCase(base.TestCase):

    def setUp(self):
        super(MessageRegistryFileTestCase, self).setUp()
        self.conn = mock.Mock()
        with open('sushy/tests/unit/json_samples/'
                  'message_registry_file.json') as f:
            self.json_doc = json.load(f)

        self.conn.get.return_value.json.return_value = self.json_doc

        self.reg_file = message_registry_file.MessageRegistryFile(
            self.conn, '/redfish/v1/Registries/Test',
            redfish_version='1.0.2')

    def test__parse_attributes(self):
        self.reg_file._parse_attributes(self.json_doc)
        self.assertEqual('Test', self.reg_file.identity)
        self.assertEqual('Test Message Registry File', self.reg_file.name)
        self.assertEqual('Message Registry file for testing',
                         self.reg_file.description)
        self.assertEqual('en', self.reg_file.languages[0])
        self.assertEqual('Test.1.0', self.reg_file.registry)
        self.assertEqual('default', self.reg_file.location[0].language)
        self.assertEqual('/redfish/v1/Registries/Test/Test.1.0.json',
                         self.reg_file.location[0].uri)
        self.assertEqual('https://example.com/Registries/Test.1.0.json',
                         self.reg_file.location[0].publication_uri)
        self.assertEqual('/redfish/v1/Registries/Archive.zip',
                         self.reg_file.location[0].archive_uri)
        self.assertEqual('Test.1.0.json',
                         self.reg_file.location[0].archive_file)

    def test__parse_attributes_return(self):
        attributes = self.reg_file._parse_attributes(self.json_doc)

        # Test that various types are returned correctly
        self.assertEqual('Test Message Registry File', attributes.get('name'))
        self.assertEqual('Test', attributes.get('identity'))
        self.assertEqual(['en'], attributes.get('languages'))
        self.assertEqual('Test.1.0', attributes.get('registry'))

    @mock.patch('sushy.resources.registry.message_registry.MessageRegistry',
                autospec=True)
    @mock.patch('sushy.resources.base.JsonDataReader', autospec=True)
    def test_get_message_registry_uri(self, mock_reader, mock_msg_reg):
        mock_reader_rv = mock.Mock()
        mock_reader.return_value = mock_reader_rv
        mock_reader_rv.get_data.return_value = FieldData(200, {}, {
            "@odata.type": "#MessageRegistry.v1_1_1.MessageRegistry",
        })
        mock_msg_reg_rv = mock.Mock()
        mock_msg_reg.return_value = mock_msg_reg_rv

        registry = self.reg_file.get_message_registry('en', None)
        mock_msg_reg.assert_called_once_with(
            self.conn, path='/redfish/v1/Registries/Test/Test.1.0.json',
            reader=None, redfish_version=self.reg_file.redfish_version)
        self.assertEqual(mock_msg_reg_rv, registry)

    @mock.patch('sushy.resources.registry.message_registry.MessageRegistry',
                autospec=True)
    @mock.patch('sushy.resources.base.JsonArchiveReader', autospec=True)
    def test_get_message_registry_archive(self, mock_reader, mock_msg_reg):
        mock_reader_rv = mock.Mock()
        mock_reader.return_value = mock_reader_rv
        mock_msg_reg_rv = mock.Mock()
        mock_reader_rv.get_data.return_value = FieldData(200, {}, {
            "@odata.type": "#MessageRegistry.v1_1_1.MessageRegistry",
        })
        mock_msg_reg.return_value = mock_msg_reg_rv
        self.reg_file.location[0].uri = None

        registry = self.reg_file.get_message_registry('fr', None)
        mock_msg_reg.assert_called_once_with(
            self.conn, path='/redfish/v1/Registries/Archive.zip',
            redfish_version=self.reg_file.redfish_version,
            reader=mock_reader_rv)
        mock_reader.assert_called_once_with('Test.1.0.json')
        self.assertEqual(mock_msg_reg_rv, registry)

    @mock.patch('sushy.resources.registry.message_registry.MessageRegistry',
                autospec=True)
    @mock.patch('sushy.resources.base.JsonPublicFileReader', autospec=True)
    def test_get_message_registry_public(self, mock_reader, mock_msg_reg):
        public_connector = mock.Mock()
        mock_reader_rv = mock.Mock()
        mock_reader.return_value = mock_reader_rv
        mock_msg_reg_rv = mock.Mock()
        mock_reader_rv.get_data.return_value = FieldData(200, {}, {
            "@odata.type": "#MessageRegistry.v1_1_1.MessageRegistry",
        })
        mock_msg_reg.return_value = mock_msg_reg_rv
        self.reg_file.location[0].uri = None
        self.reg_file.location[0].archive_uri = None

        registry = self.reg_file.get_message_registry('en', public_connector)
        mock_msg_reg.assert_called_once_with(
            public_connector,
            path='https://example.com/Registries/Test.1.0.json',
            redfish_version=self.reg_file.redfish_version,
            reader=mock_reader_rv)
        self.assertEqual(mock_msg_reg_rv, registry)

    @mock.patch('sushy.resources.registry.message_registry_file.RegistryType',
                autospec=True)
    @mock.patch('sushy.resources.registry.message_registry_file.LOG',
                autospec=True)
    def test_get_message_registry_unknown_type(
            self, mock_log, mock_registry_type):
        mock_fishing_registry = mock_registry_type.return_value
        mock_fishing_registry._odata_type = 'FishingRegistry'

        registry = self.reg_file.get_message_registry('en', None)
        self.assertIsNone(registry)
        mock_log.debug.assert_called_with(
            'Ignoring unsupported flavor of registry %(registry)s',
            {'registry': 'FishingRegistry'})

    @mock.patch('sushy.resources.registry.message_registry.MessageRegistry',
                autospec=True)
    @mock.patch('sushy.resources.registry.message_registry_file.LOG',
                autospec=True)
    def test_get_message_registry_invalid(self, mock_log, mock_msg_reg):
        mock_msg_reg_rv = mock.Mock()
        mock_msg_reg.return_value = mock_msg_reg_rv
        self.reg_file.location[0].uri = None
        self.reg_file.location[0].archive_uri = None
        self.reg_file.location[0].publication_uri = None

        registry = self.reg_file.get_message_registry('en', None)
        mock_msg_reg.assert_not_called()
        self.assertIsNone(registry)
        mock_log.warning.assert_called_with(
            'No message registry found for %(language)s or default',
            {'language': 'en'})

    @mock.patch('sushy.resources.registry.message_registry.MessageRegistry',
                autospec=True)
    @mock.patch('sushy.resources.registry.message_registry_file.RegistryType',
                autospec=True)
    @mock.patch('sushy.resources.registry.message_registry_file.LOG',
                autospec=True)
    def test_get_message_registry_invalid_uri(
            self, mock_log, mock_msg_reg_type, mock_msg_reg):
        mock_msg_reg_rv = mock.Mock()
        mock_msg_reg.return_value = mock_msg_reg_rv
        self.reg_file.location[0].uri = {'extref': 'http://127.0.0.1/reg'}
        mock_msg_reg.side_effect = TypeError('Wrong URL type')
        mock_msg_reg_type.return_value._odata_type = mock.MagicMock(
            endswith=mock.MagicMock(return_value=True))

        registry = self.reg_file.get_message_registry('en', None)

        self.assertIsNone(registry)

        mock_msg_reg_type.assert_called_once_with(
            mock.ANY,
            path={'extref': 'http://127.0.0.1/reg'}, reader=None,
            redfish_version='1.0.2')

        mock_msg_reg.assert_called_once_with(
            mock.ANY,
            path={'extref': 'http://127.0.0.1/reg'}, reader=None,
            redfish_version='1.0.2')

        expected_calls = [
            mock.call(
                'Cannot load message registry from location %(location)s: '
                '%(error)s',
                {'location': {'extref': 'http://127.0.0.1/reg'},
                 'error': mock.ANY}),
            mock.call(
                'No message registry found for %(language)s or default',
                {'language': 'en'})
        ]

        mock_log.warning.assert_has_calls(expected_calls)

    @mock.patch('sushy.resources.registry.message_registry_file.RegistryType',
                autospec=True)
    def test_get_message_registry_non_default_lang(self, mock_registry_type):
        mock_fishing_registry = mock_registry_type.return_value
        mock_fishing_registry._odata_type = 'FishingRegistry'
        self.reg_file.location[0].language = 'en'
        registry = self.reg_file.get_message_registry('en', None)
        mock_registry_type.assert_called_once_with(
            self.conn, path='/redfish/v1/Registries/Test/Test.1.0.json',
            reader=None, redfish_version=self.reg_file.redfish_version)
        self.assertIsNone(registry)

    @mock.patch('sushy.resources.registry.message_registry_file.LOG',
                autospec=True)
    @mock.patch('sushy.resources.registry.message_registry_file.RegistryType',
                autospec=True)
    def test_get_message_registry_loading_type_fails(
            self, mock_reg_type, mock_log):
        mock_reg_type.side_effect = TypeError('Something wrong')

        registry = self.reg_file.get_message_registry('en', None)
        self.assertTrue(mock_reg_type.called)
        self.assertIsNone(registry)
        mock_log.warning.assert_any_call(
            'Cannot load message registry type from location '
            '%(location)s: %(error)s',
            {'location': '/redfish/v1/Registries/Test/Test.1.0.json',
             'error': mock.ANY})
        mock_log.warning.assert_called_with(
            'No message registry found for %(language)s or default',
            {'language': 'en'})

    @mock.patch('sushy.resources.registry.message_registry_file.RegistryType',
                autospec=True)
    def test_get_message_registry_strangely_cased_lang(
            self, mock_registry_type):
        mock_fishing_registry = mock_registry_type.return_value
        mock_fishing_registry._odata_type = 'FishingRegistry'
        self.reg_file.location[0].language = 'En'
        registry = self.reg_file.get_message_registry('en', None)
        mock_registry_type.assert_called_once_with(
            self.conn, path='/redfish/v1/Registries/Test/Test.1.0.json',
            reader=None, redfish_version=self.reg_file.redfish_version)
        self.assertIsNone(registry)

    @mock.patch('sushy.resources.registry.message_registry.MessageRegistry',
                autospec=True)
    @mock.patch('sushy.resources.registry.message_registry_file.LOG',
                autospec=True)
    def test_get_message_registry_missing_lang(self, mock_log, mock_msg_reg):
        mock_msg_reg_rv = mock.Mock()
        mock_msg_reg.return_value = mock_msg_reg_rv
        self.reg_file.location[0].language = 'cz'

        registry = self.reg_file.get_message_registry('en', None)
        mock_msg_reg.assert_not_called()
        self.assertIsNone(registry)
        mock_log.warning.assert_called_with(
            'No message registry found for %(language)s or default',
            {'language': 'en'})

    @mock.patch('sushy.resources.base.logging.warning',
                autospec=True)
    def test__parse_attributes_missing_registry(self, mock_log):
        self.json_doc.pop('Registry')
        self.reg_file._parse_attributes(self.json_doc)
        self.assertEqual('UNKNOWN.0.0', self.reg_file.registry)
        mock_log.assert_called_with(
            'Applying default "UNKNOWN.0.0" on required, but missing '
            'attribute "[\'Registry\']"')


class MessageRegistryFileCollectionTestCase(base.TestCase):

    def setUp(self):
        super(MessageRegistryFileCollectionTestCase, self).setUp()
        self.conn = mock.Mock()
        with open('sushy/tests/unit/json_samples/'
                  'message_registry_file_collection.json') as f:
            self.json_doc = json.load(f)

        self.conn.get.return_value.json.return_value = self.json_doc

        self.reg_file_col =\
            message_registry_file.MessageRegistryFileCollection(
                self.conn, '/redfish/v1/Registries',
                redfish_version='1.0.2')

    def test__parse_attributes(self):
        self.reg_file_col._parse_attributes(self.json_doc)
        self.assertEqual('1.0.2', self.reg_file_col.redfish_version)
        self.assertEqual('Message Registry Test Collection',
                         self.reg_file_col.name)
        self.assertEqual(('/redfish/v1/Registries/Test',),
                         self.reg_file_col.members_identities)
