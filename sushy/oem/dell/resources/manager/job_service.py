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
from sushy.resources import common

LOG = logging.getLogger(__name__)


class ActionsField(base.CompositeField):
    delete_job_queue = common.ActionField("#DellJobService.DeleteJobQueue")


class DellJobService(base.ResourceBase):

    _actions = ActionsField('Actions')
    identity = base.Field('Id', required=True)

    def __init__(self, connector, identity, redfish_version=None,
                 registries=None):
        """A class representing a DellJobService.

        :param connector: A Connector instance
        :param identity: The identity of the DellJobService resource
        :param redfish_version: The version of Redfish. Used to construct
            the object according to schema of the given version.
        :param registries: Dict of Redfish Message Registry objects to be
            used in any resource that needs registries to parse messages.
        """
        super().__init__(
            connector, identity, redfish_version, registries)

    def delete_jobs(self, job_ids=['JID_CLEARALL']):
        """Delete the given jobs, or all jobs.

        :param job_ids: a list of job ids to delete. Clearing all the
            jobs may be accomplished using the keyword JID_CLEARALL
            as the job_id.
        """
        target_uri = self._actions.delete_job_queue.target_uri
        for job_id in job_ids:
            LOG.debug('Deleting the job %s', job_id)
            payload = {'JobID': job_id}
            self._conn.post(target_uri,
                            data=payload)
            LOG.info('Deleted the job %s', job_id)
