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

from http import client as http_client
import json
from unittest import mock

import requests

from sushy import auth as sushy_auth
from sushy import connector
from sushy import exceptions
from sushy.tests.unit import base


class ConnectorMethodsTestCase(base.TestCase):

    @mock.patch.object(sushy_auth, 'SessionOrBasicAuth', autospec=True)
    def setUp(self, mock_auth):
        mock_auth.get_session_key.return_value = None
        super(ConnectorMethodsTestCase, self).setUp()
        self.conn = connector.Connector(
            'http://foo.bar:1234', verify=True)
        self.conn._auth = mock_auth
        self.data = {'fake': 'data'}
        self.headers = {'X-Fake': 'header'}

    def test_init_with_credentials(self):
        conn = connector.Connector('http://foo.bar:1234',
                                   username='admin',
                                   password='password')
        self.assertEqual(conn._session.auth, ('admin', 'password'))

    def test_init_with_callback(self):
        def response_callback(response):
            return

        conn = connector.Connector('http://foo.bar:1234',
                                   username='admin',
                                   password='password',
                                   response_callback=response_callback)
        self.assertIs(conn._response_callback, response_callback)

    @mock.patch.object(connector.Connector, '_op', autospec=True)
    def test_get(self, mock__op):
        self.conn.get(path='fake/path', data=self.data.copy(),
                      headers=self.headers.copy())
        mock__op.assert_called_once_with(mock.ANY, 'GET', 'fake/path',
                                         data=self.data, headers=self.headers,
                                         blocking=False, timeout=60)

    @mock.patch.object(connector.Connector, '_op', autospec=True)
    def test_get_blocking(self, mock__op):
        self.conn.get(path='fake/path', data=self.data.copy(),
                      headers=self.headers.copy(), blocking=True)
        mock__op.assert_called_once_with(mock.ANY, 'GET', 'fake/path',
                                         data=self.data, headers=self.headers,
                                         blocking=True, timeout=60)

    @mock.patch.object(connector.Connector, '_op', autospec=True)
    def test_post(self, mock__op):
        self.conn.post(path='fake/path', data=self.data.copy(),
                       headers=self.headers.copy())
        mock__op.assert_called_once_with(mock.ANY, 'POST', 'fake/path',
                                         data=self.data, headers=self.headers,
                                         blocking=False, timeout=60)

    @mock.patch.object(connector.Connector, '_op', autospec=True)
    def test_post_blocking(self, mock__op):
        self.conn.post(path='fake/path', data=self.data.copy(),
                       headers=self.headers.copy(), blocking=True, timeout=120)
        mock__op.assert_called_once_with(mock.ANY, 'POST', 'fake/path',
                                         data=self.data, headers=self.headers,
                                         blocking=True, timeout=120)

    @mock.patch.object(connector.Connector, '_op', autospec=True)
    def test_patch(self, mock__op):
        self.conn.patch(path='fake/path', data=self.data.copy(),
                        headers=self.headers.copy())
        mock__op.assert_called_once_with(mock.ANY, 'PATCH', 'fake/path',
                                         data=self.data, headers=self.headers,
                                         blocking=False, timeout=60)

    @mock.patch.object(connector.Connector, '_op', autospec=True)
    def test_patch_blocking(self, mock__op):
        self.conn.patch(path='fake/path', data=self.data.copy(),
                        headers=self.headers.copy(), blocking=True)
        mock__op.assert_called_once_with(mock.ANY, 'PATCH', 'fake/path',
                                         data=self.data, headers=self.headers,
                                         blocking=True, timeout=60)

    @mock.patch.object(connector.Connector, '_op', autospec=True)
    def test_put(self, mock__op):
        self.conn.put(path='fake/path', data=self.data.copy(),
                      headers=self.headers.copy())
        mock__op.assert_called_once_with(mock.ANY, 'PUT', 'fake/path',
                                         data=self.data, headers=self.headers,
                                         blocking=False, timeout=60)

    @mock.patch.object(connector.Connector, '_op', autospec=True)
    def test_put_blocking(self, mock__op):
        self.conn.put(path='fake/path', data=self.data.copy(),
                      headers=self.headers.copy(), blocking=True)
        mock__op.assert_called_once_with(mock.ANY, 'PUT', 'fake/path',
                                         data=self.data, headers=self.headers,
                                         blocking=True, timeout=60)

    @mock.patch.object(connector.Connector, '_op', autospec=True)
    def test_delete(self, mock__op):
        self.conn.delete(path='fake/path', data=self.data.copy(),
                         headers=self.headers.copy())
        mock__op.assert_called_once_with(mock.ANY, 'DELETE', 'fake/path',
                                         data=self.data, headers=self.headers,
                                         blocking=False, timeout=60)

    @mock.patch.object(connector.Connector, '_op', autospec=True)
    def test_delete_blocking(self, mock__op):
        self.conn.delete(path='fake/path', data=self.data.copy(),
                         headers=self.headers.copy(), blocking=True)
        mock__op.assert_called_once_with(mock.ANY, 'DELETE', 'fake/path',
                                         data=self.data, headers=self.headers,
                                         blocking=True, timeout=60)

    def test_set_auth(self):
        mock_auth = mock.MagicMock()
        self.conn.set_auth(mock_auth)
        self.assertEqual(mock_auth, self.conn._auth)

    def test_set_http_basic_auth(self):
        self.conn.set_http_basic_auth('foo', 'secret')
        self.assertEqual(('foo', 'secret'), self.conn._session.auth)

    def test_set_http_session_auth(self):
        self.conn.set_http_session_auth('hash-token')
        self.assertTrue('X-Auth-Token' in self.conn._session.headers)
        self.assertEqual(
            'hash-token', self.conn._session.headers['X-Auth-Token'])

    def test_close(self):
        session = mock.Mock(spec=requests.Session)
        self.conn._session = session
        self.conn.close()
        session.close.assert_called_once_with()


class ConnectorOpTestCase(base.TestCase):

    @mock.patch.object(sushy_auth, 'SessionOrBasicAuth', autospec=True)
    def setUp(self, mock_auth):
        mock_auth.get_session_key.return_value = None
        mock_auth._session_key = None
        self.auth = mock_auth
        super(ConnectorOpTestCase, self).setUp()
        self.conn = connector.Connector(
            'http://foo.bar:1234', verify=True)
        self.conn._auth = mock_auth
        self.data = {'fake': 'data'}
        self.headers = {'X-Fake': 'header'}
        self.session = mock.Mock(spec=requests.Session)
        self.conn._session = self.session
        self.request = self.session.request
        self.request.return_value.status_code = http_client.OK

    def test_ok_get(self):
        self.conn._op('GET', path='fake/path', headers=self.headers)
        self.request.assert_called_once_with(
            'GET', 'http://foo.bar:1234/fake/path',
            headers=self.headers, json=None)

    def test_response_callback(self):
        mock_response_callback = mock.MagicMock()
        self.conn._response_callback = mock_response_callback

        self.conn._op('GET', path='fake/path', headers=self.headers)
        self.assertEqual(1, mock_response_callback.call_count)

    def test_ok_get_url_redirect_false(self):
        self.conn._op('GET', path='fake/path', headers=self.headers,
                      allow_redirects=False)
        self.request.assert_called_once_with(
            'GET', 'http://foo.bar:1234/fake/path',
            headers=self.headers, json=None, allow_redirects=False)

    def test_ok_post(self):
        self.conn._op('POST', path='fake/path', data=self.data.copy(),
                      headers=self.headers)
        self.request.assert_called_once_with(
            'POST', 'http://foo.bar:1234/fake/path',
            json=self.data, headers=self.headers)

    def test_ok_put(self):
        self.conn._op('PUT', path='fake/path', data=self.data.copy(),
                      headers=self.headers)
        self.request.assert_called_once_with(
            'PUT', 'http://foo.bar:1234/fake/path',
            json=self.data, headers=self.headers)

    def test_ok_delete(self):
        expected_headers = self.headers.copy()
        expected_headers['OData-Version'] = '4.0'
        self.conn._op('DELETE', path='fake/path', headers=self.headers.copy())
        self.request.assert_called_once_with(
            'DELETE', 'http://foo.bar:1234/fake/path',
            headers=expected_headers, json=None)

    def test_ok_post_with_session(self):
        self.conn._session.headers = {}
        self.conn._session.headers['X-Auth-Token'] = 'asdf1234'
        expected_headers = self.headers.copy()
        expected_headers['OData-Version'] = '4.0'
        self.conn._op('POST', path='fake/path', headers=self.headers,
                      data=self.data)
        self.request.assert_called_once_with(
            'POST', 'http://foo.bar:1234/fake/path',
            json=self.data, headers=expected_headers)
        self.assertEqual(self.conn._session.headers,
                         {'X-Auth-Token': 'asdf1234'})

    def test_odata_version_header_redfish(self):
        path = '/redfish/v1/path'
        headers = dict(self.headers)
        expected_headers = dict(self.headers)
        expected_headers['OData-Version'] = '4.0'
        self.request.reset_mock()
        self.conn._op('GET', path=path, headers=headers)
        self.request.assert_called_once_with(
            'GET', 'http://foo.bar:1234' + path,
            headers=expected_headers, json=None)

    def test_odata_version_header_redfish_no_headers(self):
        path = '/redfish/v1/bar'
        expected_headers = {'OData-Version': '4.0'}
        self.conn._op('GET', path=path)
        self.request.assert_called_once_with(
            'GET', 'http://foo.bar:1234' + path,
            headers=expected_headers, json=None)

    def test_odata_version_header_redfish_existing_header(self):
        path = '/redfish/v1/foo'
        headers = {'OData-Version': '3.0'}
        expected_headers = dict(headers)
        self.conn._op('GET', path=path, headers=headers)
        self.request.assert_called_once_with(
            'GET', 'http://foo.bar:1234' + path,
            headers=expected_headers, json=None)

    def test_timed_out_session_unable_to_create_session(self):
        self.conn._auth.can_refresh_session.return_value = False
        self.conn._session = self.session
        self.request = self.session.request
        self.request.return_value.status_code = http_client.FORBIDDEN
        self.request.return_value.json.side_effect = ValueError('no json')
        with self.assertRaisesRegex(exceptions.AccessError,
                                    'unknown error') as ae:
            self.conn._op('POST', path='fake/path', data=self.data,
                          headers=self.headers)
        exc = ae.exception
        self.assertEqual(http_client.FORBIDDEN, exc.status_code)

    def test_timed_out_session_re_established(self):
        self.auth._session_key = 'asdf1234'
        self.auth.get_session_key.return_value = 'asdf1234'
        self.conn._auth = self.auth
        self.session = mock.Mock(spec=requests.Session)
        self.conn._session = self.session
        self.request = self.session.request
        first_response = mock.MagicMock()
        first_response.status_code = http_client.FORBIDDEN
        second_response = mock.MagicMock()
        second_response.status_code = http_client.OK
        second_response.json = {'Test': 'Testing'}
        self.request.side_effect = [first_response, second_response]
        response = self.conn._op('POST', path='fake/path', data=self.data,
                                 headers=self.headers)
        self.auth.refresh_session.assert_called_with()
        self.auth.can_refresh_session.assert_called_with()
        self.assertEqual(response.json, second_response.json)

    def test_connection_error(self):
        self.request.side_effect = requests.exceptions.ConnectionError
        self.assertRaises(exceptions.ConnectionError, self.conn._op, 'GET')

    def test_unknown_http_error(self):
        self.request.return_value.status_code = http_client.CONFLICT
        self.request.return_value.json.side_effect = ValueError('no json')

        with self.assertRaisesRegex(exceptions.HTTPError,
                                    'unknown error') as cm:
            self.conn._op('GET', 'http://foo.bar')
        exc = cm.exception
        self.assertEqual(http_client.CONFLICT, exc.status_code)
        self.assertIsNone(exc.body)
        self.assertIsNone(exc.detail)

    def test_known_http_error(self):
        self.request.return_value.status_code = http_client.BAD_REQUEST
        with open('sushy/tests/unit/json_samples/error.json') as f:
            self.request.return_value.json.return_value = json.load(f)

        with self.assertRaisesRegex(exceptions.BadRequestError,
                                    'body submitted was malformed JSON') as cm:
            self.conn._op('GET', 'http://foo.bar')
        exc = cm.exception
        self.assertEqual(http_client.BAD_REQUEST, exc.status_code)
        self.assertIsNotNone(exc.body)
        self.assertIn('body submitted was malformed JSON', exc.detail)

    def test_known_http_error_nonlist_ext_info(self):
        self.request.return_value.status_code =\
            http_client.UNSUPPORTED_MEDIA_TYPE
        with open('sushy/tests/unit/json_samples/'
                  'error_single_ext_info.json') as f:
            self.request.return_value.json.return_value = json.load(f)

        with self.assertRaisesRegex(exceptions.HTTPError,
                                    'See Resolution for information') as cm:
            self.conn._op('POST', 'http://foo.bar')
        exc = cm.exception
        self.assertEqual(http_client.UNSUPPORTED_MEDIA_TYPE, exc.status_code)
        self.assertIsNotNone(exc.body)
        self.assertIn('See Resolution for information', exc.detail)

    def test_not_found_error(self):
        self.request.return_value.status_code = http_client.NOT_FOUND
        self.request.return_value.json.side_effect = ValueError('no json')

        with self.assertRaisesRegex(exceptions.ResourceNotFoundError,
                                    'Resource http://foo.bar not found') as cm:
            self.conn._op('GET', 'http://foo.bar')
        exc = cm.exception
        self.assertEqual(http_client.NOT_FOUND, exc.status_code)

    def test_server_error(self):
        self.request.return_value.status_code = (
            http_client.INTERNAL_SERVER_ERROR)
        self.request.return_value.json.side_effect = ValueError('no json')

        with self.assertRaisesRegex(exceptions.ServerSideError,
                                    'unknown error') as cm:
            self.conn._op('GET', 'http://foo.bar')
        exc = cm.exception
        self.assertEqual(http_client.INTERNAL_SERVER_ERROR, exc.status_code)

    def test_access_error(self):
        self.conn._auth.can_refresh_session.return_value = False

        self.request.return_value.status_code = http_client.FORBIDDEN
        self.request.return_value.json.side_effect = ValueError('no json')

        with self.assertRaisesRegex(exceptions.AccessError,
                                    'unknown error') as cm:
            self.conn._op('GET', 'http://foo.bar')
        exc = cm.exception
        self.assertEqual(http_client.FORBIDDEN, exc.status_code)

    def test_blocking_no_location_header(self):
        self.request.return_value.status_code = http_client.ACCEPTED
        self.request.return_value.headers = {'retry-after': 5}
        with self.assertRaisesRegex(exceptions.ConnectionError,
                                    'status 202, but no Location header'):
            self.conn._op('POST', 'http://foo.bar', blocking=True)

    @mock.patch('sushy.connector.time.sleep', autospec=True)
    def test_blocking_task_fails(self, mock_sleep):
        response1 = mock.MagicMock(spec=requests.Response)
        response1.status_code = http_client.ACCEPTED
        response1.headers = {
            'retry-after': 5,
            'location': '/redfish/v1/taskmon/1'
        }
        response2 = mock.MagicMock(spec=requests.Response)
        response2.status_code = http_client.BAD_REQUEST
        message = 'Unable to create Volume with given parameters'
        response2.json.return_value = {
            'error': {
                'message': message
            }
        }
        self.request.side_effect = [response1, response1, response2]
        with self.assertRaisesRegex(exceptions.BadRequestError, message):
            self.conn._op('POST', 'http://foo.bar', blocking=True)
