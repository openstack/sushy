# Copyright (c) 2026 Dell Inc. or its subsidiaries.
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

from sushy.oem.dell.resources.manager import job


class DellJobTestCase(BaseTestCase):

    def setUp(self):
        super().setUp()
        self.conn = mock.Mock()
        with open('sushy/tests/oem/dell/unit/json_samples/'
                  'job.json') as f:
            mock_response = self.conn.get.return_value
            mock_response.json.return_value = json.load(f)
            mock_response.status_code = 200

        self.dell_job = job.DellJob(
            self.conn,
            '/redfish/v1/Managers/iDRAC.Embedded.1/Jobs/JID_878623579002')

    def test_parse_attributes(self):
        self.assertEqual('JID_878623579002', self.dell_job.identity)
        self.assertEqual('Firmware Update: BIOS', self.dell_job.name)
        self.assertEqual('Job Instance', self.dell_job.description)
        self.assertEqual('Completed', self.dell_job.job_state)
        self.assertEqual('FirmwareUpdate', self.dell_job.job_type)
        self.assertEqual('Job completed successfully.',
                         self.dell_job.message)
        self.assertEqual('PR19', self.dell_job.message_id)
        self.assertEqual(100, self.dell_job.percent_complete)
        self.assertEqual('2024-06-01T15:10:02', self.dell_job.start_time)
        self.assertEqual('TIME_NA', self.dell_job.end_time)
        self.assertEqual('2024-06-01T15:21:33',
                         self.dell_job.completion_time)

    def test_is_finished_and_is_failed(self):
        # (job_state, is_finished, is_failed) for every branch of both
        # properties: each terminal state, each known non-terminal state,
        # a state this library does not know, and no state at all.
        cases = [
            ('Completed', True, False),
            ('CompletedWithErrors', True, True),
            ('Failed', True, True),
            ('RebootFailed', True, True),
            ('Scheduled', False, False),
            ('Running', False, False),
            ('UserIntervention', False, False),
            ('SomeFutureState', False, False),
            (None, False, False),
        ]
        for state, finished, failed in cases:
            with self.subTest(state=state):
                self.dell_job.job_state = state
                self.assertIs(finished, self.dell_job.is_finished)
                self.assertIs(failed, self.dell_job.is_failed)
