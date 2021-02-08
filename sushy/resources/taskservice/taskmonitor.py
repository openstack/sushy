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

import logging

from sushy import taskmonitor

LOG = logging.getLogger(__name__)


def TaskMonitor(connector,
                task_monitor,
                redfish_version=None,
                registries=None,
                field_data=None):
    """A class representing a task monitor

    Deprecated, use sushy.taskmonitor.TaskMonitor.

    :param connector: A Connector instance
    :param task_monitor: The task monitor URI
    :param redfish_version: The version of RedFish. Used to construct
        the object according to schema of the given version.
    :param registries: Dict of Redfish Message Registry objects to be
        used in any resource that needs registries to parse messages.
    :param field_data: the data to use populating the fields.
    """
    LOG.warning('sushy.resources.taskservice.taskmonitor.TaskMonitor '
                'is deprecated. Use sushy.taskmonitor.TaskMonitor.')
    return taskmonitor.TaskMonitor(connector, task_monitor, redfish_version,
                                   registries, field_data)
