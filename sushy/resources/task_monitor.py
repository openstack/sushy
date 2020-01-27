#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

# This is described in Redfish specification section "Asynchronous operations"
# www.dmtf.org/sites/default/files/standards/documents/DSP0266_1.7.0.pdf


from datetime import datetime
from datetime import timedelta
import logging

from dateutil import parser

from sushy.resources import base

LOG = logging.getLogger(__name__)


class TaskMonitor(base.ResourceBase):

    def __init__(self,
                 connector,
                 path='',
                 redfish_version=None):
        """A class representing a Redfish Task Monitor

        :param connector: A Connector instance
        :param path: sub-URI path to the resource.
        :param redfish_version: The version of Redfish. Used to construct
            the object according to schema of the given version.
        """
        super(TaskMonitor, self).__init__(connector, path, redfish_version)
        self._retry_after = None
        self._location_header = None
        self._in_progress = True
        self._response = None

    @staticmethod
    def _to_datetime(retry_after):
        if isinstance(retry_after, int) or retry_after.isdigit():
            # Retry-After: 120
            return datetime.now() + timedelta(seconds=int(retry_after))
        else:
            # Retry-After: Fri, 31 Dec 1999 23:59:59 GMT
            return parser.parse(retry_after)

    def set_retry_after(self, value):
        """Set the time the client should wait before querying the task status

        :param value: The value of the Retry-After header, which can be the
                      number of seconds to wait or an `HTTP-date` string as
                      defined by RFC 7231
        :return: The TaskMonitor object
        """
        self._retry_after = self._to_datetime(value or 1)
        return self

    @property
    def retry_after(self):
        """Time the client should wait before querying the task status

        :return: The Retry-After time in `datetime` format
        """
        return self._retry_after

    @property
    def sleep_for(self):
        """Seconds the client should wait before querying the operation status

        :return: The number of seconds to wait
        """
        return max(0, (self._retry_after - datetime.now()).total_seconds())

    @property
    def location_header(self):
        """The Location header returned from the GET on the Task Monitor

        :return: The Location header (an absolute URL)
        """
        return self._location_header

    @property
    def in_progress(self):
        """Checks the status of the async task

        :return: True if the async task is still in progress, False otherwise
        """
        if not self._in_progress:
            return False
        r = self._conn.get(self._path)
        self._response = r
        self._location_header = r.headers.get('location')
        if r.status_code == 202:
            self.set_retry_after(r.headers.get('retry-after'))
        else:
            self._in_progress = False
        return self._in_progress

    @property
    def response(self):
        """The response from the last TaskMonitor in_progress check

        :return: The `requests` response object or None
        """
        return self._response
