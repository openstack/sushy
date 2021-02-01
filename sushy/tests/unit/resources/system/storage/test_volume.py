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

from dateutil import parser

import sushy
from sushy import exceptions
from sushy.resources import constants as res_cons
from sushy.resources.system.storage import constants as store_cons
from sushy.resources.system.storage import volume
from sushy.tests.unit import base


class VolumeTestCase(base.TestCase):

    def setUp(self):
        super(VolumeTestCase, self).setUp()
        self.conn = mock.Mock()
        with open('sushy/tests/unit/json_samples/volume.json') as f:
            self.json_doc = json.load(f)

        self.conn.get.return_value.json.return_value = self.json_doc

        self.stor_volume = volume.Volume(
            self.conn, '/redfish/v1/Systems/437XR1138R2/Storage/1/Volumes/1',
            redfish_version='1.0.2')

    def test__parse_attributes(self):
        self.stor_volume._parse_attributes(self.json_doc)
        self.assertEqual('1.0.2', self.stor_volume.redfish_version)
        self.assertEqual('1', self.stor_volume.identity)
        self.assertEqual('Virtual Disk 1', self.stor_volume.name)
        self.assertEqual(899527000000, self.stor_volume.capacity_bytes)
        self.assertEqual(sushy.VOLUME_TYPE_MIRRORED,
                         self.stor_volume.volume_type)
        self.assertFalse(self.stor_volume.encrypted)
        identifiers = self.stor_volume.identifiers
        self.assertIsInstance(identifiers, list)
        self.assertEqual(1, len(identifiers))
        identifier = identifiers[0]
        self.assertEqual(sushy.DURABLE_NAME_FORMAT_UUID,
                         identifier.durable_name_format)
        self.assertEqual('38f1818b-111e-463a-aa19-fa54f792e468',
                         identifier.durable_name)
        self.assertIsNone(self.stor_volume.block_size_bytes)

    def test_initialize_volume_immediate(self):
        target_uri = '/redfish/v1/Systems/3/Storage/RAIDIntegrated/' \
                     'Volumes/1/Actions/Volume.Initialize'
        self.stor_volume.initialize_volume(
            store_cons.VOLUME_INIT_TYPE_FAST,
            apply_time=res_cons.APPLY_TIME_IMMEDIATE)
        self.stor_volume._conn.post.assert_called_once_with(
            target_uri, data={'InitializeType': 'Fast',
                              '@Redfish.OperationApplyTime': 'Immediate'},
            blocking=True, timeout=500)

    def test_initialize_volume_on_reset(self):
        target_uri = '/redfish/v1/Systems/3/Storage/RAIDIntegrated/' \
                     'Volumes/1/Actions/Volume.Initialize'
        self.stor_volume.initialize_volume(
            store_cons.VOLUME_INIT_TYPE_FAST,
            apply_time=res_cons.APPLY_TIME_ON_RESET)
        self.stor_volume._conn.post.assert_called_once_with(
            target_uri, data={'InitializeType': 'Fast',
                              '@Redfish.OperationApplyTime': 'OnReset'},
            blocking=False, timeout=500)

    def test_initialize_volume_bad_value(self):
        self.assertRaisesRegex(
            exceptions.InvalidParameterValueError,
            'The parameter.*lazy.*invalid',
            self.stor_volume.initialize_volume, 'lazy')

    def test_delete_volume(self):
        self.stor_volume.delete_volume()
        self.stor_volume._conn.delete.assert_called_once_with(
            self.stor_volume._path, data=None, blocking=False, timeout=500)

    def test_delete_volume_with_payload(self):
        payload = {'@Redfish.OperationApplyTime': 'Immediate'}
        self.stor_volume.delete_volume(payload=payload)
        self.stor_volume._conn.delete.assert_called_once_with(
            self.stor_volume._path, data=payload, blocking=True, timeout=500)

    def test_delete_volume_immediate(self):
        payload = {}
        self.conn.delete.return_value.status_code = 200
        resource = self.stor_volume.delete_volume(
            payload=payload, apply_time=res_cons.APPLY_TIME_IMMEDIATE)
        self.stor_volume._conn.delete.assert_called_once_with(
            self.stor_volume._path, data=payload, blocking=True, timeout=500)
        self.assertIsNone(resource)

    def test_delete_volume_on_reset(self):
        payload = {}
        self.conn.delete.return_value.status_code = 202
        self.conn.delete.return_value.headers = {
            'location': '/redfish/v1/taskmon/4608f7e6',
            'retry-after': '120'
        }
        task_mon = self.stor_volume.delete_volume(
            payload=payload, apply_time=res_cons.APPLY_TIME_ON_RESET,
            timeout=250)
        self.stor_volume._conn.delete.assert_called_once_with(
            self.stor_volume._path, data=payload, blocking=False, timeout=250)
        self.assertIsNotNone(task_mon)
        self.assertEqual(task_mon.resource_name, 'task_monitor')
        self.assertEqual(task_mon.path, '/redfish/v1/taskmon/4608f7e6')


class VolumeCollectionTestCase(base.TestCase):

    def setUp(self):
        super(VolumeCollectionTestCase, self).setUp()
        self.conn = mock.Mock()
        with open('sushy/tests/unit/json_samples/'
                  'volume_collection.json') as f:
            self.json_doc = json.load(f)

        self.conn.get.return_value.json.return_value = self.json_doc

        self.stor_vol_col = volume.VolumeCollection(
            self.conn, '/redfish/v1/Systems/437XR1138R2/Storage/1/Volumes',
            redfish_version='1.0.2')
        self.stor_vol_col.refresh = mock.Mock()

    def test__parse_attributes(self):
        self.stor_vol_col._parse_attributes(self.json_doc)
        self.assertEqual((
            '/redfish/v1/Systems/437XR1138R2/Storage/1/Volumes/1',
            '/redfish/v1/Systems/437XR1138R2/Storage/1/Volumes/2',
            '/redfish/v1/Systems/437XR1138R2/Storage/1/Volumes/3'),
            self.stor_vol_col.members_identities)

    def test_operation_apply_time_support(self):
        support = self.stor_vol_col.operation_apply_time_support
        self.assertIsNotNone(support)
        self.assertEqual(600, support.maintenance_window_duration_in_seconds)
        self.assertEqual(parser.parse('2017-05-03T23:12:37-05:00'),
                         support.maintenance_window_start_time)
        self.assertEqual('/redfish/v1/Systems/437XR1138R2',
                         support._maintenance_window_resource.resource_uri)
        self.assertEqual(['Immediate', 'OnReset', 'AtMaintenanceWindowStart'],
                         support.supported_values)
        self.assertEqual([res_cons.APPLY_TIME_IMMEDIATE,
                          res_cons.APPLY_TIME_ON_RESET,
                          res_cons.APPLY_TIME_MAINT_START],
                         support.mapped_supported_values)

    @mock.patch.object(volume, 'Volume', autospec=True)
    def test_get_member(self, Volume_mock):
        self.stor_vol_col.get_member(
            '/redfish/v1/Systems/437XR1138R2/Storage/1/Volumes/1')
        Volume_mock.assert_called_once_with(
            self.stor_vol_col._conn,
            '/redfish/v1/Systems/437XR1138R2/Storage/1/Volumes/1',
            self.stor_vol_col.redfish_version, None)

    @mock.patch.object(volume, 'Volume', autospec=True)
    def test_get_members(self, Volume_mock):
        members = self.stor_vol_col.get_members()
        calls = [
            mock.call(self.stor_vol_col._conn,
                      '/redfish/v1/Systems/437XR1138R2/Storage/1/Volumes/1',
                      self.stor_vol_col.redfish_version, None),
            mock.call(self.stor_vol_col._conn,
                      '/redfish/v1/Systems/437XR1138R2/Storage/1/Volumes/2',
                      self.stor_vol_col.redfish_version, None),
            mock.call(self.stor_vol_col._conn,
                      '/redfish/v1/Systems/437XR1138R2/Storage/1/Volumes/3',
                      self.stor_vol_col.redfish_version, None),
        ]
        Volume_mock.assert_has_calls(calls)
        self.assertIsInstance(members, list)
        self.assertEqual(3, len(members))

    def test_max_size_bytes(self):
        self.conn.get.return_value.json.reset_mock()

        successive_return_values = []
        file_names = ['sushy/tests/unit/json_samples/volume.json',
                      'sushy/tests/unit/json_samples/volume2.json',
                      'sushy/tests/unit/json_samples/volume3.json']
        for file_name in file_names:
            with open(file_name) as f:
                successive_return_values.append(json.load(f))
        self.conn.get.return_value.json.side_effect = successive_return_values

        self.assertEqual(1073741824000, self.stor_vol_col.max_size_bytes)

        # for any subsequent fetching it gets it from the cached value
        self.conn.get.return_value.json.reset_mock()
        self.assertEqual(1073741824000, self.stor_vol_col.max_size_bytes)
        self.conn.get.return_value.json.assert_not_called()

    def test_max_size_bytes_after_refresh(self):
        self.stor_vol_col.refresh()
        self.conn.get.return_value.json.reset_mock()

        successive_return_values = []
        file_names = ['sushy/tests/unit/json_samples/volume.json',
                      'sushy/tests/unit/json_samples/volume2.json',
                      'sushy/tests/unit/json_samples/volume3.json']
        for file_name in file_names:
            with open(file_name) as f:
                successive_return_values.append(json.load(f))
        self.conn.get.return_value.json.side_effect = successive_return_values

        self.assertEqual(1073741824000, self.stor_vol_col.max_size_bytes)

    def test_create_volume_immediate(self):
        payload = {
            'Name': 'My Volume 4',
            'VolumeType': 'Mirrored',
            'RAIDType': 'RAID1',
            'CapacityBytes': 107374182400
        }
        expected_payload = dict(payload)
        expected_payload['@Redfish.OperationApplyTime'] = 'Immediate'
        with open('sushy/tests/unit/json_samples/volume4.json') as f:
            self.conn.get.return_value.json.return_value = json.load(f)
        self.conn.post.return_value.status_code = 201
        self.conn.post.return_value.headers.return_value = {
            'Location': '/redfish/v1/Systems/437XR1138R2/Storage/1/Volumes/4'
        }
        new_vol = self.stor_vol_col.create_volume(
            payload, apply_time=res_cons.APPLY_TIME_IMMEDIATE)
        self.stor_vol_col._conn.post.assert_called_once_with(
            '/redfish/v1/Systems/437XR1138R2/Storage/1/Volumes',
            data=expected_payload, blocking=True, timeout=500)
        self.stor_vol_col.refresh.assert_called_once()
        self.assertIsNotNone(new_vol)
        self.assertEqual('4', new_vol.identity)
        self.assertEqual('My Volume 4', new_vol.name)
        self.assertEqual(107374182400, new_vol.capacity_bytes)
        self.assertEqual(sushy.VOLUME_TYPE_MIRRORED, new_vol.volume_type)
        self.assertEqual(sushy.RAID_TYPE_RAID1, new_vol.raid_type)

    def test_create_volume_on_reset(self):
        payload = {
            'Name': 'My Volume 4',
            'VolumeType': 'Mirrored',
            'RAIDType': 'RAID1',
            'CapacityBytes': 107374182400
        }
        expected_payload = dict(payload)
        expected_payload['@Redfish.OperationApplyTime'] = 'OnReset'
        with open('sushy/tests/unit/json_samples/volume4.json') as f:
            self.conn.get.return_value.json.return_value = json.load(f)
        self.conn.post.return_value.status_code = 202
        self.conn.post.return_value.headers = {
            'Location': '/redfish/v1/taskmon/4608f7e6',
            'retry-after': '120'
        }
        task_mon = self.stor_vol_col.create_volume(
            payload, apply_time=res_cons.APPLY_TIME_ON_RESET)
        self.stor_vol_col._conn.post.assert_called_once_with(
            '/redfish/v1/Systems/437XR1138R2/Storage/1/Volumes',
            data=expected_payload, blocking=False, timeout=500)
        self.assertIsNotNone(task_mon)
        self.assertEqual(task_mon.resource_name, 'task_monitor')
        self.assertEqual(task_mon.path, '/redfish/v1/taskmon/4608f7e6')
