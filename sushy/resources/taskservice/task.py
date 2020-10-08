# Copyright (c) 2020 Dell, Inc. or its subsidiaries
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# This is referred from Redfish standard schema.
# https://redfish.dmtf.org/schemas/Task.v1_4_3.json

from http import client as http_client
import logging

from sushy.resources import base
from sushy.resources import mappings as res_maps
from sushy.resources.registry import message_registry
from sushy.resources.taskservice import mappings as task_maps
from sushy import utils


LOG = logging.getLogger(__name__)


class Task(base.ResourceBase):

    identity = base.Field('Id', required=True)
    """The Task identity"""

    name = base.Field('Name', required=True)
    """The Task name"""

    description = base.Field('Description')
    """The Task description"""

    task_monitor = base.Field('TaskMonitor')
    """An opaque URL that the client can use to monitor an asynchronous
       operation"""

    start_time = base.Field('StartTime')
    """Start time of the Task"""

    end_time = base.Field('EndTime')
    """End time of the Task"""

    percent_complete = base.Field('PercentComplete', adapter=utils.int_or_none)
    """Percentage complete of the Task"""

    task_state = base.MappedField('TaskState', task_maps.TASK_STATE_VALUE_MAP)
    """The Task state"""

    task_status = base.MappedField('TaskStatus', res_maps.HEALTH_VALUE_MAP)
    """The Task status"""

    messages = base.MessageListField("Messages")
    """List of :class:`.MessageListField` with messages from the Task"""

    def __init__(self, connector, identity, redfish_version=None,
                 registries=None, json_doc=None):
        """A class representing a Task

        :param connector: A Connector instance
        :param identity: The identity of the task
        :param redfish_version: The version of RedFish. Used to construct
            the object according to schema of the given version.
        :param registries: Dict of Redfish Message Registry objects to be
            used in any resource that needs registries to parse messages
        :param field_data: the data to use populating the fields
        """
        super(Task, self).__init__(
            connector, identity, redfish_version, registries,
            json_doc=json_doc)

    @property
    def is_processing(self):
        """Indicates if the Task is processing"""
        return self.status_code == http_client.ACCEPTED

    def parse_messages(self):
        """Parses the messages"""
        for m in self.messages:
            message_registry.parse_message(self._registries, m)


class TaskCollection(base.ResourceCollectionBase):

    @property
    def _resource_type(self):
        return Task

    @property
    @utils.cache_it
    def summary(self):
        """Summary of task ids and corresponding state

        :returns: dictionary in the format
            {'jid_123456789': sushy.TASK_STATE_NEW,
            'jid_123454321': sushy.TASK_STATE_RUNNING}
        """
        task_dict = {}
        for task in self.get_members():
            task_dict[task.identity] = task.task_state
        return task_dict
