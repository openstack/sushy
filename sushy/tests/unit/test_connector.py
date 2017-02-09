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

from sushy import connector
from sushy.tests.unit import base


class ConnectorTestCase(base.TestCase):

    def setUp(self):
        super(ConnectorTestCase, self).setUp()
        self.conn = connector.Connector(
            'http://foo.bar:1234/redfish/v1', username='user',
            password='pass', verify=True)
        self.data = {'fake': 'data'}
        self.headers = {'X-Fake': 'header'}

    @mock.patch.object(connector.Connector, '_op', autospec=True)
    def test_get(self, mock__op):
        self.conn.get(path='fake/path', data=self.data, headers=self.headers)
        mock__op.assert_called_once_with(mock.ANY, 'GET', 'fake/path',
                                         self.data, self.headers)

    @mock.patch.object(connector.Connector, '_op', autospec=True)
    def test_post(self, mock__op):
        self.conn.post(path='fake/path', data=self.data, headers=self.headers)
        mock__op.assert_called_once_with(mock.ANY, 'POST', 'fake/path',
                                         self.data, self.headers)

    @mock.patch.object(connector.Connector, '_op', autospec=True)
    def test_patch(self, mock__op):
        self.conn.patch(path='fake/path', data=self.data, headers=self.headers)
        mock__op.assert_called_once_with(mock.ANY, 'PATCH', 'fake/path',
                                         self.data, self.headers)

    @mock.patch('sushy.connector.requests.Session', autospec=True)
    def test__op(self, mock_session):
        fake_session = mock.Mock()
        mock_session.return_value.__enter__.return_value = fake_session

        self.conn._op('GET', path='fake/path', data=self.data,
                      headers=self.headers)
        mock_session.assert_called_once_with()
        fake_session.request.assert_called_once_with(
            'GET', 'http://foo.bar:1234/redfish/v1/fake/path',
            data='{"fake": "data"}')
        expected_headers = {'Content-Type': 'application/json',
                            'X-Fake': 'header'}
        self.assertEqual(expected_headers, fake_session.headers)
