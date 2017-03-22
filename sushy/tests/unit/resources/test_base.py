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

import mock

from sushy import exceptions
from sushy.resources import base as resource_base
from sushy.tests.unit import base


class BaseResouce(resource_base.ResourceBase):

    def _parse_attributes(self):
        pass


class ResourceBaseTestCase(base.TestCase):

    def setUp(self):
        super(ResourceBaseTestCase, self).setUp()
        self.conn = mock.Mock()
        self.base_resource = BaseResouce(connector=self.conn, path='/Foo',
                                         redfish_version='1.0.2')
        # refresh() is called in the constructor
        self.conn.reset_mock()

    def test_refresh(self):
        self.base_resource.refresh()
        self.conn.get.assert_called_once_with(path='/Foo')

    def test_refresh_http_error_reraised(self):
        self.conn.get.side_effect = exceptions.HTTPError(
            method='GET', url='http://foo.bar:8000/redfish/v1', error='boom',
            status_code=404)
        self.assertRaises(exceptions.ResourceNotFoundError,
                          self.base_resource.refresh)
        self.conn.get.assert_called_once_with(path='/Foo')

    def test_refresh_resource_not_found(self):
        self.conn.get.side_effect = exceptions.HTTPError(
            method='GET', url='http://foo.bar:8000/redfish/v1', error='boom',
            status_code=400)
        self.assertRaises(exceptions.HTTPError, self.base_resource.refresh)
        self.conn.get.assert_called_once_with(path='/Foo')


class TestResouce(resource_base.ResourceBase):
    """A concrete Test Resource to test against"""

    def __init__(self, connector, identity, redfish_version=None):
        """Ctor of TestResouce

        :param connector: A Connector instance
        :param identity: The id of the Resource
        :param redfish_version: The version of RedFish. Used to construct
            the object according to schema of the given version.
        """
        super(TestResouce, self).__init__(connector, 'Fakes/%s' % identity,
                                          redfish_version)
        self.identity = identity

    def _parse_attributes(self):
        pass


class TestResouceCollection(resource_base.ResourceCollectionBase):
    """A concrete Test Resource Collection to test against"""

    @property
    def _resource_type(self):
        return TestResouce

    def __init__(self, connector, redfish_version=None):
        """Ctor of TestResourceCollection

        :param connector: A Connector instance
        :param redfish_version: The version of RedFish. Used to construct
            the object according to schema of the given version.
        """
        super(TestResouceCollection, self).__init__(connector, 'Fakes',
                                                    redfish_version)


class ResourceCollectionBaseTestCase(base.TestCase):

    def setUp(self):
        super(ResourceCollectionBaseTestCase, self).setUp()
        self.conn = mock.MagicMock()
        self.test_resource_collection = TestResouceCollection(
            self.conn, redfish_version='1.0.x')
        self.conn.reset_mock()

    def test_get_member(self):
        # | GIVEN |
        # setting a valid member identity
        self.test_resource_collection.members_identities = ('1',)
        # | WHEN |
        result = self.test_resource_collection.get_member('1')
        # | THEN |
        self.assertTrue(isinstance(result, TestResouce))
        self.assertEqual('1', result.identity)
        self.assertEqual('1.0.x', result.redfish_version)

    def test_get_member_for_invalid_id(self):
        # | GIVEN |
        # setting a valid member identity
        self.test_resource_collection.members_identities = ('1',)
        self.conn.get.side_effect = exceptions.HTTPError(
            method='GET', url='http://foo.bar:8000/redfish/v1/Fakes/2',
            error='boom', status_code=404)
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
        self.assertTrue(isinstance(result, list))
        for val in result:
            self.assertTrue(isinstance(val, TestResouce))
            self.assertTrue(val.identity in member_ids)
            self.assertEqual('1.0.x', val.redfish_version)
