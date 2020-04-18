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

from datetime import datetime
from datetime import timedelta
from unittest import mock

from dateutil import parser

from sushy.resources.task_monitor import TaskMonitor
from sushy.tests.unit import base


class TaskMonitorTestCase(base.TestCase):

    def setUp(self):
        super(TaskMonitorTestCase, self).setUp()
        self.conn = mock.Mock()
        self.data = {'fake': 'data'}
        self.http_date = 'Fri, 31 Dec 1999 23:59:59 GMT'
        self.seconds = 120
        self.datetime = parser.parse(self.http_date)
        self.req_headers = {'X-Fake': 'header'}
        self.res_headers1 = {'location': 'https://sample.com/foo/bar',
                             'retry-after': self.http_date}
        self.res_headers2 = {'location': 'https://sample.com/foo/bar',
                             'retry-after': str(self.seconds)}

    def test_task_in_progress(self):
        self.conn.post.return_value.status_code = 202
        self.conn.post.return_value.headers = self.res_headers1.copy()
        self.conn.get.return_value.status_code = 202
        self.conn.get.return_value.headers = self.res_headers1.copy()
        self.conn.get.return_value.json.return_value = {}
        res = self.conn.post(path='fake/path', data=self.data.copy(),
                             headers=self.req_headers.copy())
        tm = TaskMonitor(self.conn, res.headers.get('location'))\
            .set_retry_after(res.headers.get('retry-after'))
        self.assertIsNotNone(tm)
        self.assertTrue(tm.in_progress)

    def test_task_not_in_progress(self):
        self.conn.post.return_value.status_code = 202
        self.conn.post.return_value.headers = self.res_headers1.copy()
        self.conn.get.return_value.status_code = 201
        self.conn.get.return_value.json.return_value = self.data.copy()
        res = self.conn.post(path='fake/path', data=self.data.copy(),
                             headers=self.req_headers.copy())
        tm = TaskMonitor(self.conn, res.headers.get('location'))\
            .set_retry_after(res.headers.get('retry-after'))
        self.assertIsNotNone(tm)
        self.assertFalse(tm.in_progress)

    def test_retry_after_http_date(self):
        self.conn.post.return_value.status_code = 202
        self.conn.post.return_value.headers = self.res_headers1.copy()
        self.conn.get.return_value.status_code = 202
        self.conn.get.return_value.headers = self.res_headers1.copy()
        self.conn.get.return_value.json.return_value = {}
        res = self.conn.post(path='fake/path', data=self.data.copy(),
                             headers=self.req_headers.copy())
        tm = TaskMonitor(self.conn, res.headers.get('location')) \
            .set_retry_after(res.headers.get('retry-after'))
        self.assertIsNotNone(tm)
        self.assertEqual(self.datetime, tm.retry_after)

    def test_retry_after_seconds(self):
        self.conn.post.return_value.status_code = 202
        self.conn.post.return_value.headers = self.res_headers2.copy()
        self.conn.get.return_value.status_code = 202
        self.conn.get.return_value.headers = self.res_headers2.copy()
        self.conn.get.return_value.json.return_value = {}
        start = datetime.now() + timedelta(seconds=self.seconds)
        res = self.conn.post(path='fake/path', data=self.data.copy(),
                             headers=self.req_headers.copy())
        tm = TaskMonitor(self.conn, res.headers.get('location')) \
            .set_retry_after(res.headers.get('retry-after'))
        end = datetime.now() + timedelta(seconds=self.seconds)
        self.assertIsNotNone(tm)
        self.assertTrue(start <= tm.retry_after <= end)

    def test_sleep_for(self):
        self.conn.post.return_value.status_code = 202
        self.conn.post.return_value.headers = self.res_headers2.copy()
        self.conn.get.return_value.status_code = 202
        self.conn.get.return_value.headers = self.res_headers2.copy()
        self.conn.get.return_value.json.return_value = {}
        start = datetime.now()
        res = self.conn.post(path='fake/path', data=self.data.copy(),
                             headers=self.req_headers.copy())
        tm = TaskMonitor(self.conn, res.headers.get('location')) \
            .set_retry_after(res.headers.get('retry-after'))
        self.assertIsNotNone(tm)
        sleep_for = tm.sleep_for
        elapsed = (datetime.now() - start).total_seconds()
        self.assertTrue(self.seconds - elapsed <= sleep_for <= self.seconds)

    def test_response(self):
        self.conn.post.return_value.status_code = 202
        self.conn.post.return_value.headers = self.res_headers1.copy()
        self.conn.get.return_value.status_code = 201
        self.conn.get.return_value.json.return_value = self.data.copy()
        res = self.conn.post(path='fake/path', data=self.data.copy(),
                             headers=self.req_headers.copy())
        tm = TaskMonitor(self.conn, res.headers.get('location')) \
            .set_retry_after(res.headers.get('retry-after'))
        self.assertIsNotNone(tm)
        self.assertFalse(tm.in_progress)
        response = tm.response
        self.assertEqual(201, response.status_code)
        self.assertEqual(self.data.copy(), response.json())
