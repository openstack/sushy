# Copyright (c) 2020-2021 Dell Inc. or its subsidiaries.
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

from sushy.oem.dell.resources.manager import job_collection


class DellJobCollectionTestCase(BaseTestCase):

    # Every job state iDRAC is known to report that does not mean the
    # Lifecycle Controller has stopped working on the job. 'UserIntervention'
    # is absent from the JobState enum in
    # sushy.oem.dell.resources.taskservice.constants but is reported by
    # iDRAC for firmware that is staged and awaiting a POST flash.
    NON_TERMINAL_STATES = ['New',
                           'Scheduling',
                           'Scheduled',
                           'ReadyForExecution',
                           'Waiting',
                           'Downloading',
                           'Downloaded',
                           'Running',
                           'Paused',
                           'RebootPending',
                           'RebootCompleted',
                           'PendingActivation',
                           'UserIntervention',
                           'Unknown']

    TERMINAL_STATES = ['Completed',
                       'CompletedWithErrors',
                       'Failed',
                       'RebootFailed']

    def _set_jobs(self, states):
        """Point the mocked connection at a job queue with these states.

        :param states: a list of JobState strings, one per job. A state of
            None omits the JobState field entirely.
        :returns: the list of job IDs generated, in order.
        """
        members = []
        for index, state in enumerate(states):
            job = {'@odata.id': '/redfish/v1/Managers/iDRAC.Embedded.1'
                                '/Jobs/JID_%d' % index,
                   'Id': 'JID_%d' % index}
            if state is not None:
                job['JobState'] = state
            members.append(job)

        self.conn.get.return_value.json.return_value = {
            'Id': 'JobQueue', 'Name': 'JobQueue', 'Members': members}
        return [job['Id'] for job in members]

    def setUp(self):
        super().setUp()
        self.conn = mock.Mock()
        with open('sushy/tests/oem/dell/unit/json_samples/'
                  'job_collection_expanded.json') as f:
            mock_response = self.conn.get.return_value
            mock_response.json.return_value = json.load(f)
            mock_response.status_code = 200

        mock_response = self.conn.post.return_value
        mock_response.status_code = 202
        mock_response.headers.get.return_value = '1'
        self.job_collection = job_collection.DellJobCollection(
            self.conn, '/redfish/v1/Managers/iDRAC.Embedded.1/Jobs')

    def test_get_unfinished_jobs(self):
        expected_unfinished_jobs = ['RID_878460711202']
        actual_unfinished_jobs = self.job_collection.get_unfinished_jobs()
        target_uri = ('/redfish/v1/Managers/iDRAC.Embedded.1'
                      '/Jobs?$expand=.($levels=1)')
        self.conn.get.assert_called_with(target_uri)
        self.assertEqual(expected_unfinished_jobs, actual_unfinished_jobs)

    def test_get_unfinished_jobs_non_terminal_states(self):
        expected = self._set_jobs(self.NON_TERMINAL_STATES)
        self.assertEqual(expected, self.job_collection.get_unfinished_jobs())

    def test_get_unfinished_jobs_terminal_states(self):
        self._set_jobs(self.TERMINAL_STATES)
        self.assertEqual([], self.job_collection.get_unfinished_jobs())

    def test_get_unfinished_jobs_user_intervention(self):
        """A staged firmware job awaiting a POST flash is not finished."""
        self._set_jobs(['UserIntervention'])
        self.assertEqual(['JID_0'],
                         self.job_collection.get_unfinished_jobs())

    def test_get_unfinished_jobs_unrecognised_state(self):
        """An unknown state must not be mistaken for a finished job."""
        self._set_jobs(['SomeFutureIdracState'])
        self.assertEqual(['JID_0'],
                         self.job_collection.get_unfinished_jobs())

    def test_get_unfinished_jobs_missing_job_state(self):
        self._set_jobs([None])
        self.assertEqual(['JID_0'],
                         self.job_collection.get_unfinished_jobs())

    def test_get_unfinished_jobs_mixed(self):
        self._set_jobs(['Completed', 'UserIntervention', 'Failed',
                        'RebootPending'])
        self.assertEqual(['JID_1', 'JID_3'],
                         self.job_collection.get_unfinished_jobs())

    def test_get_unfinished_jobs_empty_queue(self):
        self._set_jobs([])
        self.assertEqual([], self.job_collection.get_unfinished_jobs())
