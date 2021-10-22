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


from sushy.resources import constants as res_cons
from sushy.resources.system import simple_storage
from sushy.tests.unit import base


class SimpleStorageTestCase(base.TestCase):

    def setUp(self):
        super(SimpleStorageTestCase, self).setUp()
        self.conn = mock.Mock()
        with open('sushy/tests/unit/json_samples/'
                  'simple_storage.json') as f:
            self.json_doc = json.load(f)

        self.conn.get.return_value.json.return_value = self.json_doc

        self.simpl_stor = simple_storage.SimpleStorage(
            self.conn, '/redfish/v1/Systems/437XR1138R2/SimpleStorage/1',
            redfish_version='1.0.2')

    def test__parse_attributes(self):
        self.simpl_stor._parse_attributes(self.json_doc)
        self.assertEqual('1.0.2', self.simpl_stor.redfish_version)
        self.assertEqual('1', self.simpl_stor.identity)
        self.assertEqual('Simple Storage Controller', self.simpl_stor.name)
        self.assertEqual(8000000000000,
                         self.simpl_stor.devices[0].capacity_bytes)
        self.assertEqual(4000000000000,
                         self.simpl_stor.devices[1].capacity_bytes)
        self.assertEqual(res_cons.State.ENABLED,
                         self.simpl_stor.devices[0].status.state)
        self.assertEqual(res_cons.State.ABSENT,
                         self.simpl_stor.devices[2].status.state)
        self.assertEqual(res_cons.Health.OK,
                         self.simpl_stor.devices[0].status.health)


class SimpleStorageCollectionTestCase(base.TestCase):

    def setUp(self):
        super(SimpleStorageCollectionTestCase, self).setUp()
        self.conn = mock.Mock()
        with open('sushy/tests/unit/json_samples/'
                  'simple_storage_collection.json') as f:

            self.json_doc = json.load(f)

        self.conn.get.return_value.json.return_value = self.json_doc

        self.simpl_stor_col = simple_storage.SimpleStorageCollection(
            self.conn, '/redfish/v1/Systems/437XR1138R2/SimpleStorage',
            redfish_version='1.0.2')

    def test__parse_attributes(self):
        self.simpl_stor_col._parse_attributes(self.json_doc)
        self.assertEqual((
            '/redfish/v1/Systems/437XR1138R2/SimpleStorage/1',),
            self.simpl_stor_col.members_identities)

    @mock.patch.object(simple_storage, 'SimpleStorage', autospec=True)
    def test_get_member(self, SimpleStorage_mock):
        self.simpl_stor_col.get_member(
            '/redfish/v1/Systems/437XR1138R2/SimpleStorage/1')
        SimpleStorage_mock.assert_called_once_with(
            self.simpl_stor_col._conn,
            '/redfish/v1/Systems/437XR1138R2/SimpleStorage/1',
            redfish_version=self.simpl_stor_col.redfish_version,
            registries=None,
            root=self.simpl_stor_col.root)

    @mock.patch.object(simple_storage, 'SimpleStorage', autospec=True)
    def test_get_members(self, SimpleStorage_mock):
        members = self.simpl_stor_col.get_members()
        SimpleStorage_mock.assert_called_once_with(
            self.simpl_stor_col._conn,
            '/redfish/v1/Systems/437XR1138R2/SimpleStorage/1',
            redfish_version=self.simpl_stor_col.redfish_version,
            registries=None, root=self.simpl_stor_col.root)
        self.assertIsInstance(members, list)
        self.assertEqual(1, len(members))

    def test_disks_sizes_bytes(self):
        self.conn.get.return_value.json.reset_mock()

        with open('sushy/tests/unit/json_samples/'
                  'simple_storage.json') as f:
            self.conn.get.return_value.json.return_value = json.load(f)

        self.assertEqual([4000000000000, 8000000000000],
                         self.simpl_stor_col.disks_sizes_bytes)

    def test_disks_sizes_bytes_capacity_bytes_none(self):
        self.conn.get.return_value.json.reset_mock()

        with open('sushy/tests/unit/json_samples/'
                  'simple_storage.json') as f:
            json_doc = json.load(f)

        json_doc['Devices'][0]['CapacityBytes'] = None
        self.conn.get.return_value.json.return_value = json_doc

        self.assertEqual([4000000000000],
                         self.simpl_stor_col.disks_sizes_bytes)

    def test_max_size_bytes(self):
        self.conn.get.return_value.json.reset_mock()

        with open('sushy/tests/unit/json_samples/'
                  'simple_storage.json') as f:
            self.conn.get.return_value.json.return_value = json.load(f)

        self.assertEqual(8000000000000, self.simpl_stor_col.max_size_bytes)

        # for any subsequent fetching it gets it from the cached value
        self.conn.get.return_value.json.reset_mock()
        self.assertEqual(8000000000000, self.simpl_stor_col.max_size_bytes)
        self.conn.get.return_value.json.assert_not_called()

    def test_max_size_bytes_after_refresh(self):
        self.simpl_stor_col.refresh()
        self.conn.get.return_value.json.reset_mock()

        with open('sushy/tests/unit/json_samples/'
                  'simple_storage.json') as f:
            self.conn.get.return_value.json.return_value = json.load(f)

        self.assertEqual(8000000000000, self.simpl_stor_col.max_size_bytes)
