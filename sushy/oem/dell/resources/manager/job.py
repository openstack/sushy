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

from sushy.oem.dell import constants
from sushy.resources import base

LOG = logging.getLogger(__name__)


class DellJob(base.ResourceBase):
    """A class representing a DellJob.

    Represents the status of a single Lifecycle Controller job, such as a
    firmware update or a configuration change, tracked by iDRAC.
    """

    identity = base.Field('Id', required=True)
    name = base.Field('Name')
    description = base.Field('Description')
    job_state = base.Field('JobState')
    job_type = base.Field('JobType')
    message = base.Field('Message')
    message_id = base.Field('MessageId')
    percent_complete = base.Field('PercentComplete', adapter=int)
    start_time = base.Field('StartTime')
    end_time = base.Field('EndTime')
    completion_time = base.Field('CompletionTime')

    @property
    def is_finished(self):
        """Whether the Lifecycle Controller has stopped working on this job.

        A job counts as finished only when it is reported in one of
        :py:data:`~sushy.oem.dell.constants.TERMINAL_JOB_STATES`. Any other
        state, including one this library does not recognise, means the
        job is still in flight.

        :returns: True if the job is in a terminal state, False otherwise.
        """
        return self.job_state in constants.TERMINAL_JOB_STATES

    @property
    def is_failed(self):
        """Whether this job finished without doing what it was asked to.

        True when the job is reported in one of
        :py:data:`~sushy.oem.dell.constants.FAILED_JOB_STATES`: it failed,
        completed with errors, or its reboot failed. A job that is still
        in flight is not failed (yet); check :py:attr:`is_finished`
        first to tell the two apart.

        :returns: True if the job ended in a failed state, False otherwise.
        """
        return self.job_state in constants.FAILED_JOB_STATES
