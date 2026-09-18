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

from sushy import exceptions
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

    def test_get_jobs(self):
        self.conn.get.reset_mock()
        jobs = self.job_collection.get_jobs()
        target_uri = ('/redfish/v1/Managers/iDRAC.Embedded.1'
                      '/Jobs?$expand=.($levels=1)')
        self.conn.get.assert_called_once_with(target_uri)
        self.assertEqual(1, len(jobs))
        dell_job = jobs[0]
        self.assertEqual('RID_878460711202', dell_job.identity)
        self.assertEqual('Reboot3', dell_job.name)
        self.assertEqual('Job Instance', dell_job.description)
        self.assertEqual('Running', dell_job.job_state)
        self.assertEqual('RebootForce', dell_job.job_type)
        self.assertEqual('Reboot is complete.', dell_job.message)
        self.assertEqual('RED030', dell_job.message_id)
        self.assertEqual(100, dell_job.percent_complete)
        self.assertEqual('TIME_NOW', dell_job.start_time)
        self.assertEqual('TIME_NA', dell_job.end_time)
        self.assertEqual('2020-04-25T15:21:33', dell_job.completion_time)
        self.assertFalse(dell_job.is_finished)

    def test_get_jobs_filters_by_job_ids(self):
        expected = self._set_jobs(
            ['Completed', 'UserIntervention', 'Failed', 'RebootPending'])
        self.conn.get.reset_mock()
        jobs = self.job_collection.get_jobs(
            job_ids=[expected[3], expected[1]])
        self.assertEqual([expected[1], expected[3]],
                         [dell_job.identity for dell_job in jobs])
        self.conn.get.assert_called_once()

    def test_get_jobs_member_without_id_raises(self):
        # Id is a required field of DellJob, so a member lacking it is a
        # malformed response and surfaces as such rather than being
        # silently dropped.
        base_uri = '/redfish/v1/Managers/iDRAC.Embedded.1/Jobs'
        no_id_member = {
            '@odata.id': base_uri + '/JID_0', 'JobState': 'Completed'}
        self.conn.get.return_value.json.return_value = {
            'Id': 'JobQueue', 'Name': 'JobQueue',
            'Members': [no_id_member]}
        self.assertRaises(exceptions.MissingAttributeError,
                          self.job_collection.get_jobs)

    def test_get_job(self):
        with open('sushy/tests/oem/dell/unit/json_samples/'
                  'job.json') as f:
            self.conn.get.return_value.json.return_value = json.load(f)
        self.conn.get.reset_mock()
        dell_job = self.job_collection.get_job('JID_878623579002')
        target_uri = ('/redfish/v1/Managers/iDRAC.Embedded.1'
                      '/Jobs/JID_878623579002')
        self.conn.get.assert_called_once_with(path=target_uri)
        self.assertEqual('JID_878623579002', dell_job.identity)
        self.assertEqual('Completed', dell_job.job_state)
        self.assertTrue(dell_job.is_finished)
