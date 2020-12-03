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

import json
from unittest import mock

from sushy.resources import constants as res_cons
from sushy.resources.taskservice import constants as ts_cons
from sushy.resources.taskservice import task
from sushy.resources.taskservice import taskservice
from sushy.tests.unit import base


class TaskServiceTestCase(base.TestCase):

    def setUp(self):
        super(TaskServiceTestCase, self).setUp()
        self.conn = mock.Mock()
        with open('sushy/tests/unit/json_samples/taskservice.json') as f:
            self.json_doc = json.load(f)

        self.conn.get.return_value.json.return_value = self.json_doc

        self.tsk_serv = taskservice.TaskService(
            self.conn, '/redfish/v1/TaskService/TaskService',
            redfish_version='1.3.0')

    def test__parse_attributes(self):
        self.tsk_serv._parse_attributes(self.json_doc)
        self.assertEqual('TaskService', self.tsk_serv.identity)
        self.assertTrue(self.tsk_serv.service_enabled)
        self.assertTrue(self.tsk_serv.event_on_task_state_change)
        self.assertEqual(res_cons.STATE_ENABLED, self.tsk_serv.status.state)
        self.assertEqual(res_cons.HEALTH_OK, self.tsk_serv.status.health)
        self.assertEqual(self.tsk_serv.overwrite_policy,
                         ts_cons.OVERWRITE_POLICY_MANUAL)

    @mock.patch.object(task, 'TaskCollection', autospec=True)
    def test_tasks(self, task_collection_mock):
        self.tsk_serv.tasks
        task_collection_mock.assert_called_once_with(
            self.conn, '/redfish/v1/TaskService/Tasks',
            self.tsk_serv.redfish_version,
            self.tsk_serv._registries)
