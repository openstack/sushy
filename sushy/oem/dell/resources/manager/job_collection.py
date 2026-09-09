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

from sushy.oem.dell.resources.manager import job
from sushy.resources import base

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

    def get_jobs(self, job_ids=None):
        """Get the status of jobs in this collection.

        Performs a single GET of the expanded job collection and builds a
        :class:`~sushy.oem.dell.resources.manager.job.DellJob` for each
        member from the document that GET already returned, without
        issuing any further requests.

        :param job_ids: an optional list of job identities to filter by.
            If given, only jobs whose ``Id`` is among them are returned,
            preserving the order in which they appear in the collection.
            If not given, all jobs in the collection are returned.
        :returns: a list of :class:`~sushy.oem.dell.resources.manager.
            job.DellJob` instances.
        """
        job_expand_uri = f'{self._path}{self._JOB_EXPAND}'
        job_response = self._conn.get(job_expand_uri)
        data = job_response.json()
        jobs = []
        for member in data['Members']:
            job_id = member.get('Id')
            if job_ids is not None and job_id not in job_ids:
                continue
            job_path = member.get('@odata.id', f'{self._path}/{job_id}')
            jobs.append(job.DellJob(
                self._conn, job_path, json_doc=member,
                redfish_version=self.redfish_version,
                registries=self.registries, root=self.root))
        return jobs

    def get_job(self, job_id):
        """Get the status of a single job.

        Unlike :py:meth:`get_jobs`, this performs its own GET of the job
        resource rather than reading it out of the collection.

        :param job_id: the identity of the job to fetch.
        :returns: a :class:`~sushy.oem.dell.resources.manager.job.DellJob`
            instance.
        :raises: ResourceNotFoundError if no job with this identity exists.
        """
        return job.DellJob(
            self._conn, f'{self._path}/{job_id}',
            redfish_version=self.redfish_version,
            registries=self.registries, root=self.root)

    def get_unfinished_jobs(self):
        """Get the unfinished jobs.

        A job counts as finished only when the iDRAC reports it in one of
        :py:data:`~sushy.oem.dell.constants.TERMINAL_JOB_STATES`. Every
        other state, including states this library does not recognise, is
        reported as unfinished so that a job the Lifecycle Controller is
        still working on is never mistaken for a completed one.

        :returns: A list of unfinished jobs.
        """
        unfinished_jobs = []
        for dell_job in self.get_jobs():
            if not dell_job.is_finished:
                LOG.debug('Job %(id)s is in state %(state)s, treating it '
                          'as unfinished',
                          {'id': dell_job.identity,
                           'state': dell_job.job_state})
                unfinished_jobs.append(dell_job.identity)
        return unfinished_jobs
