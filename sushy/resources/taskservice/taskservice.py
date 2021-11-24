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
# https://redfish.dmtf.org/schemas/v1/TaskService.v1_1_5.json

import logging

from sushy.resources import base
from sushy.resources import common
from sushy.resources.taskservice import constants as ts_cons
from sushy.resources.taskservice import task
from sushy import utils

LOG = logging.getLogger(__name__)


class TaskService(base.ResourceBase):

    identity = base.Field('Id', required=True)
    """The task service identity"""

    name = base.Field('Name', required=True)
    """The task service name"""

    service_enabled = base.Field('ServiceEnabled')
    """The status of whether this service is enabled"""

    status = common.StatusField('Status')
    """The status of the task service"""

    overwrite_policy = base.MappedField(
        'CompletedTaskOverWritePolicy', ts_cons.OverWritePolicy)
    """The overwrite policy for completed tasks"""

    event_on_task_state_change = base.Field(
        'LifeCycleEventOnTaskStateChange', adapter=bool)
    """Whether a task state change sends an event"""

    def __init__(self, connector, identity, redfish_version=None,
                 registries=None, root=None):
        """A class representing a TaskService

        :param connector: A Connector instance
        :param identity: The identity of the TaskService resource
        :param redfish_version: The version of RedFish. Used to construct
            the object according to schema of given version
        :param registries: Dict of Redfish Message Registry objects to be
            used in any resource that needs registries to parse messages
        :param root: Sushy root object. Empty for Sushy root itself.
        """
        super(TaskService, self).__init__(
            connector, identity, redfish_version=redfish_version,
            registries=registries, root=root)

    @property
    @utils.cache_it
    def tasks(self):
        """Property to reference `TaskCollection` instance

        It is set once when the first time it is queried. On refresh,
        this property is marked as stale (greedy-refresh not done).
        Here the actual refresh of the sub-resource happens, if stale.
        """
        return task.TaskCollection(
            self._conn, utils.get_sub_resource_path_by(self, 'Tasks'),
            redfish_version=self.redfish_version,
            registries=self.registries, root=self.root)
