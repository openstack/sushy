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

from sushy.resources import base as resource_base
from sushy.resources.taskservice import task
from sushy.resources.taskservice import taskmonitor
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

        self.task_monitor = taskmonitor.TaskMonitor(
            self.conn, '/Task/545',
            field_data=self.field_data
        )

    def test_init_accepted_no_content(self):
        field_data = resource_base.FieldData(
            http_client.ACCEPTED,
            {'Content-Length': 0,
             'Location': '/Task/545',
             'Retry-After': 20,
             'Allow': 'DELETE'},
            None)

        task_monitor = taskmonitor.TaskMonitor(
            self.conn, '/Task/545',
            field_data=field_data)

        self.assertEqual(http_client.ACCEPTED,
                         task_monitor._field_data._status_code)
        self.assertEqual(
            0, task_monitor._field_data._headers['Content-Length'])

    def test_init_accepted_content(self):
        self.assertIsNotNone(self.task_monitor._task)

    def test_init_no_field_data(self):
        self.conn.reset_mock()
        self.conn.get.return_value.status_code = 202
        self.conn.get.return_value.headers = {'Content-Length': 42}

        task_monitor = taskmonitor.TaskMonitor(self.conn, '/Task/545')

        self.conn.get.assert_called_with(path='/Task/545')
        self.assertEqual(1, self.conn.get.call_count)
        self.assertIsNotNone(task_monitor._task)

    def test_refresh_no_content(self):
        self.conn.reset_mock()
        self.conn.get.return_value.status_code = 202
        self.conn.get.return_value.headers = {'Content-Length': 0}

        self.task_monitor.refresh()

        self.conn.get.assert_called_with(path='/Task/545')
        self.assertEqual(1, self.conn.get.call_count)
        self.assertIsNone(self.task_monitor._task)

    def test_refresh_content_no_task(self):
        self.conn.reset_mock()
        self.conn.get.return_value.status_code = 202
        self.conn.get.return_value.headers = {'Content-Length': 42}
        self.task_monitor._task = None

        self.task_monitor.refresh()

        self.conn.get.assert_called_with(path='/Task/545')
        self.assertEqual(1, self.conn.get.call_count)
        self.assertIsNotNone(self.task_monitor._task)

    def test_refresh_content_task(self):
        self.conn.reset_mock()
        self.conn.get.return_value.status_code = 202
        self.conn.get.return_value.headers = {'Content-Length': 42}

        self.task_monitor.refresh()

        self.conn.get.assert_called_with(path='/Task/545')
        self.assertEqual(1, self.conn.get.call_count)
        self.assertIsNotNone(self.task_monitor._task)

    def test_refresh_done(self):
        self.conn.reset_mock()
        self.conn.get.return_value.status_code = 200

        self.task_monitor.refresh()

        self.conn.get.assert_called_once_with(path='/Task/545')
        self.assertIsNone(self.task_monitor._task)

    def test_task_monitor(self):
        self.assertEqual('/Task/545', self.task_monitor.task_monitor)

    def test_is_processing(self):
        self.assertTrue(self.task_monitor.is_processing)

    def test_retry_after(self):
        self.assertEqual(20, self.task_monitor.retry_after)

    def test_cancellable(self):
        self.assertTrue(self.task_monitor.cancellable)

    def test_not_cancellable_no_header(self):
        field_data = resource_base.FieldData(
            http_client.ACCEPTED,
            {'Content-Length': 42,
             'Location': '/Task/545',
             'Retry-After': 20},
            self.json_doc)

        task_monitor = taskmonitor.TaskMonitor(
            self.conn, '/Task/545',
            field_data=field_data
        )

        self.assertFalse(task_monitor.cancellable)

    def test_not_cancellable(self):
        field_data = resource_base.FieldData(
            http_client.ACCEPTED,
            {'Content-Length': 42,
             'Location': '/Task/545',
             'Retry-After': 20,
             'Allow': 'GET'},
            self.json_doc)

        task_monitor = taskmonitor.TaskMonitor(
            self.conn, '/Task/545',
            field_data=field_data
        )

        self.assertFalse(task_monitor.cancellable)

    def test_task(self):
        tm_task = self.task_monitor.task

        self.assertIsInstance(tm_task, task.Task)
        self.assertEqual('545', tm_task.identity)
