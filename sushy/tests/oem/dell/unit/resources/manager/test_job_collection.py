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
