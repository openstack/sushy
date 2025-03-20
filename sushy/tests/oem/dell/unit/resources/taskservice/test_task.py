# Copyright (c) 2021 Dell Inc. or its subsidiaries.
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

import json
from unittest import mock

from oslotest.base import BaseTestCase
from sushy.resources.taskservice import task as sushy_task

from sushy.oem.dell.resources.taskservice import constants as ts_cons
from sushy.oem.dell.resources.taskservice import task


class TaskTestCase(BaseTestCase):

    def setUp(self):
        super().setUp()
        self.conn = mock.Mock()
        with open('sushy/tests/oem/dell/unit/json_samples/'
                  'task.json') as f:
            mock_response = self.conn.get.return_value
            mock_response.json.return_value = json.load(f)
            mock_response.status_code = 200

        self.task = sushy_task.Task(
            self.conn,
            '/redfish/v1/TaskService/Tasks/JID_257309938313')
        self.oem_task = task.DellTaskExtension(
            self.conn,
            '/redfish/v1/TaskService/Tasks/JID_257309938313')
        self.oem_task = self.oem_task.set_parent_resource(
            self.task, 'Dell')

    def test_parse_attributes(self):
        self.assertEqual('JID_257309938313', self.oem_task.identity)
        self.assertEqual('Configure: RAID.Integrated.1-1',
                         self.oem_task.name)
        self.assertEqual('Job Instance', self.oem_task.description)
        self.assertIsNone(self.oem_task.completion_time)
        self.assertEqual('TIME_NA', self.oem_task.end_time)
        self.assertEqual(ts_cons.JobState.SCHEDULED,
                         self.oem_task.job_state)
        self.assertEqual(ts_cons.JobType.RAID_CONF,
                         self.oem_task.job_type)
        # For backward compatibility
        self.assertEqual(ts_cons.JOB_STATE_SCHEDULED,
                         self.oem_task.job_state)
        self.assertEqual(ts_cons.JOB_TYPE_RAID_CONF,
                         self.oem_task.job_type)
        self.assertEqual('Task successfully scheduled.',
                         self.oem_task.message)
        self.assertEqual([], self.oem_task.message_args)
        self.assertEqual('IDRAC.2.5.JCP001', self.oem_task.message_id)
        self.assertEqual(0, self.oem_task.percent_complete)
        self.assertEqual('TIME_NOW', self.oem_task.start_time)
