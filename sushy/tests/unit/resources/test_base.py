# Copyright 2017 Red Hat, Inc.
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

import copy
import enum
from http import client as http_client
import io
import json
from unittest import mock
import zipfile

from sushy import exceptions
from sushy.resources import base as resource_base
from sushy.tests.unit import base


BASE_RESOURCE_JSON = {
    "@odata.type": "#FauxResource.v1_0_0.FauxResource",
    "Id": "1111AAAA",
    "Name": "Faux Resource",
    "@odata.id": "/redfish/v1/FauxResource/1111AAAA",
    "Oem": {
        "Contoso": {
            "@odata.type": "http://contoso.com/schemas/extensions.v1_2_1#contoso.AnvilTypes1",  # noqa
            "slogan": "Contoso never fail",
            "disclaimer": "* Most of the time"
        },
        "EID_412_ASB_123": {
            "@odata.type": "http://AnotherStandardsBody/schemas.v1_0_1#styleInfoExt",  # noqa
            "Style": "Executive"
        }
    },
    "Links": {
        "Oem": {
            "Contoso": {
                "@odata.type": "http://contoso.com/schemas/extensions.v1_2_1#contoso.AnvilTypes1",  # noqa
                "slogan": "Contoso never fail",
                "disclaimer": "* Most of the time"
            },
            "EID_420_ASB_345": {
                "@odata.type": "http://AnotherStandardsBody/schemas.v1_0_1#styleInfoExt",  # noqa
                "Style": "Executive"
            }
        }
    }

}


class BaseResource(resource_base.ResourceBase):

    def _parse_attributes(self, json_doc):
        pass


class BaseResource2(resource_base.ResourceBase):
    pass


class ResourceBaseTestCase(base.TestCase):

    def setUp(self):
        super(ResourceBaseTestCase, self).setUp()
        self.conn = mock.Mock()
        self.conn.get.return_value.json.return_value = (
            copy.deepcopy(BASE_RESOURCE_JSON))
        self.base_resource = BaseResource(connector=self.conn, path='/Foo',
                                          redfish_version='1.0.2')
        self.assertFalse(self.base_resource._is_stale)
        self.base_resource2 = BaseResource2(connector=self.conn, path='/Foo',
                                            redfish_version='1.0.2')
        # refresh() is called in the constructor
        self.conn.reset_mock()

    def test_refresh_no_force(self):
        self.base_resource.refresh(force=False)
        self.conn.get.assert_not_called()

    def test_refresh_force(self):
        self.base_resource.refresh()
        self.conn.get.assert_called_once_with(path='/Foo')

    def test_invalidate(self):
        self.base_resource.invalidate()
        self.conn.get.assert_not_called()

        self.base_resource.refresh(force=False)
        self.conn.get.assert_called_once_with(path='/Foo')

    def test_invalidate_force_refresh(self):
        self.base_resource.invalidate(force_refresh=True)
        self.conn.get.assert_called_once_with(path='/Foo')

    def test_refresh_archive(self):
        mock_response = mock.Mock(
            headers={'content-type': 'application/zip'})
        with open('sushy/tests/unit/json_samples/TestRegistry.zip', 'rb') as f:
            mock_response.content = f.read()
        self.conn.get.return_value = mock_response

        resource = BaseResource(connector=self.conn,
                                path='/Foo',
                                redfish_version='1.0.2',
                                reader=resource_base.
                                JsonArchiveReader('Test.2.0.json'))

        self.assertIsNotNone(resource._json)
        self.assertEqual('Test.2.0.0', resource._json['Id'])

    @mock.patch.object(resource_base, 'LOG', autospec=True)
    def test_refresh_archive_not_implemented(self, mock_log):
        mock_response = mock.Mock(
            headers={'content-type': 'application/gzip'})
        self.conn.get.return_value = mock_response
        BaseResource(connector=self.conn,
                     path='/Foo',
                     redfish_version='1.0.2',
                     reader=resource_base.JsonArchiveReader('Test.2.0.json'))
        mock_log.error.assert_called_once()

    @mock.patch.object(io, 'BytesIO', autospec=True)
    def test_refresh_archive_badzip_error(self, mock_io):
        mock_response = mock.Mock(
            headers={'content-type': 'application/zip'})
        mock_io.side_effect = zipfile.BadZipfile('Something wrong')
        self.conn.get.return_value = mock_response

        self.assertRaises(exceptions.SushyError,
                          BaseResource, connector=self.conn,
                          path='/Foo',
                          redfish_version='1.0.2',
                          reader=resource_base.
                          JsonArchiveReader('Test.2.0.json'))

    def test_init_default_reader(self):
        resource_a = BaseResource(connector=self.conn)
        resource_b = BaseResource(connector=self.conn)

        self.assertIsInstance(resource_a._reader, resource_base.JsonDataReader)
        self.assertIsInstance(resource_b._reader, resource_base.JsonDataReader)

        self.assertIsNot(resource_a._reader, resource_b._reader)

    def test__parse_attributes(self):
        expected_oem_vendors = ['Contoso', 'EID_412_ASB_123',
                                'EID_420_ASB_345']
        actual_oem_vendors = sorted(self.base_resource2.oem_vendors)
        self.assertEqual(expected_oem_vendors, actual_oem_vendors)
        self.assertEqual('base_resource2', self.base_resource2.resource_name)

    def test_refresh_local(self):
        resource = BaseResource(None, 'json_samples/message_registry.json',
                                reader=resource_base.
                                JsonPackagedFileReader('sushy.tests.unit'))
        self.assertIsNotNone(resource._json)
        self.assertEqual('Test.1.1.1', resource._json['Id'])

    def test_refresh_public(self):
        mock_connector = mock.Mock()
        with open('sushy/tests/unit/json_samples/message_registry.json') as f:
            mock_connector.get.return_value.json.return_value = json.load(f)
        resource = BaseResource(mock_connector, 'https://example.com/'
                                'message_registry.json',
                                reader=resource_base.JsonPublicFileReader())
        mock_connector.get.assert_called_once_with('https://example.com/'
                                                   'message_registry.json')
        self.assertIsNotNone(resource._json)
        self.assertEqual('Test.1.1.1', resource._json['Id'])


class TestResource(resource_base.ResourceBase):
    """A concrete Test Resource to test against"""

    def __init__(self, connector, identity, redfish_version=None,
                 registries=None, root=None):
        """Ctor of TestResource

        :param connector: A Connector instance
        :param identity: The id of the Resource
        :param redfish_version: The version of RedFish. Used to construct
            the object according to schema of the given version.
        :param registries: Dict of Redfish Message Registry objects to be
            used in any resource that needs registries to parse messages.
        """
        super(TestResource, self).__init__(connector, 'Fakes/%s' % identity,
                                           redfish_version, registries, root)
        self.identity = identity

    def _parse_attributes(self, json_doc):
        pass


class TestResourceCollection(resource_base.ResourceCollectionBase):
    """A concrete Test Resource Collection to test against"""

    @property
    def _resource_type(self):
        return TestResource

    def __init__(self, connector, redfish_version=None, registries=None,
                 root=None):
        """Ctor of TestResourceCollection

        :param connector: A Connector instance
        :param redfish_version: The version of RedFish. Used to construct
            the object according to schema of the given version.
        :param registries: Dict of Redfish Message Registry objects to be
            used in any resource that needs registries to parse messages.
        """
        super(TestResourceCollection, self).__init__(
            connector, 'Fakes', redfish_version, registries, root)


class ResourceCollectionBaseTestCase(base.TestCase):

    def setUp(self):
        super(ResourceCollectionBaseTestCase, self).setUp()
        self.conn = mock.MagicMock()
        self.test_resource_collection = TestResourceCollection(
            self.conn, redfish_version='1.0.x', registries=None)
        self.conn.reset_mock()

    def test_get_member(self):
        # | GIVEN |
        # setting a valid member identity
        self.test_resource_collection.members_identities = ('1',)
        # | WHEN |
        result = self.test_resource_collection.get_member('1')
        # | THEN |
        self.assertIsInstance(result, TestResource)
        self.assertEqual('1', result.identity)
        self.assertEqual('1.0.x', result.redfish_version)

    def test_get_member_for_invalid_id(self):
        # | GIVEN |
        # setting a valid member identity
        self.test_resource_collection.members_identities = ('1',)
        self.conn.get.side_effect = exceptions.ResourceNotFoundError(
            method='GET', url='http://foo.bar:8000/redfish/v1/Fakes/2',
            response=mock.MagicMock(status_code=http_client.NOT_FOUND))
        # | WHEN & THEN |
        self.assertRaises(exceptions.ResourceNotFoundError,
                          self.test_resource_collection.get_member, '2')
        self.conn.get.assert_called_once_with(path='Fakes/2')

    def _validate_get_members_result(self, member_ids):
        # | GIVEN |
        # setting some valid member paths
        self.test_resource_collection.members_identities = member_ids
        # | WHEN |
        result = self.test_resource_collection.get_members()
        # | THEN |
        self.assertIsInstance(result, list)
        for val in result:
            self.assertIsInstance(val, TestResource)
            self.assertIn(val.identity, member_ids)
            self.assertEqual('1.0.x', val.redfish_version)
            self.assertFalse(val._is_stale)

        return result

    def test_get_members(self):
        self._validate_get_members_result(('1', '2'))

    def test_get_members_on_refresh(self):
        all_members = self._validate_get_members_result(('1', '2'))

        # Call resource invalidate
        self.test_resource_collection.invalidate()
        self.assertTrue(self.test_resource_collection._is_stale)
        #  Now invoke refresh action on resource. This can be viewed as
        # "light refresh" which involves only the resource's fresh retrieval
        # and not its nested resources (these are only marked as stale).
        self.test_resource_collection.refresh(force=False)
        # resource itself is fresh
        self.assertFalse(self.test_resource_collection._is_stale)
        # members are marked as stale
        for m in all_members:
            self.assertTrue(m._is_stale)

        self._validate_get_members_result(('1', '2'))
        # members are also now freshly retrieved
        for m in all_members:
            self.assertFalse(m._is_stale)

        # Again invalidate and do a forced refresh on resource
        self.test_resource_collection.invalidate(force_refresh=True)
        # Now, even the members are also freshly retrieved. This can be viewed
        # as "cascading refresh" which involves not only the resource's fresh
        # retrieval but also its nested resources.
        for m in all_members:
            self.assertFalse(m._is_stale)

    def test_get_members_caching(self):
        result = self._validate_get_members_result(('1', '2'))
        self.assertIs(result, self.test_resource_collection.get_members())


TEST_JSON = {
    'String': 'a string',
    'Integer': '42',
    'MappedList': ['raw1', 'raw2', 'raw'],
    'Nested': {
        'String': 'another string',
        'Integer': 0,
        'Object': {
            'Field': 'field value'
        },
        'Mapped': 'raw'
    },
    'ListField': [
        {
            'String': 'a third string',
            'Integer': 1
        },
        {
            'String': 'a fourth string',
            'Integer': 2
        }
    ],
    'Dictionary': {
        'key1': {'property_a': 'value1', 'property_b': 'value2'},
        'key2': {'property_a': 'value3', 'property_b': 'value4'}
    },
    'Enum': 'PROTOCOL_FIELD_2',
    'EnumList': ['PROTOCOL_FIELD_2', 'PROTOCOL_FIELD_3'],
}


MAPPING = {
    'raw': 'real',
    'raw1': 'real1',
    'raw2': 'real2'
}


class EnumMapping(enum.Enum):

    FIELD1 = "PROTOCOL_FIELD_1"
    FIELD2 = "PROTOCOL_FIELD_2"
    FIELD3 = "PROTOCOL_FIELD_3"


class NestedTestField(resource_base.CompositeField):
    string = resource_base.Field('String', required=True)
    integer = resource_base.Field('Integer', adapter=int)
    nested_field = resource_base.Field(['Object', 'Field'], required=True)
    mapped = resource_base.MappedField('Mapped', MAPPING)
    non_existing = resource_base.Field('NonExisting', default=3.14)


class TestListField(resource_base.ListField):
    string = resource_base.Field('String', required=True)
    integer = resource_base.Field('Integer', adapter=int)


class TestDictionaryField(resource_base.DictionaryField):
    property_a = resource_base.Field('property_a')
    property_b = resource_base.Field('property_b')


class ComplexResource(resource_base.ResourceBase):
    string = resource_base.Field('String', required=True)
    integer = resource_base.Field('Integer', adapter=int)
    nested = NestedTestField('Nested')
    mapped_list = resource_base.MappedListField('MappedList', MAPPING)
    field_list = TestListField('ListField')
    dictionary = TestDictionaryField('Dictionary')
    non_existing_nested = NestedTestField('NonExistingNested')
    non_existing_mapped = resource_base.MappedField('NonExistingMapped',
                                                    MAPPING)
    enum_mapped = resource_base.MappedField('Enum', EnumMapping)
    enum_mapped_list = resource_base.MappedListField('EnumList', EnumMapping)
    non_existing_enum_mapped = resource_base.MappedField('NonExistingEnum',
                                                         EnumMapping)


class FieldTestCase(base.TestCase):
    def setUp(self):
        super(FieldTestCase, self).setUp()
        self.conn = mock.Mock()
        self.json = copy.deepcopy(TEST_JSON)
        self.conn.get.return_value.json.return_value = self.json
        self.test_resource = ComplexResource(self.conn,
                                             redfish_version='1.0.x')

    def test_ok(self):
        self.assertEqual('a string', self.test_resource.string)
        self.assertEqual(42, self.test_resource.integer)
        self.assertEqual('another string', self.test_resource.nested.string)
        self.assertEqual(0, self.test_resource.nested.integer)
        self.assertEqual('field value', self.test_resource.nested.nested_field)
        self.assertEqual('real', self.test_resource.nested.mapped)
        self.assertEqual(3.14, self.test_resource.nested.non_existing)
        self.assertEqual(['real1', 'real2', 'real'],
                         self.test_resource.mapped_list)
        self.assertEqual('a third string',
                         self.test_resource.field_list[0].string)
        self.assertEqual(2, self.test_resource.field_list[1].integer)
        self.assertEqual(2, len(self.test_resource.dictionary))
        self.assertEqual('value1',
                         self.test_resource.dictionary['key1'].property_a)
        self.assertEqual('value4',
                         self.test_resource.dictionary['key2'].property_b)
        self.assertIsNone(self.test_resource.non_existing_nested)
        self.assertIsNone(self.test_resource.non_existing_mapped)
        self.assertEqual(EnumMapping.FIELD2, self.test_resource.enum_mapped)
        self.assertEqual([EnumMapping.FIELD2, EnumMapping.FIELD3],
                         self.test_resource.enum_mapped_list)
        self.assertIsNone(self.test_resource.non_existing_enum_mapped)

    def test_missing_required(self):
        del self.json['String']
        self.assertRaisesRegex(
            exceptions.MissingAttributeError,
            'String', self.test_resource.refresh, force=True)

    def test_missing_nested_required(self):
        del self.json['Nested']['String']
        self.assertRaisesRegex(
            exceptions.MissingAttributeError,
            'Nested/String', self.test_resource.refresh, force=True)

    def test_missing_nested_required2(self):
        del self.json['Nested']['Object']['Field']
        self.assertRaisesRegex(exceptions.MissingAttributeError,
                               'Nested/Object/Field',
                               self.test_resource.refresh, force=True)

    def test_malformed_int(self):
        self.json['Integer'] = 'banana'
        self.assertRaisesRegex(
            exceptions.MalformedAttributeError,
            'attribute Integer is malformed.*invalid literal for int',
            self.test_resource.refresh, force=True)

    def test_malformed_nested_int(self):
        self.json['Nested']['Integer'] = 'banana'
        self.assertRaisesRegex(
            exceptions.MalformedAttributeError,
            'attribute Nested/Integer is malformed.*invalid literal for int',
            self.test_resource.refresh, force=True)

    def test_mapping_missing(self):
        self.json['Nested']['Mapped'] = 'banana'
        self.json['Enum'] = 'banana'
        self.test_resource.refresh(force=True)

        self.assertIsNone(self.test_resource.nested.mapped)
        self.assertIsNone(self.test_resource.enum_mapped)

    def test_composite_field_as_mapping(self):
        field = self.test_resource.nested
        keys = {'string', 'integer', 'nested_field', 'mapped', 'non_existing'}
        values = {'another string', 0, 'field value', 'real', 3.14}

        self.assertEqual(keys, set(iter(field)))
        self.assertEqual(keys, set(field.keys()))
        self.assertEqual(values, set(field.values()))
        self.assertEqual(3.14, field['non_existing'])
        self.assertEqual(3.14, field.get('non_existing'))
        self.assertIsNone(field.get('foobar'))
        # Check KeyError from undefined fields
        self.assertRaisesRegex(KeyError, 'foobar', lambda: field['foobar'])
        # Regular attributes cannot be accessed via mapping
        self.assertRaisesRegex(KeyError, '_load', lambda: field['_load'])
        self.assertRaisesRegex(KeyError, '__init__', lambda: field['__init__'])

    def test_invalid_mapping_definiton(self):
        self.assertRaises(TypeError, resource_base.MappedField, 'Field', 42)
        self.assertRaises(TypeError, resource_base.MappedListField,
                          'Field', 42)


class PartialKeyResource(resource_base.ResourceBase):
    string = resource_base.Field(
        lambda key, **context: key.startswith('Str'))
    integer = resource_base.Field(
        lambda key, value, **context: key == 'Integer' and int(value) < 42)


class FieldPartialKeyTestCase(base.TestCase):
    def setUp(self):
        super(FieldPartialKeyTestCase, self).setUp()
        self.conn = mock.Mock()
        self.json = copy.deepcopy(TEST_JSON)
        self.conn.get.return_value.json.return_value = self.json
        self.test_resource = PartialKeyResource(
            self.conn, redfish_version='1.0.x')

    def test_ok(self):
        self.assertEqual('a string', self.test_resource.string)
        self.assertIsNone(self.test_resource.integer)
