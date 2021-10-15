# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from http import client as http_client
import json
from unittest import mock

import requests

from sushy import exceptions
from sushy.resources import base as resource_base
from sushy.resources.taskservice import task
from sushy import taskmonitor
from sushy.tests.unit import base


class TaskMonitorTestCase(base.TestCase):

    def setUp(self):
        super(TaskMonitorTestCase, self).setUp()
        self.conn = mock.Mock()

        with open('sushy/tests/unit/json_samples/task.json') as f:
            self.json_doc = json.load(f)

        self.conn.get.return_value.json.return_value = self.json_doc

        self.field_data = resource_base.FieldData(
            http_client.ACCEPTED,
            {'Content-Length': 42,
             'Location': '/Task/545',
             'Retry-After': 20,
             'Allow': 'DELETE'},
            self.json_doc)

        self.response = mock.Mock()
        self.response.status_code = http_client.ACCEPTED
        self.response.headers = {'Content-Length': 42,
                                 'Location': '/Task/545',
                                 'Retry-After': 20,
                                 'Allow': 'DELETE'}
        self.response.content = json.dumps(self.json_doc).encode('utf-8')
        self.response.json.return_value = self.json_doc

        self.task_monitor = taskmonitor.TaskMonitor(
            self.conn, '/Task/545',
            response=self.response
        )

    def test_init_accepted_no_content(self):
        response = mock.Mock()
        response.status_code = http_client.ACCEPTED
        response.headers = {'Location': '/Task/545',
                            'Retry-After': 20,
                            'Allow': 'DELETE'}
        response.content = None

        task_monitor = taskmonitor.TaskMonitor(
            self.conn, '/Task/545',
            response=response)

        self.assertIsNone(task_monitor.task)

    def test_init_accepted_content(self):
        self.assertIsNotNone(self.task_monitor.task)

    def test_init_no_response(self):
        self.conn.reset_mock()
        self.conn.get.return_value.status_code = 202
        self.conn.get.return_value.headers = {'Content-Length': 42}

        task_monitor = taskmonitor.TaskMonitor(self.conn, '/Task/545')

        self.conn.get.assert_called_with(path='/Task/545')
        self.assertEqual(1, self.conn.get.call_count)
        self.assertIsNotNone(task_monitor.task)

    def test_refresh_no_content(self):
        self.conn.reset_mock()
        self.conn.get.return_value.status_code = 202
        self.conn.get.return_value.headers = {'Content-Length': 0}
        self.conn.get.return_value.content = None

        self.task_monitor.refresh()

        self.conn.get.assert_called_with(path='/Task/545')
        self.assertEqual(1, self.conn.get.call_count)
        self.assertIsNone(self.task_monitor.task)

    def test_refresh_content_no_task(self):
        self.conn.reset_mock()
        self.conn.get.return_value.status_code = 202
        self.conn.get.return_value.headers = {'Content-Length': 42}
        self.task_monitor._task = None

        self.task_monitor.refresh()

        self.conn.get.assert_called_with(path='/Task/545')
        self.assertEqual(1, self.conn.get.call_count)
        self.assertIsNotNone(self.task_monitor.task)

    def test_refresh_content_task(self):
        self.conn.reset_mock()
        self.conn.get.return_value.status_code = 202
        self.conn.get.return_value.headers = {'Content-Length': 42}

        self.task_monitor.refresh()

        self.conn.get.assert_called_with(path='/Task/545')
        self.assertEqual(1, self.conn.get.call_count)
        self.assertIsNotNone(self.task_monitor.task)

    def test_refresh_done(self):
        self.conn.reset_mock()
        self.conn.get.return_value.status_code = 200

        self.task_monitor.refresh()

        self.conn.get.assert_called_once_with(path='/Task/545')
        self.assertIsNone(self.task_monitor.task)

    def test_task_monitor_uri(self):
        self.assertEqual('/Task/545', self.task_monitor.task_monitor_uri)

    def test_is_processing(self):
        self.assertTrue(self.task_monitor.is_processing)

    def test_check_is_processing_not_processing(self):
        response = mock.Mock()
        response.status_code = http_client.OK
        response.headers = {}
        response.content = None
        task_monitor = taskmonitor.TaskMonitor(
            self.conn, '/Task/545',
            response=response)

        self.assertEqual(False, task_monitor.check_is_processing)

    def test_check_is_processing_refreshing(self):
        self.conn.reset_mock()
        self.conn.get.return_value.status_code = 202
        self.conn.get.return_value.headers = {}
        self.conn.get.return_value.content = None

        task_monitor = taskmonitor.TaskMonitor(
            self.conn, '/Task/545')

        self.assertEqual(True, task_monitor.check_is_processing)

    def test_cancellable(self):
        self.assertTrue(self.task_monitor.cancellable)

    def test_sleep_for_retry_after_empty(self):
        self.task_monitor._response.headers["Retry-After"] = None
        self.assertEqual(1, self.task_monitor.sleep_for)

    def test_sleep_for_retry_after_digit(self):
        self.assertEqual(20, self.task_monitor.sleep_for)

    def test_sleep_for_retry_after_date_past(self):
        self.task_monitor._response.headers["Retry-After"] =\
            'Fri, 31 Dec 1999 23:59:59 GMT'
        self.assertEqual(0, self.task_monitor.sleep_for)

    def test_not_cancellable_no_header(self):
        response = mock.Mock()
        response.status_code = http_client.ACCEPTED
        response.headers = {
            'Content-Length': 42,
            'Location': '/Task/545',
            'Retry-After': 20}
        response.json.return_value = self.json_doc

        task_monitor = taskmonitor.TaskMonitor(
            self.conn, '/Task/545',
            response=response
        )

        self.assertFalse(task_monitor.cancellable)

    def test_not_cancellable(self):
        response = mock.Mock()
        response.status_code = http_client.ACCEPTED
        response.headers = {
            'Content-Length': 42,
            'Location': '/Task/545',
            'Retry-After': 20,
            'Allow': 'GET'}
        response.json.return_value = self.json_doc

        task_monitor = taskmonitor.TaskMonitor(
            self.conn, '/Task/545',
            response=response
        )

        self.assertFalse(task_monitor.cancellable)

    def test_task(self):
        tm_task = self.task_monitor.task

        self.assertIsInstance(tm_task, task.Task)
        self.assertEqual('545', tm_task.identity)

    def test_get_task(self):
        tm_task = self.task_monitor.get_task()

        self.assertIsInstance(tm_task, task.Task)
        self.assertEqual('545', tm_task.identity)

    @mock.patch('time.sleep', autospec=True)
    def test_wait(self, mock_time):
        self.conn.reset_mock()
        response1 = mock.MagicMock(spec=requests.Response)
        response1.status_code = http_client.ACCEPTED
        response1.headers = {
            'Retry-After': 5,
            'Location': '/redfish/v1/taskmon/1',
            'Content-Length': 10
        }
        response1.json.return_value = {'Id': 3, 'Name': 'Test'}

        response2 = mock.MagicMock(spec=requests.Response)
        response2.status_code = http_client.OK
        response2.headers = {
            'Retry-After': 5,
            'Location': '/redfish/v1/taskmon/1',
            'Content-Length': 10
        }
        response2.json.return_value = {'Id': 3, 'Name': 'Test'}

        self.conn.get.side_effect = [response1, response2]
        self.task_monitor.wait(60)

        self.assertFalse(self.task_monitor.is_processing)
        self.assertEqual(response2, self.task_monitor.response)

    @mock.patch('time.sleep', autospec=True)
    def test_wait_timeout(self, mock_time):
        self.conn.reset_mock()
        response1 = mock.MagicMock(spec=requests.Response)
        response1.status_code = http_client.ACCEPTED
        response1.headers = {
            'Retry-After': 5,
            'Location': '/redfish/v1/taskmon/1',
            'Content-Length': 10
        }
        response1.json.return_value = {'Id': 3, 'Name': 'Test'}

        self.conn.get.side_effect = [response1, response1]

        self.assertRaises(exceptions.ConnectionError,
                          self.task_monitor.wait, -10)

    def test_from_response_no_content(self):
        self.conn.reset_mock()
        self.conn.get.return_value.status_code = 202
        response = mock.Mock()
        response.content = None
        response.headers = {'Location': '/Task/545'}
        response.status_code = http_client.ACCEPTED

        tm = taskmonitor.TaskMonitor.from_response(
            self.conn, response,
            '/redfish/v1/UpdateService/Actions/SimpleUpdate')

        self.assertIsInstance(tm, taskmonitor.TaskMonitor)
        self.assertEqual('/Task/545', tm.task_monitor_uri)
        self.assertIsNotNone(tm.task)
        self.assertEqual('545', tm.task.identity)

    def test_from_response_odata_id(self):
        response = mock.Mock()
        response.content = "something"
        response.json.return_value = {'Id': '545', 'Name': 'test',
                                      '@odata.id': '545'}
        response.headers = {'Location': '/TaskMonitor/'}
        response.status_code = http_client.ACCEPTED

        tm = taskmonitor.TaskMonitor.from_response(
            self.conn, response,
            '/redfish/v1/UpdateService/Actions/SimpleUpdate')

        self.assertIsInstance(tm, taskmonitor.TaskMonitor)
        self.assertEqual('/TaskMonitor/545', tm.task_monitor_uri)
        self.assertIsNotNone(tm.task)
        self.assertEqual('545', tm.task.identity)

    def test_from_response_location_header_missing(self):
        response = mock.Mock()
        response.content = "something"
        response.json.return_value = {'Id': '545', 'Name': 'test'}
        response.headers = {}
        response.status_code = http_client.ACCEPTED

        self.assertRaises(exceptions.MissingHeaderError,
                          taskmonitor.TaskMonitor.from_response,
                          self.conn, response,
                          '/redfish/v1/UpdateService/Actions/SimpleUpdate')

    def test_from_response(self):
        response = mock.Mock()
        response.content = "something"
        response.json.return_value = {'Id': '545', 'Name': 'test'}
        response.headers = {'Location': '/Task/545'}
        response.status_code = http_client.ACCEPTED

        tm = taskmonitor.TaskMonitor.from_response(
            self.conn, response,
            '/redfish/v1/UpdateService/Actions/SimpleUpdate')

        self.assertIsInstance(tm, taskmonitor.TaskMonitor)
        self.assertEqual('/Task/545', tm.task_monitor_uri)
        self.assertIsNotNone(tm.task)
        self.assertEqual('545', tm.task.identity)
