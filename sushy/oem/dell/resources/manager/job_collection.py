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

import logging

from sushy.resources import base

from sushy.oem.dell import constants

LOG = logging.getLogger(__name__)


class DellJobCollection(base.ResourceBase):

    _JOB_EXPAND = '?$expand=.($levels=1)'

    def __init__(self, connector, identity, redfish_version=None,
                 registries=None):
        """A class representing a DellJobCollection.

        :param connector: A Connector instance
        :param identity: The identity of the DellJobCollection resource
        :param redfish_version: The version of Redfish. Used to construct
            the object according to schema of the given version.
        :param registries: Dict of Redfish Message Registry objects to be
            used in any resource that needs registries to parse messages
        """
        super().__init__(
            connector, identity, redfish_version, registries)

    def get_unfinished_jobs(self):
        """Get the unfinished jobs.

        :returns: A list of unfinished jobs.
        """
        job_expand_uri = f'{self._path}{self._JOB_EXPAND}'
        unfinished_jobs = []
        LOG.debug('Getting unfinished jobs...')
        job_response = self._conn.get(job_expand_uri)
        data = job_response.json()
        for job in data['Members']:
            if job['JobState'] in constants.INCOMPLETE_JOB_STATES:
                unfinished_jobs.append(job['Id'])
        LOG.info('Got unfinished jobs')
        return unfinished_jobs
