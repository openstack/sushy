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

from sushy.resources.system.storage import volume
from sushy.tests.unit import base


class VolumeTestCase(base.TestCase):

    def setUp(self):
        super(VolumeTestCase, self).setUp()
        self.conn = mock.Mock()
        volume_file = 'sushy/tests/unit/json_samples/volume.json'
        with open(volume_file, 'r') as f:
            self.conn.get.return_value.json.return_value = json.loads(f.read())

        self.stor_volume = volume.Volume(
            self.conn, '/redfish/v1/Systems/437XR1138R2/Storage/1/Volumes/1',
            redfish_version='1.0.2')

    def test__parse_attributes(self):
        self.stor_volume._parse_attributes()
        self.assertEqual('1.0.2', self.stor_volume.redfish_version)
        self.assertEqual('1', self.stor_volume.identity)
        self.assertEqual('Virtual Disk 1', self.stor_volume.name)
        self.assertEqual(899527000000, self.stor_volume.capacity_bytes)


class VolumeCollectionTestCase(base.TestCase):

    def setUp(self):
        super(VolumeCollectionTestCase, self).setUp()
        self.conn = mock.Mock()
        with open('sushy/tests/unit/json_samples/'
                  'volume_collection.json', 'r') as f:
            self.conn.get.return_value.json.return_value = json.loads(f.read())
        self.stor_vol_col = volume.VolumeCollection(
            self.conn, '/redfish/v1/Systems/437XR1138R2/Storage/1/Volumes',
            redfish_version='1.0.2')

    def test__parse_attributes(self):
        self.stor_vol_col._parse_attributes()
        self.assertEqual((
            '/redfish/v1/Systems/437XR1138R2/Storage/1/Volumes/1',
            '/redfish/v1/Systems/437XR1138R2/Storage/1/Volumes/2',
            '/redfish/v1/Systems/437XR1138R2/Storage/1/Volumes/3'),
            self.stor_vol_col.members_identities)

    @mock.patch.object(volume, 'Volume', autospec=True)
    def test_get_member(self, Volume_mock):
        self.stor_vol_col.get_member(
            '/redfish/v1/Systems/437XR1138R2/Storage/1/Volumes/1')
        Volume_mock.assert_called_once_with(
            self.stor_vol_col._conn,
            '/redfish/v1/Systems/437XR1138R2/Storage/1/Volumes/1',
            redfish_version=self.stor_vol_col.redfish_version)

    @mock.patch.object(volume, 'Volume', autospec=True)
    def test_get_members(self, Volume_mock):
        members = self.stor_vol_col.get_members()
        calls = [
            mock.call(self.stor_vol_col._conn,
                      '/redfish/v1/Systems/437XR1138R2/Storage/1/Volumes/1',
                      redfish_version=self.stor_vol_col.redfish_version),
            mock.call(self.stor_vol_col._conn,
                      '/redfish/v1/Systems/437XR1138R2/Storage/1/Volumes/2',
                      redfish_version=self.stor_vol_col.redfish_version),
            mock.call(self.stor_vol_col._conn,
                      '/redfish/v1/Systems/437XR1138R2/Storage/1/Volumes/3',
                      redfish_version=self.stor_vol_col.redfish_version),
        ]
        Volume_mock.assert_has_calls(calls)
        self.assertIsInstance(members, list)
        self.assertEqual(3, len(members))

    def test_max_size_bytes(self):
        self.assertIsNone(self.stor_vol_col._max_size_bytes)
        self.conn.get.return_value.json.reset_mock()

        successive_return_values = []
        with open('sushy/tests/unit/json_samples/volume.json', 'r') as f:
            successive_return_values.append(json.loads(f.read()))
        with open('sushy/tests/unit/json_samples/volume2.json', 'r') as f:
            successive_return_values.append(json.loads(f.read()))
        with open('sushy/tests/unit/json_samples/volume3.json', 'r') as f:
            successive_return_values.append(json.loads(f.read()))
        self.conn.get.return_value.json.side_effect = successive_return_values

        self.assertEqual(1073741824000, self.stor_vol_col.max_size_bytes)

        # for any subsequent fetching it gets it from the cached value
        self.conn.get.return_value.json.reset_mock()
        self.assertEqual(1073741824000, self.stor_vol_col.max_size_bytes)
        self.conn.get.return_value.json.assert_not_called()

    def test_max_size_bytes_after_refresh(self):
        self.stor_vol_col.refresh()
        self.assertIsNone(self.stor_vol_col._max_size_bytes)
        self.conn.get.return_value.json.reset_mock()

        successive_return_values = []
        with open('sushy/tests/unit/json_samples/volume.json', 'r') as f:
            successive_return_values.append(json.loads(f.read()))
        with open('sushy/tests/unit/json_samples/volume2.json', 'r') as f:
            successive_return_values.append(json.loads(f.read()))
        with open('sushy/tests/unit/json_samples/volume3.json', 'r') as f:
            successive_return_values.append(json.loads(f.read()))
        self.conn.get.return_value.json.side_effect = successive_return_values

        self.assertEqual(1073741824000, self.stor_vol_col.max_size_bytes)
