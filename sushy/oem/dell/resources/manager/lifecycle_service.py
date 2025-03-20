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
    remote_service_api_status = common.ActionField(
        "#DellLCService.GetRemoteServicesAPIStatus")


class DellLCService(base.ResourceBase):

    _actions = ActionsField('Actions')
    _OK_STATUS_CODE = 200
    _READY_STATUS = 'Ready'
    identity = base.Field('Id', required=True)

    def __init__(self, connector, identity, redfish_version=None,
                 registries=None):
        """A class representing a DellLCService.

        :param connector: A Connector instance
        :param identity: The identity of the DellLCService resource
        :param redfish_version: The version of Redfish. Used to construct
            the object according to schema of the given version.
        :param registries: Dict of Redfish Message Registry objects to be
            used in any resource that needs registries to parse messages.
        """
        super().__init__(
            connector, identity, redfish_version, registries)

    def _is_remote_service_api_status_ready(self, status_field):
        """Checks remote service status field

        :param status_field: Status field to check, e.g., LCStatus, RTStatus
        :returns: True if response returned and status field is Ready,
            otherwise False.
        """
        target_uri = self._actions.remote_service_api_status.target_uri
        response = self._conn.post(target_uri, data={})
        if response.status_code != self._OK_STATUS_CODE:
            return False
        data = response.json()
        return data[status_field] == self._READY_STATUS

    def is_idrac_ready(self):
        """Indicates if the iDRAC is ready to accept commands.

        :returns: A boolean value True/False based on remote service api status
            response.
        """
        LOG.debug('Checking to see if the iDRAC is ready...')
        return self._is_remote_service_api_status_ready('LCStatus')

    def is_realtime_ready(self):
        """Indicates if real-time operations are ready to be accepted.

        :returns: True if ready to accept real-time operations, otherwise
            false.
        """
        LOG.debug('Checking to see if the real-time operations are ready...')
        return self._is_remote_service_api_status_ready('RTStatus')
