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


import sushy
from sushy.resources import constants as res_cons
from sushy.resources.system.storage import controller
from sushy.resources.system.storage import drive
from sushy.resources.system.storage import storage
from sushy.resources.system.storage import volume
from sushy.tests.unit import base


STORAGE_DRIVE_FILE_NAMES = [
    'sushy/tests/unit/json_samples/drive.json',
    'sushy/tests/unit/json_samples/drive2.json',
    'sushy/tests/unit/json_samples/drive3.json'
]

STORAGE_VOLUME_FILE_NAMES = [
    'sushy/tests/unit/json_samples/volume_collection.json',
    'sushy/tests/unit/json_samples/volume.json',
    'sushy/tests/unit/json_samples/volume2.json',
    'sushy/tests/unit/json_samples/volume3.json'
]


class StorageTestCase(base.TestCase):

    def setUp(self):
        super(StorageTestCase, self).setUp()
        self.conn = mock.Mock()
        with open('sushy/tests/unit/json_samples/storage.json') as f:
            self.json_doc = json.load(f)
        with open('sushy/tests/unit/json_samples/'
                  'storage_controller_collection.json') as f:
            self.json_doc_ctrl_col = json.load(f)
        with open('sushy/tests/unit/json_samples/'
                  'storage_controller.json') as f:
            self.json_doc_ctrl = json.load(f)

        self.conn.get.return_value.json.return_value = self.json_doc

        self.storage = storage.Storage(
            self.conn, '/redfish/v1/Systems/437XR1138R2/Storage/1',
            redfish_version='1.0.2')

    def test__parse_attributes(self):
        self.storage._parse_attributes(self.json_doc)
        self.assertEqual('1.0.2', self.storage.redfish_version)
        self.assertEqual('1', self.storage.identity)
        self.assertEqual('Local Storage Controller', self.storage.name)
        self.assertEqual(res_cons.Health.OK, self.storage.status.health)
        self.assertEqual(res_cons.Health.OK, self.storage.status.health_rollup)
        self.assertEqual(res_cons.State.ENABLED, self.storage.status.state)
        self.assertEqual(
            ('/redfish/v1/Systems/437XR1138R2/Storage/1/Drives/35D38F11ACEF7BD3',  # noqa
             '/redfish/v1/Systems/437XR1138R2/Storage/1/Drives/3F5A8C54207B7233',  # noqa
             '/redfish/v1/Systems/437XR1138R2/Storage/1/Drives/32ADF365C6C1B7BD',  # noqa
             '/redfish/v1/Systems/437XR1138R2/Storage/1/Drives/3D58ECBC375FD9F2',  # noqa
             ), self.storage.drives_identities)

    def test_get_drive(self):
        # | WHEN |
        actual_drive = self.storage.get_drive(
            '/redfish/v1/Systems/437XR1138R2/Storage/1/Drives/'
            '35D38F11ACEF7BD3')
        # | THEN |
        self.assertIsInstance(actual_drive, drive.Drive)
        self.assertTrue(self.conn.get.return_value.json.called)

    @mock.patch.object(drive, 'Drive', autospec=True)
    def test_drives(self, Drive_mock):
        # | WHEN |
        all_drives = self.storage.drives
        # | THEN |
        calls = [
            mock.call(self.storage._conn,
                      '/redfish/v1/Systems/437XR1138R2/Storage/1/Drives/35D38F11ACEF7BD3',  # noqa
                      redfish_version=self.storage.redfish_version,
                      registries=None, root=None),
            mock.call(self.storage._conn,
                      '/redfish/v1/Systems/437XR1138R2/Storage/1/Drives/3F5A8C54207B7233',  # noqa
                      redfish_version=self.storage.redfish_version,
                      registries=None, root=None),
            mock.call(self.storage._conn,
                      '/redfish/v1/Systems/437XR1138R2/Storage/1/Drives/32ADF365C6C1B7BD',  # noqa
                      redfish_version=self.storage.redfish_version,
                      registries=None, root=None),
            mock.call(self.storage._conn,
                      '/redfish/v1/Systems/437XR1138R2/Storage/1/Drives/3D58ECBC375FD9F2',  # noqa
                      redfish_version=self.storage.redfish_version,
                      registries=None, root=None)
        ]
        Drive_mock.assert_has_calls(calls)
        self.assertIsInstance(all_drives, list)
        self.assertEqual(4, len(all_drives))
        self.assertIsInstance(all_drives[0], drive.Drive.__class__)

        # returning cached value
        Drive_mock.reset_mock()
        # | WHEN |
        all_drives = self.storage.drives
        # | THEN |
        self.assertFalse(Drive_mock.called)
        self.assertIsInstance(all_drives, list)
        self.assertEqual(4, len(all_drives))
        self.assertIsInstance(all_drives[0], drive.Drive.__class__)

    def test_storage_controllers(self):
        controllers = self.storage.storage_controllers
        self.assertIsInstance(controllers, list)
        self.assertEqual(1, len(controllers))
        controller = controllers[0]
        self.assertEqual('0', controller.member_id)
        self.assertEqual('Contoso Integrated RAID', controller.name)
        self.assertEqual(res_cons.Health.OK, controller.status.health)
        self.assertEqual(res_cons.State.ENABLED, controller.status.state)
        identifiers = controller.identifiers
        self.assertIsInstance(identifiers, list)
        self.assertEqual(1, len(identifiers))
        identifier = identifiers[0]
        self.assertEqual(sushy.DurableNameFormat.NAA,
                         identifier.durable_name_format)
        self.assertEqual('345C59DBD970859C', identifier.durable_name)
        self.assertEqual(12, controller.speed_gbps)
        self.assertEqual([sushy.Protocol.PCIe],
                         controller.controller_protocols)
        self.assertEqual([sushy.Protocol.SAS, sushy.Protocol.SATA],
                         controller.device_protocols)
        self.assertEqual([sushy.RAIDType.RAID0, sushy.RAIDType.RAID1],
                         controller.raid_types)

    def test_controllers(self):
        self.conn.get.return_value.json.side_effect = [
            self.json_doc_ctrl_col,
            self.json_doc_ctrl]
        controllers = self.storage.controllers
        self.assertIsInstance(controllers, controller.ControllerCollection)
        self.assertEqual(1, len(controllers.get_members()))
        controller1 = controllers.get_members()[0]
        self.assertEqual('1', controller1.identity)

    def test_drives_after_refresh(self):
        self.storage.refresh()
        self.conn.get.return_value.json.reset_mock()

        successive_return_values = []
        # repeating the 3rd one to provide mock data for 4th iteration.
        for fname in STORAGE_DRIVE_FILE_NAMES + [STORAGE_DRIVE_FILE_NAMES[-1]]:
            with open(fname) as f:
                successive_return_values.append(json.load(f))
        self.conn.get.return_value.json.side_effect = successive_return_values

        all_drives = self.storage.drives
        self.assertIsInstance(all_drives, list)
        self.assertEqual(4, len(all_drives))
        for drv in all_drives:
            self.assertIsInstance(drv, drive.Drive)

    def test_drives_max_size_bytes(self):
        self.conn.get.return_value.json.reset_mock()

        successive_return_values = []
        # repeating the 3rd one to provide mock data for 4th iteration.
        for fname in STORAGE_DRIVE_FILE_NAMES + [STORAGE_DRIVE_FILE_NAMES[-1]]:
            with open(fname) as f:
                successive_return_values.append(json.load(f))
        self.conn.get.return_value.json.side_effect = successive_return_values

        self.assertEqual(899527000000, self.storage.drives_max_size_bytes)

        # for any subsequent fetching it gets it from the cached value
        self.conn.get.return_value.json.reset_mock()
        self.assertEqual(899527000000, self.storage.drives_max_size_bytes)
        self.conn.get.return_value.json.assert_not_called()

    def test_drives_max_size_bytes_after_refresh(self):
        self.storage.refresh()
        self.conn.get.return_value.json.reset_mock()

        successive_return_values = []
        # repeating the 3rd one to provide mock data for 4th iteration.
        for fname in STORAGE_DRIVE_FILE_NAMES + [STORAGE_DRIVE_FILE_NAMES[-1]]:
            with open(fname) as f:
                successive_return_values.append(json.load(f))
        self.conn.get.return_value.json.side_effect = successive_return_values

        self.assertEqual(899527000000, self.storage.drives_max_size_bytes)

    def test_volumes(self):
        # | GIVEN |
        self.conn.get.return_value.json.reset_mock()
        with open('sushy/tests/unit/json_samples/volume_collection.json') as f:
            self.conn.get.return_value.json.return_value = json.load(f)
        # | WHEN |
        actual_volumes = self.storage.volumes
        # | THEN |
        self.assertIsInstance(actual_volumes,
                              volume.VolumeCollection)
        self.conn.get.return_value.json.assert_called_once_with()

    def test_volumes_cached(self):
        # | GIVEN |
        self.conn.get.return_value.json.reset_mock()
        with open('sushy/tests/unit/json_samples/volume_collection.json') as f:
            self.conn.get.return_value.json.return_value = json.load(f)
        # invoke it once
        actual_volumes = self.storage.volumes
        self.conn.get.return_value.json.reset_mock()
        # | WHEN & THEN |
        # tests for same object on invoking subsequently
        self.assertIs(actual_volumes,
                      self.storage.volumes)
        self.conn.get.return_value.json.assert_not_called()

    def test_volumes_on_refresh(self):
        # | GIVEN |
        with open('sushy/tests/unit/json_samples/volume_collection.json') as f:
            self.conn.get.return_value.json.return_value = json.load(f)
        # | WHEN & THEN |
        vols = self.storage.volumes
        self.assertIsInstance(vols, volume.VolumeCollection)

        # On refreshing the system instance...
        with open('sushy/tests/unit/json_samples/storage.json') as f:
            self.conn.get.return_value.json.return_value = json.load(f)

        self.storage.invalidate()
        self.storage.refresh(force=False)

        # | WHEN & THEN |
        self.assertTrue(vols._is_stale)

        # | GIVEN |
        with open('sushy/tests/unit/json_samples/volume_collection.json') as f:
            self.conn.get.return_value.json.return_value = json.load(f)
        # | WHEN & THEN |
        self.assertIsInstance(self.storage.volumes,
                              volume.VolumeCollection)


class StorageCollectionTestCase(base.TestCase):

    def setUp(self):
        super(StorageCollectionTestCase, self).setUp()
        self.conn = mock.Mock()
        with open('sushy/tests/unit/json_samples/'
                  'storage_collection.json') as f:
            self.json_doc = json.load(f)

        self.conn.get.return_value.json.return_value = self.json_doc

        self.stor_col = storage.StorageCollection(
            self.conn, '/redfish/v1/Systems/437XR1138R2/Storage',
            redfish_version='1.0.2')

    def test__parse_attributes(self):
        self.stor_col._parse_attributes(self.json_doc)
        self.assertEqual((
            '/redfish/v1/Systems/437XR1138R2/Storage/1',),
            self.stor_col.members_identities)

    @mock.patch.object(storage, 'Storage', autospec=True)
    def test_get_member(self, Storage_mock):
        self.stor_col.get_member(
            '/redfish/v1/Systems/437XR1138R2/Storage/1')
        Storage_mock.assert_called_once_with(
            self.stor_col._conn,
            '/redfish/v1/Systems/437XR1138R2/Storage/1',
            redfish_version=self.stor_col.redfish_version, registries=None,
            root=self.stor_col.root)

    @mock.patch.object(storage, 'Storage', autospec=True)
    def test_get_members(self, Storage_mock):
        members = self.stor_col.get_members()
        Storage_mock.assert_called_once_with(
            self.stor_col._conn,
            '/redfish/v1/Systems/437XR1138R2/Storage/1',
            redfish_version=self.stor_col.redfish_version, registries=None,
            root=self.stor_col.root)
        self.assertIsInstance(members, list)
        self.assertEqual(1, len(members))

    def test_drives_sizes_bytes(self):
        self.conn.get.return_value.json.reset_mock()

        successive_return_values = []
        with open('sushy/tests/unit/json_samples/storage.json') as f:
            successive_return_values.append(json.load(f))
        # repeating the 3rd one to provide mock data for 4th iteration.
        for fname in STORAGE_DRIVE_FILE_NAMES + [STORAGE_DRIVE_FILE_NAMES[-1]]:
            with open(fname) as f:
                successive_return_values.append(json.load(f))
        self.conn.get.return_value.json.side_effect = successive_return_values

        self.assertEqual([899527000000, 899527000000, 899527000000,
                          899527000000], self.stor_col.drives_sizes_bytes)

    def test_max_drive_size_bytes(self):
        self.conn.get.return_value.json.reset_mock()

        successive_return_values = []
        with open('sushy/tests/unit/json_samples/storage.json') as f:
            successive_return_values.append(json.load(f))
        # repeating the 3rd one to provide mock data for 4th iteration.
        for fname in STORAGE_DRIVE_FILE_NAMES + [STORAGE_DRIVE_FILE_NAMES[-1]]:
            with open(fname) as f:
                successive_return_values.append(json.load(f))
        self.conn.get.return_value.json.side_effect = successive_return_values

        self.assertEqual(899527000000, self.stor_col.max_drive_size_bytes)

        # for any subsequent fetching it gets it from the cached value
        self.conn.get.return_value.json.reset_mock()
        self.assertEqual(899527000000, self.stor_col.max_drive_size_bytes)
        self.conn.get.return_value.json.assert_not_called()

    def test_max_drive_size_bytes_after_refresh(self):
        self.stor_col.refresh(force=False)
        self.conn.get.return_value.json.reset_mock()

        successive_return_values = []
        with open('sushy/tests/unit/json_samples/storage.json') as f:
            successive_return_values.append(json.load(f))
        # repeating the 3rd one to provide mock data for 4th iteration.
        for fname in STORAGE_DRIVE_FILE_NAMES + [STORAGE_DRIVE_FILE_NAMES[-1]]:
            with open(fname) as f:
                successive_return_values.append(json.load(f))
        self.conn.get.return_value.json.side_effect = successive_return_values

        self.assertEqual(899527000000, self.stor_col.max_drive_size_bytes)

    def test_volumes_sizes_bytes(self):
        self.conn.get.return_value.json.reset_mock()

        successive_return_values = []
        with open('sushy/tests/unit/json_samples/storage.json') as f:
            successive_return_values.append(json.load(f))
        # repeating the 3rd one to provide mock data for 4th iteration.
        for fname in STORAGE_VOLUME_FILE_NAMES:
            with open(fname) as f:
                successive_return_values.append(json.load(f))
        self.conn.get.return_value.json.side_effect = successive_return_values

        self.assertEqual([107374182400, 899527000000, 1073741824000],
                         self.stor_col.volumes_sizes_bytes)

    def test_max_volume_size_bytes(self):
        self.conn.get.return_value.json.reset_mock()

        successive_return_values = []
        with open('sushy/tests/unit/json_samples/storage.json') as f:
            successive_return_values.append(json.load(f))
        # repeating the 3rd one to provide mock data for 4th iteration.
        for fname in STORAGE_VOLUME_FILE_NAMES:
            with open(fname) as f:
                successive_return_values.append(json.load(f))
        self.conn.get.return_value.json.side_effect = successive_return_values

        self.assertEqual(1073741824000, self.stor_col.max_volume_size_bytes)

        # for any subsequent fetching it gets it from the cached value
        self.conn.get.return_value.json.reset_mock()
        self.assertEqual(1073741824000, self.stor_col.max_volume_size_bytes)
        self.conn.get.return_value.json.assert_not_called()

    def test_max_volume_size_bytes_after_refresh(self):
        self.stor_col.refresh(force=False)
        self.conn.get.return_value.json.reset_mock()

        successive_return_values = []
        with open('sushy/tests/unit/json_samples/storage.json') as f:
            successive_return_values.append(json.load(f))
        # repeating the 3rd one to provide mock data for 4th iteration.
        for fname in STORAGE_VOLUME_FILE_NAMES:
            with open(fname) as f:
                successive_return_values.append(json.load(f))
        self.conn.get.return_value.json.side_effect = successive_return_values

        self.assertEqual(1073741824000, self.stor_col.max_volume_size_bytes)
