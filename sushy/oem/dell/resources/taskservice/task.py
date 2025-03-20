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

import logging

from sushy.resources import base
from sushy.resources.oem import base as oem_base

from sushy.oem.dell.resources.taskservice import constants as ts_cons

LOG = logging.getLogger(__name__)


class DellTaskExtension(oem_base.OEMResourceBase):
    """Dell OEM extension for DellJob type"""
    identity = base.Field('Id', required=True)

    name = base.Field('Name', required=True)

    description = base.Field('Description')

    completion_time = base.Field('CompletionTime')
    """Job completion time"""

    end_time = base.Field('EndTime')
    """End time of job

    Timestamp until when the service will wait for a job to complete.
    If a job does not complete within this time, it is killed and marked
    as failed. TIME_NA is a default value and implies EndTime is not
    applicable.
    """

    job_state = base.MappedField('JobState', ts_cons.JobState)
    """Job state"""

    job_type = base.MappedField('JobType', ts_cons.JobType)
    """Job type"""

    message = base.Field('Message')
    """The status message for job"""

    message_args = base.Field('MessageArgs')
    """Array of message arguments for message field"""

    message_id = base.Field('MessageId')
    """Message id for job"""

    percent_complete = base.Field('PercentComplete', adapter=int)
    """The percentage completion of job"""

    start_time = base.Field('StartTime')
    """Scheduled start time of job

    String that will contain a timestamp in Edm.DateTime format.
    TIME_NOW is a default value and implies apply pending configuration
    now.
    """


def get_extension(*args, **kwargs):
    return DellTaskExtension
