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

import mock

from sushy.resources.system.storage import drive
from sushy.resources.system.storage import storage
from sushy.tests.unit import base


STORAGE_DRIVE_FILE_NAMES = [
    'sushy/tests/unit/json_samples/drive.json',
    'sushy/tests/unit/json_samples/drive2.json',
    'sushy/tests/unit/json_samples/drive3.json'
]


class StorageTestCase(base.TestCase):

    def setUp(self):
        super(StorageTestCase, self).setUp()
        self.conn = mock.Mock()
        with open('sushy/tests/unit/json_samples/storage.json') as f:
            self.conn.get.return_value.json.return_value = json.load(f)

        self.storage = storage.Storage(
            self.conn, '/redfish/v1/Systems/437XR1138R2/Storage/1',
            redfish_version='1.0.2')

    def test__parse_attributes(self):
        self.storage._parse_attributes()
        self.assertEqual('1.0.2', self.storage.redfish_version)
        self.assertEqual('1', self.storage.identity)
        self.assertEqual('Local Storage Controller', self.storage.name)
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

    def test_drives_max_size_bytes(self):
        self.assertIsNone(self.storage._drives_max_size_bytes)
        self.conn.get.return_value.json.reset_mock()

        successive_return_values = []
        # repeating the 3rd one to provide mock data for 4th iteration.
        for fname in STORAGE_DRIVE_FILE_NAMES + [STORAGE_DRIVE_FILE_NAMES[-1]]:
            with open(fname, 'r') as f:
                successive_return_values.append(json.load(f))
        self.conn.get.return_value.json.side_effect = successive_return_values

        self.assertEqual(899527000000, self.storage.drives_max_size_bytes)

        # for any subsequent fetching it gets it from the cached value
        self.conn.get.return_value.json.reset_mock()
        self.assertEqual(899527000000, self.storage.drives_max_size_bytes)
        self.conn.get.return_value.json.assert_not_called()

    def test_drives_max_size_bytes_after_refresh(self):
        self.storage.refresh()
        self.assertIsNone(self.storage._drives_max_size_bytes)
        self.conn.get.return_value.json.reset_mock()

        successive_return_values = []
        # repeating the 3rd one to provide mock data for 4th iteration.
        for fname in STORAGE_DRIVE_FILE_NAMES + [STORAGE_DRIVE_FILE_NAMES[-1]]:
            with open(fname, 'r') as f:
                successive_return_values.append(json.load(f))
        self.conn.get.return_value.json.side_effect = successive_return_values

        self.assertEqual(899527000000, self.storage.drives_max_size_bytes)
