# Copyright (c) 2022 Dell Inc. or its subsidiaries.
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
from sushy.resources import base
from sushy.resources.oem import base as oem_base

from sushy.oem.dell.resources.system.storage import constants as s_cons


class DellStorageController(base.CompositeField):

    controller_mode = base.MappedField('ControllerMode', s_cons.ControllerMode)
    """Mode of RAID controller"""


class DellStorageControllerExtension(oem_base.OEMResourceBase):
    dell_storage_controller = DellStorageController('DellStorageController')

    def convert_to_raid(self):
        """Converts to RAID mode if applicable

        If PERC 9 or PERC 10 controller is in non-RAID mode, then convert
        to RAID mode. No changes made for PERC 11 and above as they support
        only RAID mode, and BOSS controller as it does not have controller
        mode.
        :returns: TaskMonitor if controller mode changes applied and need to
            reboot, otherwise None
        """
        controller_mode = self.dell_storage_controller.controller_mode

        # BOSS will have this empty, PERC will have something assigned
        if controller_mode and controller_mode != s_cons.ControllerMode.RAID:
            patch = {
                "Oem": {
                    "Dell": {
                        "DellStorageController": {
                            "ControllerMode":
                                s_cons.ControllerMode.RAID.value}}}}
            return self._parent_resource.update(
                patch, apply_time=sushy.ApplyTime.ON_RESET)


def get_extension(*args, **kwargs):
    return DellStorageControllerExtension
