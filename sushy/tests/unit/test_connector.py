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

import json

import mock
import requests

from sushy import connector
from sushy import exceptions
from sushy.tests.unit import base


class ConnectorMethodsTestCase(base.TestCase):

    def setUp(self):
        super(ConnectorMethodsTestCase, self).setUp()
        self.conn = connector.Connector(
            'http://foo.bar:1234', username='user',
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


class ConnectorOpTestCase(base.TestCase):

    def setUp(self):
        super(ConnectorOpTestCase, self).setUp()
        self.conn = connector.Connector(
            'http://foo.bar:1234', username='user',
            password='pass', verify=True)
        self.data = {'fake': 'data'}
        self.headers = {'X-Fake': 'header'}
        self.session = mock.Mock(spec=requests.Session)
        self.conn._session = self.session
        self.request = self.session.request
        self.request.return_value.status_code = 200

    def test_ok_get(self):
        expected_headers = self.headers.copy()

        self.conn._op('GET', path='fake/path', headers=self.headers)
        self.request.assert_called_once_with(
            'GET', 'http://foo.bar:1234/fake/path',
            data=None, headers=expected_headers)

    def test_ok_post(self):
        expected_headers = self.headers.copy()
        expected_headers['Content-Type'] = 'application/json'

        self.conn._op('POST', path='fake/path', data=self.data,
                      headers=self.headers)
        self.request.assert_called_once_with(
            'POST', 'http://foo.bar:1234/fake/path',
            data=json.dumps(self.data), headers=expected_headers)

    def test_connection_error(self):
        self.request.side_effect = requests.exceptions.ConnectionError
        self.assertRaises(exceptions.ConnectionError, self.conn._op, 'GET')

    def test_unknown_http_error(self):
        self.request.return_value.status_code = 409
        self.request.return_value.json.side_effect = ValueError('no json')

        with self.assertRaisesRegex(exceptions.HTTPError,
                                    'unknown error') as cm:
            self.conn._op('GET', 'http://foo.bar')
        exc = cm.exception
        self.assertEqual(409, exc.status_code)
        self.assertIsNone(exc.body)
        self.assertIsNone(exc.detail)

    def test_known_http_error(self):
        self.request.return_value.status_code = 400
        with open('sushy/tests/unit/json_samples/error.json', 'r') as f:
            self.request.return_value.json.return_value = json.load(f)

        with self.assertRaisesRegex(exceptions.BadRequestError,
                                    'A general error has occurred') as cm:
            self.conn._op('GET', 'http://foo.bar')
        exc = cm.exception
        self.assertEqual(400, exc.status_code)
        self.assertIsNotNone(exc.body)
        self.assertIn('A general error has occurred', exc.detail)

    def test_not_found_error(self):
        self.request.return_value.status_code = 404
        self.request.return_value.json.side_effect = ValueError('no json')

        with self.assertRaisesRegex(exceptions.ResourceNotFoundError,
                                    'Resource http://foo.bar not found') as cm:
            self.conn._op('GET', 'http://foo.bar')
        exc = cm.exception
        self.assertEqual(404, exc.status_code)

    def test_server_error(self):
        self.request.return_value.status_code = 500
        self.request.return_value.json.side_effect = ValueError('no json')

        with self.assertRaisesRegex(exceptions.ServerSideError,
                                    'unknown error') as cm:
            self.conn._op('GET', 'http://foo.bar')
        exc = cm.exception
        self.assertEqual(500, exc.status_code)

    def test_access_error(self):
        self.request.return_value.status_code = 403
        self.request.return_value.json.side_effect = ValueError('no json')

        with self.assertRaisesRegex(exceptions.AccessError,
                                    'unknown error') as cm:
            self.conn._op('GET', 'http://foo.bar')
        exc = cm.exception
        self.assertEqual(403, exc.status_code)
