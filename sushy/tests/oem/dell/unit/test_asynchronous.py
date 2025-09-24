# Copyright (c) 2020 Dell Inc. or its subsidiaries.
#
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

from unittest import mock

from oslotest.base import BaseTestCase

import sushy
from sushy.oem.dell.asynchronous import http_call


class AsychronousTestCase(BaseTestCase):

    def setUp(self):
        super().setUp()
        self.conn = mock.Mock()

    def test_http_call_post_accepted(self):
        mock_post_response = self.conn.post.return_value
        mock_post_response.status_code = 202
        mock_post_response.headers.get.return_value = '1'

        mock_get_202_response = mock.Mock()
        mock_get_202_response.status_code = 202
        mock_get_202_response.headers.get.return_value = '1'

        mock_get_200_response = mock.Mock()
        mock_get_200_response.status_code = 200

        self.conn.get.side_effect = [
            mock_get_202_response, mock_get_200_response]

        resp = http_call(self.conn, 'POST')
        self.assertIs(resp, mock_get_200_response)

    def test_http_call_post_accepted_no_location(self):
        mock_response = self.conn.post.return_value
        mock_response.status_code = 202
        mock_response.headers.get.return_value = None

        self.assertRaises(sushy.exceptions.ExtensionError,
                          http_call, self.conn, 'POST')

    @mock.patch('time.sleep', autospec=True)
    def test_http_call_404_retry_success(self, mock_sleep):
        # First call returns 404, second call succeeds
        mock_404_response = mock.Mock()
        mock_404_response.status_code = 404

        mock_200_response = mock.Mock()
        mock_200_response.status_code = 200

        self.conn.post.side_effect = [mock_404_response, mock_200_response]

        resp = http_call(self.conn, 'POST', '/some/path')

        self.assertIs(resp, mock_200_response)
        self.assertEqual(self.conn.post.call_count, 2)
        mock_sleep.assert_called_once_with(10)  # Default retry delay

    @mock.patch('time.sleep', autospec=True)
    def test_http_call_404_retry_custom_params(self, mock_sleep):
        # Test with custom retry parameters
        mock_404_response = mock.Mock()
        mock_404_response.status_code = 404

        mock_200_response = mock.Mock()
        mock_200_response.status_code = 200

        self.conn.post.side_effect = [mock_404_response, mock_200_response]

        resp = http_call(self.conn, 'POST', '/some/path',
                         max_404_retries=5, retry_404_delay=2)

        self.assertIs(resp, mock_200_response)
        self.assertEqual(self.conn.post.call_count, 2)
        mock_sleep.assert_called_once_with(2)  # Custom delay

    @mock.patch('time.sleep', autospec=True)
    def test_http_call_404_retry_exhausted(self, mock_sleep):
        # All retries return 404, should fail with ExtensionError
        mock_404_response = mock.Mock()
        mock_404_response.status_code = 404

        self.conn.post.return_value = mock_404_response

        self.assertRaisesRegex(sushy.exceptions.ExtensionError,
                               'failed with code 404',
                               http_call, self.conn, 'POST', '/some/path')

        # 1 initial + 3 retries
        self.assertEqual(self.conn.post.call_count, 4)
        self.assertEqual(mock_sleep.call_count, 3)

    @mock.patch('time.sleep', autospec=True)
    def test_http_call_non_404_error_no_retry(self, mock_sleep):
        # Non-404 errors should not trigger retry
        mock_500_response = mock.Mock()
        mock_500_response.status_code = 500

        self.conn.post.return_value = mock_500_response

        self.assertRaisesRegex(sushy.exceptions.ExtensionError,
                               'failed with code 500',
                               http_call, self.conn, 'POST', '/some/path')

        self.assertEqual(self.conn.post.call_count, 1)  # No retries
        mock_sleep.assert_not_called()

    def test_http_call_success_no_retry(self):
        # Successful response should not trigger any retry logic
        mock_200_response = mock.Mock()
        mock_200_response.status_code = 200

        self.conn.post.return_value = mock_200_response

        resp = http_call(self.conn, 'POST', '/some/path')

        self.assertIs(resp, mock_200_response)
        self.assertEqual(self.conn.post.call_count, 1)

    @mock.patch('time.sleep', autospec=True)
    def test_http_call_404_retry_with_202_polling(self, mock_sleep):
        # Test 404 retry followed by 202 polling behavior
        mock_404_response = mock.Mock()
        mock_404_response.status_code = 404

        mock_202_response = mock.Mock()
        mock_202_response.status_code = 202

        def mock_get_header(header_name, default=None):
            if header_name == 'Location':
                return '/redfish/v1/TaskService/Tasks/123'
            elif header_name == 'Retry-After':
                return None
            return default
        mock_202_response.headers.get.side_effect = mock_get_header

        mock_200_response = mock.Mock()
        mock_200_response.status_code = 200

        self.conn.post.side_effect = [mock_404_response, mock_202_response]
        self.conn.get.return_value = mock_200_response

        resp = http_call(self.conn, 'POST', '/some/path')

        self.assertIs(resp, mock_200_response)
        self.assertEqual(self.conn.post.call_count, 2)
        self.assertEqual(self.conn.get.call_count, 1)
        # Should have slept for 404 retry and 202 polling
        self.assertEqual(mock_sleep.call_count, 2)
