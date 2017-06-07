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

import mock

from sushy import exceptions
from sushy.resources import base as resource_base
from sushy.tests.unit import base


class BaseResource(resource_base.ResourceBase):

    def _parse_attributes(self):
        pass


class ResourceBaseTestCase(base.TestCase):

    def setUp(self):
        super(ResourceBaseTestCase, self).setUp()
        self.conn = mock.Mock()
        self.base_resource = BaseResource(connector=self.conn, path='/Foo',
                                          redfish_version='1.0.2')
        # refresh() is called in the constructor
        self.conn.reset_mock()

    def test_refresh(self):
        self.base_resource.refresh()
        self.conn.get.assert_called_once_with(path='/Foo')


class TestResource(resource_base.ResourceBase):
    """A concrete Test Resource to test against"""

    def __init__(self, connector, identity, redfish_version=None):
        """Ctor of TestResouce

        :param connector: A Connector instance
        :param identity: The id of the Resource
        :param redfish_version: The version of RedFish. Used to construct
            the object according to schema of the given version.
        """
        super(TestResource, self).__init__(connector, 'Fakes/%s' % identity,
                                           redfish_version)
        self.identity = identity

    def _parse_attributes(self):
        pass


class TestResourceCollection(resource_base.ResourceCollectionBase):
    """A concrete Test Resource Collection to test against"""

    @property
    def _resource_type(self):
        return TestResource

    def __init__(self, connector, redfish_version=None):
        """Ctor of TestResourceCollection

        :param connector: A Connector instance
        :param redfish_version: The version of RedFish. Used to construct
            the object according to schema of the given version.
        """
        super(TestResourceCollection, self).__init__(connector, 'Fakes',
                                                     redfish_version)


class ResourceCollectionBaseTestCase(base.TestCase):

    def setUp(self):
        super(ResourceCollectionBaseTestCase, self).setUp()
        self.conn = mock.MagicMock()
        self.test_resource_collection = TestResourceCollection(
            self.conn, redfish_version='1.0.x')
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
            response=mock.Mock(status_code=404))
        # | WHEN & THEN |
        self.assertRaises(exceptions.ResourceNotFoundError,
                          self.test_resource_collection.get_member, '2')
        self.conn.get.assert_called_once_with(path='Fakes/2')

    def test_get_members(self):
        # | GIVEN |
        # setting some valid member paths
        member_ids = ('1', '2')
        self.test_resource_collection.members_identities = member_ids
        # | WHEN |
        result = self.test_resource_collection.get_members()
        # | THEN |
        self.assertIsInstance(result, list)
        for val in result:
            self.assertIsInstance(val, TestResource)
            self.assertTrue(val.identity in member_ids)
            self.assertEqual('1.0.x', val.redfish_version)


TEST_JSON = {
    'String': 'a string',
    'Integer': '42',
    'List': ['a string', 42],
    'Nested': {
        'String': 'another string',
        'Integer': 0,
        'Object': {
            'Field': 'field value'
        },
        'Mapped': 'raw'
    }
}


MAPPING = {
    'raw': 'real'
}


class NestedTestField(resource_base.CompositeField):
    string = resource_base.Field('String', required=True)
    integer = resource_base.Field('Integer', adapter=int)
    nested_field = resource_base.Field(['Object', 'Field'], required=True)
    mapped = resource_base.MappedField('Mapped', MAPPING)
    non_existing = resource_base.Field('NonExisting', default=3.14)


class ComplexResource(resource_base.ResourceBase):
    string = resource_base.Field('String', required=True)
    integer = resource_base.Field('Integer', adapter=int)
    nested = NestedTestField('Nested')
    non_existing_nested = NestedTestField('NonExistingNested')
    non_existing_mapped = resource_base.MappedField('NonExistingMapped',
                                                    MAPPING)


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
        self.assertIsNone(self.test_resource.non_existing_nested)
        self.assertIsNone(self.test_resource.non_existing_mapped)

    def test_missing_required(self):
        del self.json['String']
        self.assertRaisesRegex(exceptions.MissingAttributeError,
                               'String', self.test_resource.refresh)

    def test_missing_nested_required(self):
        del self.json['Nested']['String']
        self.assertRaisesRegex(exceptions.MissingAttributeError,
                               'Nested/String', self.test_resource.refresh)

    def test_missing_nested_required2(self):
        del self.json['Nested']['Object']['Field']
        self.assertRaisesRegex(exceptions.MissingAttributeError,
                               'Nested/Object/Field',
                               self.test_resource.refresh)

    def test_malformed_int(self):
        self.json['Integer'] = 'banana'
        self.assertRaisesRegex(
            exceptions.MalformedAttributeError,
            'attribute Integer is malformed.*invalid literal for int',
            self.test_resource.refresh)

    def test_malformed_nested_int(self):
        self.json['Nested']['Integer'] = 'banana'
        self.assertRaisesRegex(
            exceptions.MalformedAttributeError,
            'attribute Nested/Integer is malformed.*invalid literal for int',
            self.test_resource.refresh)

    def test_mapping_missing(self):
        self.json['Nested']['Mapped'] = 'banana'
        self.test_resource.refresh()

        self.assertIsNone(self.test_resource.nested.mapped)

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
