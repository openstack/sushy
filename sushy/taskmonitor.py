# Copyright (c) 2021 Dell, Inc. or its subsidiaries
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

from datetime import datetime
from http import client as http_client
import logging
import time
from urllib.parse import urljoin

from dateutil import parser

from sushy import exceptions
from sushy.resources.taskservice import task

LOG = logging.getLogger(__name__)


class TaskMonitor(object):
    def __init__(self,
                 connector,
                 task_monitor_uri,
                 redfish_version=None,
                 registries=None,
                 response=None):
        """A class representing a task monitor

        :param connector: A Connector instance
        :param task_monitor_uri: The task monitor URI
        :param redfish_version: The version of Redfish. Used to construct
            the object according to schema of the given version.
        :param registries: Dict of Redfish Message Registry objects to be
            used in any resource that needs registries to parse messages.
        :param response: Raw response
        """
        self._connector = connector
        self._task_monitor_uri = task_monitor_uri
        self._redfish_version = redfish_version
        self._registries = registries
        self._task = None
        self._response = response

        if (self._response and self._response.content
                and self._response.status_code == http_client.ACCEPTED):
            self._task = task.Task(self._connector, self._task_monitor_uri,
                                   redfish_version=self._redfish_version,
                                   registries=self._registries,
                                   json_doc=self._response.json())
        else:
            self.refresh()

    def refresh(self):
        """Refresh the Task

        Freshly retrieves/fetches the Task.
        :raises: ResourceNotFoundError
        :raises: ConnectionError
        :raises: HTTPError
        """
        self._response = self._connector.get(path=self.task_monitor_uri)

        if self._response.status_code == http_client.ACCEPTED:
            # A Task should have been returned, but wasn't
            if not self._response.content:
                self._task = None
                return

            # Assume that the body contains a Task since we got a 202
            if not self._task:
                self._task = task.Task(self._connector, self._task_monitor_uri,
                                       redfish_version=self._redfish_version,
                                       registries=self._registries,
                                       json_doc=self._response.json())
            else:
                self._task.refresh(json_doc=self._response.json())
        else:
            self._task = None

    @property
    def task_monitor_uri(self):
        """The TaskMonitor URI

        :returns: The TaskMonitor URI.
        """
        return self._task_monitor_uri

    @property
    def is_processing(self):
        """Indicates if the task is still processing

        :returns: A boolean indicating if the task is still processing.
        """
        return self._response.status_code == http_client.ACCEPTED

    @property
    def check_is_processing(self):
        """Refreshes task and check if it is still processing

        :returns: A boolean indicating if the task is still processing.
        """
        if not self.is_processing:
            return False

        self.refresh()

        return self.is_processing

    @property
    def sleep_for(self):
        """Seconds the client should wait before querying the operation status

        Defaults to 1 second if Retry-After not specified in response.

        :returns: The number of seconds to wait
        """
        retry_after = self._response.headers.get('Retry-After')
        if retry_after is None:
            return 1

        if isinstance(retry_after, int) or retry_after.isdigit():
            return retry_after

        return max(0, (parser.parse(retry_after)
                   - datetime.now().astimezone()).total_seconds())

    @property
    def cancellable(self):
        """The amount of time to sleep before retrying

        :returns: A Boolean indicating if the Task is cancellable.
        """
        allow = self._response.headers.get('Allow')

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

    @property
    def response(self):
        """Unprocessed response.

        Intended to be used internally.
        :returns: Unprocessed response.
        """
        return self._response

    def get_task(self):
        """Construct Task instance from task monitor URI.

        :returns: Task instance.
        """
        return task.Task(self._connector, self._task_monitor_uri,
                         redfish_version=self._redfish_version,
                         registries=self._registries)

    def wait(self, timeout_sec):
        """Waits until task is completed or it times out.

        :param timeout_sec: Timeout to wait
        :raises: ConnectionError when times out
        """
        timeout_at = time.time() + timeout_sec

        while self.check_is_processing:

            LOG.debug('Waiting for task monitor %(url)s; sleeping for '
                      '%(sleep)s seconds',
                      {'url': self.task_monitor_uri,
                       'sleep': self.sleep_for})
            time.sleep(self.sleep_for)
            if time.time() >= timeout_at and self.check_is_processing:
                m = ('Timeout waiting for task monitor %(url)s '
                     '(timeout = %(timeout)s)'
                     % {'url': self.task_monitor_uri,
                        'timeout': timeout_sec})
                raise exceptions.ConnectionError(url=self.task_monitor_uri,
                                                 error=m)

    @staticmethod
    def from_response(conn, response, target_uri, redfish_version=None,
                      registries=None):
        """Construct TaskMonitor instance from received response.

        :response: Unprocessed response
        :target_uri: URI used to initiate async operation
        :redfish_version: Redfish version. Optional when used internally.
        :registries: Redfish registries. Optional when used internally.
        :returns: TaskMonitor instance
        :raises: MissingHeaderError if Location is missing in response
        """
        json_data = response.json() if response.content else {}

        header = 'Location'
        task_monitor_uri = response.headers.get(header)
        task_uri_data = json_data.get('@odata.id')

        if task_uri_data:
            task_monitor_uri = urljoin(task_monitor_uri, task_uri_data)

        if not task_monitor_uri:
            raise exceptions.MissingHeaderError(target_uri=target_uri,
                                                header=header)

        return TaskMonitor(conn,
                           task_monitor_uri,
                           redfish_version=redfish_version,
                           registries=registries,
                           response=response)
