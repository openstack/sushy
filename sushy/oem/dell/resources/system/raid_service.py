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

from sushy import exceptions
from sushy.resources import base
from sushy.resources import common
from sushy import taskmonitor

from sushy.oem.dell import constants

LOG = logging.getLogger(__name__)


class ActionsField(base.CompositeField):
    convert_to_raid = common.ActionField("#DellRaidService.ConvertToRAID")
    convert_to_nonraid = common.ActionField(
        "#DellRaidService.ConvertToNonRAID")
    clear_foreign_config = common.ActionField(
        "#DellRaidService.ClearForeignConfig")


class DellRaidService(base.ResourceBase):
    identity = base.Field('Id', required=True)
    _actions = ActionsField('Actions')

    def __init__(self, connector, identity, redfish_version=None,
                 registries=None, root=None):
        """A class representing a DellRaidService.

        :param connector: A Connector instance
        :param identity: The identity of the DellRaidService resource
        :param redfish_version: The version of Redfish. Used to
            construct the object according to schema of the given
            version.
        :param registries: Dict of Redfish Message Registry objects to
            be used in any resource that needs registries to parse
            messages.
        :param root: Sushy root object. Empty for Sushy root itself.
        """
        super().__init__(
            connector, identity, redfish_version=redfish_version,
            registries=registries, root=root)

    def convert_to_raid(self, physical_disk_fqdds):
        """Converts physical disks to a state usable for RAID

        :param physical_disk_fqdds: An array of FQDDs where each
            identifies a physical drive.
        :returns: Sushy's TaskMonitor instance for TaskService task
        """
        target_uri = self._actions.convert_to_raid.target_uri
        payload = {'PDArray': physical_disk_fqdds}
        response = self._conn.post(target_uri, data=payload)
        task_monitor = self._get_task_monitor_from_dell_job(response)
        LOG.info('Converting to RAID mode: %s', physical_disk_fqdds)
        return task_monitor

    def convert_to_nonraid(self, physical_disk_fqdds):
        """Converts physical disks to non-RAID state.

        :param physical_disk_fqdds: An array of FQDDs where each
            identifies a physical drive.
        :returns: Sushy's TaskMonitor instance for TaskService task
        """
        target_uri = self._actions.convert_to_nonraid.target_uri
        payload = {'PDArray': physical_disk_fqdds}
        response = self._conn.post(target_uri, data=payload)
        task_monitor = self._get_task_monitor_from_dell_job(response)
        LOG.info('Converting to non-RAID mode: %s', physical_disk_fqdds)
        return task_monitor

    def clear_foreign_config(self, controller_fqdd):
        """Clears foreign configuration

        Prepares any foreign physical disks for inclusion in the local
        configuration

        :param controller_fqdd: FQDD of controller to clear foreign
            config

        :returns: Sushy's TaskMonitor instance for TaskService task if
            there are foreign drives to clear, otherwise None.
        """
        target_uri = self._actions.clear_foreign_config.target_uri
        payload = {'TargetFQDD': controller_fqdd}

        try:
            response = self._conn.post(target_uri, data=payload)
        except exceptions.BadRequestError as ex:
            # Check if failed for no foreign drives
            errors = ex.body and ex.body.get('@Message.ExtendedInfo') or []

            no_foreign_conf = [x for x in errors if constants.NO_FOREIGN_CONFIG
                               in x.get('MessageId')]

            if len(no_foreign_conf) == 0:
                raise ex
            else:
                LOG.debug('%s: %s', no_foreign_conf[0].get('Message'),
                          controller_fqdd)
                return

        task_mon = self._get_task_monitor_from_dell_job(response)
        LOG.info('Clearing foreign config: %s', controller_fqdd)
        return task_mon

    def _get_task_monitor_from_dell_job(self, response):
        """From OEM job response returns generic Task monitor

        :param response: Response from OEM job
        :returns: Sushy's TaskMonitor instance for TaskService task
        """
        location = response.headers.get('Location')
        if not location:
            raise exceptions.ExtensionError(
                error=f'Response {response.url} does not include Location '
                      'in header')

        task_id = location.split('/')[-1]
        task = None

        for t in self.root.get_task_service().tasks.get_members():
            if t.identity == task_id:
                task = t
                break

        if not task:
            raise exceptions.ExtensionError(
                error=f"Did not find task by id {task_id}")

        return taskmonitor.TaskMonitor(
            self._conn, task.path,
            redfish_version=self.redfish_version,
            registries=self.registries)
