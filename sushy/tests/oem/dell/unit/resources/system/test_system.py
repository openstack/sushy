# Copyright (c) 2021-2022 Dell Inc. or its subsidiaries.
#
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

import json
from unittest import mock

from oslotest.base import BaseTestCase
from sushy import exceptions

from sushy.oem.dell.resources.system import constants as sys_cons
from sushy.oem.dell.resources.system import raid_service
from sushy.oem.dell.resources.system import system as oem_system


class SystemTestCase(BaseTestCase):

    def setUp(self):
        super().setUp()
        self.conn = mock.Mock()

        with open('sushy/tests/oem/dell/unit/json_samples/'
                  'system.json') as f:
            mock_response = self.conn.get.return_value
            mock_response.json.return_value = json.load(f)
            mock_response.status_code = 200

        self.oem_system = oem_system.DellSystemExtension(
            self.conn, '/redfish/v1/Systems/System.Embedded.1')

        mock_perc_raid = mock.Mock(
            identity='Disk.Bay.0:Enclosure.Internal.0-1:RAID.Integrated.1-1')
        type(mock_perc_raid).volumes = mock.PropertyMock(
            side_effect=exceptions.MissingAttributeError)
        mock_perc_nonraid = mock.Mock(
            identity='Disk.Bay.1:Enclosure.Internal.0-1:RAID.Integrated.1-1',
            volumes=[mock.Mock(volume_type='rawdevice', raid_type=None)])

        mock_boss_controller = mock.MagicMock(raid_types=['RAID1'])
        mock_boss_controller.name = 'BOSS-S1'
        mock_boss = mock.Mock(storage_controllers=[mock_boss_controller],
                              drives=mock.Mock())
        mock_perc_controller = mock.MagicMock(raid_types=['RAID1'])
        mock_perc_controller.name = 'PERC'
        mock_perc = mock.Mock(storage_controllers=[mock_perc_controller],
                              drives=[mock_perc_raid, mock_perc_nonraid])

        mock_system = mock.Mock()
        mock_storage_nocontroller = mock.Mock(storage_controllers=[])
        mock_storage_nonraid = mock.Mock(
            storage_controllers=[mock.Mock(raid_types=[])])
        mock_storage_boss = mock_boss
        mock_storage_raid = mock_perc
        mock_system.storage.get_members.return_value = [
            mock_storage_nocontroller, mock_storage_nonraid, mock_storage_boss,
            mock_storage_raid]
        self.oem_system._parent_resource = mock_system

    def test_raid_service(self):
        with open('sushy/tests/oem/dell/unit/json_samples/'
                  'raid_service.json') as f:
            mock_response = self.conn.get.return_value
            mock_response.json.return_value = json.load(f)
            mock_response.status_code = 200
        result = self.oem_system.raid_service
        self.assertEqual(
            '/redfish/v1/Systems/System.Embedded.1/Oem/Dell/DellRaidService',
            result.path)
        self.assertIsInstance(result,
                              raid_service.DellRaidService)

    def test_change_physical_disk_state_raid(self):
        mock_taskmon = mock.Mock()
        mock_raid = mock.Mock()
        mock_raid.return_value = mock_taskmon
        mock_nonraid = mock.Mock()
        self.oem_system.raid_service.convert_to_raid = mock_raid
        self.oem_system.raid_service.convert_to_nonraid = mock_nonraid

        task_mons = self.oem_system.change_physical_disk_state(
            sys_cons.PhysicalDiskStateMode.RAID)

        self.assertEqual([mock_taskmon], task_mons)
        mock_raid.assert_called_once_with(
            ['Disk.Bay.1:Enclosure.Internal.0-1:RAID.Integrated.1-1'])
        mock_nonraid.assert_not_called()

    def test_change_physical_disk_state_nonraid(self):
        mock_taskmon = mock.Mock()
        mock_raid = mock.Mock()
        mock_nonraid = mock.Mock()
        mock_nonraid.return_value = mock_taskmon
        self.oem_system.raid_service.convert_to_raid = mock_raid
        self.oem_system.raid_service.convert_to_nonraid = mock_nonraid

        task_mons = self.oem_system.change_physical_disk_state(
            sys_cons.PhysicalDiskStateMode.NONRAID)

        self.assertEqual([mock_taskmon], task_mons)
        mock_raid.assert_not_called()
        mock_nonraid.assert_called_once_with(
            ['Disk.Bay.0:Enclosure.Internal.0-1:RAID.Integrated.1-1'])

    def test_clear_foreign_config(self):
        mock_taskmon = mock.Mock()
        mock_clear_foreign_config = mock.Mock()
        mock_clear_foreign_config.side_effect = [mock_taskmon]
        self.oem_system.raid_service.clear_foreign_config =\
            mock_clear_foreign_config

        task_mons = self.oem_system.clear_foreign_config()

        self.assertEqual([mock_taskmon], task_mons)
