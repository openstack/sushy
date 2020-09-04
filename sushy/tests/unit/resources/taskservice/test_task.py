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

from sushy.resources import constants as res_cons
from sushy.resources.taskservice import task
from sushy.tests.unit import base


class TaskTestCase(base.TestCase):

    def setUp(self):
        super(TaskTestCase, self).setUp()
        self.conn = mock.Mock()
        with open('sushy/tests/unit/json_samples/task.json') as f:
            self.json_doc = json.load(f)

        self.conn.get.return_value.json.return_value = self.json_doc

        message_registry = mock.Mock()
        message = mock.Mock()
        message.message = "Property %1 is read only."
        message.number_of_args = 1
        message_registry.messages = {"PropertyNotWriteable": message}

        self.task = task.Task(
            self.conn, '/redfish/v1/TaskService/Tasks/545',
            redfish_version='1.4.3',
            registries={'Base.1.0': message_registry})

    def test__parse_attributes(self):
        self.task._parse_attributes(self.json_doc)
        self.assertEqual('545', self.task.identity)
        self.assertEqual('Task 545', self.task.name)
        self.assertEqual('Task description', self.task.description)
        self.assertEqual('/taskmon/545', self.task.task_monitor)
        self.assertEqual('2012-03-07T14:44+06:00', self.task.start_time)
        self.assertEqual('2012-03-07T14:45+06:00', self.task.end_time)
        self.assertEqual(100, self.task.percent_complete)
        self.assertEqual(res_cons.TASK_STATE_COMPLETED, self.task.task_state)
        self.assertEqual(res_cons.HEALTH_OK, self.task.task_status)
        self.assertEqual(1, len(self.task.messages))
        self.assertEqual('Base.1.0.PropertyNotWriteable',
                         self.task.messages[0].message_id)
        self.assertEqual('Property %1 is read only.',
                         self.task.messages[0].message)
        self.assertEqual(res_cons.SEVERITY_WARNING,
                         self.task.messages[0].severity)

    def test_is_processing_true(self):
        self.task.status_code = http_client.ACCEPTED
        self.assertTrue(self.task.is_processing)

    def test_is_processing_false(self):
        self.task.status_code = http_client.OK
        self.assertFalse(self.task.is_processing)

    def test_parse_messages(self):
        self.task.parse_messages()
        self.assertEqual('Property SKU is read only.',
                         self.task.messages[0].message)
