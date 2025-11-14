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
        super().setUp()
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
        super().setUp()
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

    def test_get_members_expanded(self):
        # Test with expanded JSON data containing full member objects
        # This simulates a response from ?$expand=.($levels=1)
        with open('sushy/tests/unit/json_samples/'
                  'simple_storage_collection_expanded.json') as f:
            expanded_json = json.loads(f.read())

        # Create collection with the URL that would have ?$expand appended
        expanded_collection = simple_storage.SimpleStorageCollection(
            self.conn,
            "/redfish/v1/Systems/1/SimpleStorage?$expand=.($levels=1)",
            redfish_version="1.0.2",
        )
        expanded_collection._json = expanded_json

        # Mock the SimpleStorage objects that will be created
        mock_member1 = mock.Mock(spec=simple_storage.SimpleStorage)
        mock_member1.identity = "RAID-1"
        mock_member1.name = "RAID Controller"

        mock_member2 = mock.Mock(spec=simple_storage.SimpleStorage)
        mock_member2.identity = "AHCI-1"
        mock_member2.name = "AHCI Controller"

        with mock.patch.object(
            simple_storage, "SimpleStorage", autospec=True
        ) as mock_simple_storage:
            # Make the constructor return our mocked instances
            mock_simple_storage.side_effect = [mock_member1, mock_member2]

            members = expanded_collection.get_members()

            # Verify it created SimpleStorage objects from expanded data
            self.assertEqual(2, len(members))
            self.assertEqual([mock_member1, mock_member2], members)

            # Check that SimpleStorage was initialized with expanded JSON data
            self.assertEqual(2, mock_simple_storage.call_count)

            # Verify first member initialization with expanded data
            first_call = mock_simple_storage.call_args_list[0]
            self.assertEqual(expanded_collection._conn, first_call[0][0])
            self.assertEqual(
                "/redfish/v1/Systems/1/SimpleStorage/RAID-1",
                first_call[0][1],
            )
            # Check that expanded data was passed
            self.assertEqual(
                expanded_json["Members"][0], first_call[1]["json_doc"]
            )

            # Verify second member initialization with expanded data
            second_call = mock_simple_storage.call_args_list[1]
            self.assertEqual(expanded_collection._conn, second_call[0][0])
            self.assertEqual(
                "/redfish/v1/Systems/1/SimpleStorage/AHCI-1",
                second_call[0][1],
            )
            # Check that expanded data was passed
            self.assertEqual(
                expanded_json["Members"][1], second_call[1]["json_doc"]
            )

    def test_get_members_unexpanded(self):
        # Test with unexpanded JSON data containing only references
        # This simulates a normal response without ?$expand parameter
        with open('sushy/tests/unit/json_samples/'
                  'simple_storage_collection.json') as f:
            unexpanded_json = json.loads(f.read())

        # Create collection without expand in URL
        unexpanded_collection = simple_storage.SimpleStorageCollection(
            self.conn,
            "/redfish/v1/Systems/1/SimpleStorage",
            redfish_version="1.0.2",
        )
        unexpanded_collection._json = unexpanded_json

        # Mock the parent get_members method which will fetch each member
        # individually
        mock_member1 = mock.Mock(spec=simple_storage.SimpleStorage)
        mock_member2 = mock.Mock(spec=simple_storage.SimpleStorage)
        with mock.patch.object(
            simple_storage.base.ResourceCollectionBase,
            "get_members",
            autospec=True,
            return_value=[mock_member1, mock_member2],
        ) as mock_super:
            members = unexpanded_collection.get_members()

            # Should fall back to parent implementation for individual fetches
            mock_super.assert_called_once_with(unexpanded_collection)
            self.assertEqual([mock_member1, mock_member2], members)

    def test_get_members_no_json(self):
        # Test when collection has no _json attribute
        collection_no_json = simple_storage.SimpleStorageCollection(
            self.conn,
            "/redfish/v1/Systems/1/SimpleStorage",
            redfish_version="1.0.2",
        )

        # Mock the parent get_members method
        with mock.patch.object(
            simple_storage.base.ResourceCollectionBase,
            "get_members",
            autospec=True,
            return_value=["mock_member"],
        ) as mock_super:
            members = collection_no_json.get_members()

            # Should fall back to parent implementation
            mock_super.assert_called_once()
            self.assertEqual(["mock_member"], members)
