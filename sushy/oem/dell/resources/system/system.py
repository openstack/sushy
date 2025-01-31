# Copyright (c) 2021-2022 Dell Inc. or its subsidiaries.
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

import sushy
from sushy import exceptions
from sushy.resources.oem import base as oem_base
from sushy import utils as sushy_utils

from sushy.oem.dell.resources.system import constants as sys_cons
from sushy.oem.dell.resources.system import raid_service


def _filter_disks_not_in_mode(controller_to_disks, mode):
    """Filters disks that are not in requested mode

    :param controller_to_disks: dictionary of controllers and their drives
    :param mode: constants.PhysicalDiskStateMode
    :returns: dictionary of controllers and their drives that need mode changed
    """
    sushy_raw_device = sushy.VOLUME_TYPE_RAW_DEVICE
    for controller, drives in controller_to_disks.items():
        toprocess_drives = []
        for drive in drives:
            is_raw_device = False
            volumes = None
            try:
                volumes = drive.volumes
            except exceptions.MissingAttributeError:
                pass

            if (volumes
                and (volumes[0].volume_type == sushy_raw_device
                     or volumes[0].raid_type is None)):
                is_raw_device = True

            if (mode == sys_cons.PhysicalDiskStateMode.RAID
                    and is_raw_device
                    or mode == sys_cons.PhysicalDiskStateMode.NONRAID
                    and not is_raw_device):
                toprocess_drives.append(drive)
        controller_to_disks[controller] = toprocess_drives
    return controller_to_disks


class DellSystemExtension(oem_base.OEMResourceBase):

    @property
    @sushy_utils.cache_it
    def raid_service(self):
        """`DellRaidService` of the system"""

        path = sushy_utils.get_sub_resource_path_by(
            self, ["Links", "Oem", "Dell", "DellRaidService"],
            is_collection=False)

        return raid_service.DellRaidService(
            self._conn, path, redfish_version=self.redfish_version,
            registries=self.registries, root=self.root)

    def change_physical_disk_state(self, mode, controller_to_disks=None):
        """Converts physical disks RAID status

        Converts only those disks that are not already in requested mode.

        :param mode: constants.PhysicalDiskStateMode
        :param controller_to_disks: dictionary of controllers and their drives.
            Optional, if not provided, processes all RAID, except BOSS,
            controller drives.
        :returns: List of task monitors for each controller's disks if any
            drives need changes
        """
        if not controller_to_disks:
            controller_to_disks = self._get_controller_to_disks()

        # Do not process BOSS controllers as can't convert their disks
        boss_controllers = [c for c in controller_to_disks
                            if 'BOSS' in c.name.upper()]
        for c in boss_controllers:
            controller_to_disks.pop(c)

        controller_to_disks = _filter_disks_not_in_mode(
            controller_to_disks, mode)

        # Convert by each controller that have eligible disks
        task_monitors = []
        for controller, drives in controller_to_disks.items():
            if drives:
                drive_fqdds = [d.identity for d in drives]
                if mode == sys_cons.PhysicalDiskStateMode.RAID:
                    task_monitors.append(
                        self.raid_service.convert_to_raid(drive_fqdds))
                elif mode == sys_cons.PhysicalDiskStateMode.NONRAID:
                    task_monitors.append(
                        self.raid_service.convert_to_nonraid(drive_fqdds))

        return task_monitors

    def clear_foreign_config(self, storage_list=None):
        """Clears foreign config on given controllers

        :param storage_list: List of storage objects, each of which
            corresponds to a controller
        :returns: List of task monitors, where each entry is for a
            controller that has foreign config to clear
        """
        if storage_list is None:
            storage_list = self._get_storage_list()

        # Do not process BOSS controllers as not supporting clearing
        boss_storage = [s for s in storage_list
                        if any(c for c in s.storage_controllers
                               if 'BOSS' in c.name.upper())]
        for s in boss_storage:
            storage_list.remove(s)

        task_monitors = []
        for storage in storage_list:
            task_mon = self.raid_service.clear_foreign_config(storage.identity)
            if task_mon:
                task_monitors.append(task_mon)

        return task_monitors

    def _get_controller_to_disks(self):
        """Gets all RAID controllers and their disks on system

        :returns: dictionary of RAID controllers and their disks
        """
        controller_to_disks = {}
        for storage in self._parent_resource.storage.get_members():
            controller = (storage.storage_controllers[0]
                          if storage.storage_controllers else None)
            if not controller or controller and not controller.raid_types:
                continue
            controller_to_disks[controller] = storage.drives
        return controller_to_disks

    def _get_storage_list(self):
        """Gets all storage items corresponding to RAID controllers

        :returns: list of storage items
        """
        storage_list = []
        for storage in self._parent_resource.storage.get_members():
            controller = (storage.storage_controllers[0]
                          if storage.storage_controllers else None)
            if not controller or controller and not controller.raid_types:
                continue
            storage_list.append(storage)
        return storage_list


def get_extension(*args, **kwargs):
    return DellSystemExtension
