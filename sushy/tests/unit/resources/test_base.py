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
        self.base_resource = BaseResouce(connector=self.conn, path='/Foo')
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
