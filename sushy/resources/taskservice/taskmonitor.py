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

from sushy.resources import base
from sushy.resources.taskservice import task
from sushy import utils


class TaskMonitor(object):
    def __init__(self,
                 connector,
                 task_monitor,
                 redfish_version=None,
                 registries=None,
                 field_data=None):
        """A class representing a task monitor

        :param connector: A Connector instance
        :param task_monitor: The task monitor
        :param retry_after: The amount of time to wait in seconds before
            calling is_processing.
        :param redfish_version: The version of RedFish. Used to construct
            the object according to schema of the given version.
        :param registries: Dict of Redfish Message Registry objects to be
            used in any resource that needs registries to parse messages.
        :param field_data: the data to use populating the fields.
        """
        self._connector = connector
        self._task_monitor = task_monitor
        self._redfish_version = redfish_version
        self._registries = registries
        self._field_data = field_data
        self._reader = base.get_reader(connector, task_monitor)
        self._task = None

        if self._field_data:
            # We do not check 'content-length' as it is not always present
            # and will rely on task uri in those cases.
            if self._field_data.status_code == http_client.ACCEPTED:
                self._task = task.Task(self._connector, self._task_monitor,
                                       redfish_version=self._redfish_version,
                                       registries=self._registries,
                                       json_doc=self._field_data.json_doc)
        else:
            self.refresh()

    def refresh(self):
        """Refresh the Task

        Freshly retrieves/fetches the Task.
        :raises: ResourceNotFoundError
        :raises: ConnectionError
        :raises: HTTPError
        """
        self._field_data = self._reader.get_data()

        if self._field_data.status_code == http_client.ACCEPTED:
            # A Task should have been returned, but wasn't
            if int(self._field_data.headers.get('Content-Length')) == 0:
                self._task = None
                return

            # Assume that the body contains a Task since we got a 202
            if not self._task:
                self._task = task.Task(self._connector, self._task_monitor,
                                       redfish_version=self._redfish_version,
                                       registries=self._registries,
                                       json_doc=self._field_data.json_doc)
            else:
                self._task.refresh(json_doc=self._field_data.json_doc)
        else:
            self._task = None

    @property
    def task_monitor(self):
        """The TaskMonitor URI

        :returns: The TaskMonitor URI.
        """
        return self._task_monitor

    @property
    def is_processing(self):
        """Indicates if the task is still processing

        :returns: A boolean indicating if the task is still processing.
        """
        return self._field_data.status_code == http_client.ACCEPTED

    @property
    def retry_after(self):
        """The amount of time to sleep before retrying

        :returns: The amount of time in seconds to wait before calling
            is_processing.
        """
        return utils.int_or_none(self._field_data.headers.get('Retry-After'))

    @property
    def cancellable(self):
        """The amount of time to sleep before retrying

        :returns: A Boolean indicating if the Task is cancellable.
        """
        allow = self._field_data.headers.get('Allow')

        cancellable = False
        if allow and allow.upper() == 'DELETE':
            cancellable = True

        return cancellable

    @property
    def task(self):
        """The executing task

        :returns: The Task being executed.
        """

        return self._task

    def get_task(self):
        return task.Task(self._connector, self._task_monitor,
                         redfish_version=self._redfish_version,
                         registries=self._registries)
