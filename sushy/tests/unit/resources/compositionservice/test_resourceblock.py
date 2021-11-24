# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import json
from unittest import mock

from sushy import exceptions
from sushy.resources.compositionservice import constants as res_block_cons
from sushy.resources.compositionservice import resourceblock
from sushy.resources import constants as res_cons
from sushy.tests.unit import base


class ResourceBlockTestCase(base.TestCase):

    def setUp(self):
        super(ResourceBlockTestCase, self).setUp()
        self.conn = mock.Mock()
        with open('sushy/tests/unit/json_samples/resourceblock.json') as f:
            self.json_doc = json.load(f)

        self.conn.get.return_value.json.return_value = self.json_doc

        self.res_block = resourceblock.ResourceBlock(
            self.conn,
            '/redfish/v1/CompositionService/ResourceBlocks/DriveBlock3',
            redfish_version='1.0.2')

    def test__parse_attributes(self):
        self.res_block._parse_attributes(self.json_doc)
        self.assertEqual(
            res_block_cons.CompositionState.COMPOSED,
            self.res_block.composition_status.composition_state)
        self.assertEqual(1, self.res_block.composition_status.max_compositions)
        self.assertEqual(
            0, self.res_block.composition_status.number_of_compositions)
        self.assertFalse(self.res_block.composition_status.reserved_state)
        self.assertTrue(self.res_block.composition_status.sharing_capable)
        self.assertFalse(self.res_block.composition_status.sharing_enabled)
        self.assertEqual('ResourceBlock1', self.res_block.description)
        self.assertEqual('DriveBlock3', self.res_block.identity)
        self.assertEqual('Drive Block 3', self.res_block.name)
        self.assertEqual(
            res_block_cons.ResourceBlockType.STORAGE,
            self.res_block.resource_block_type)
        self.assertEqual(
            res_cons.State.ENABLED,
            self.res_block.status.state)
        self.assertEqual(res_cons.Health.OK, self.res_block.status.health)
        exp_path = '/redfish/v1/CompositionService/ResourceBlocks/DriveBlock3'
        self.assertEqual(exp_path, self.res_block.path)

    def test__parse_attributes_missing_identity(self):
        self.res_block.json.pop('Id')
        self.assertRaisesRegex(
            exceptions.MissingAttributeError, 'attribute Id',
            self.res_block._parse_attributes, self.json_doc)


class ResourceBlockCollectionTestCase(base.TestCase):

    def setUp(self):
        super(ResourceBlockCollectionTestCase, self).setUp()
        self.conn = mock.Mock()
        with open('sushy/tests/unit/json_samples/'
                  'resourceblock_collection.json') as f:
            self.json_doc = json.load(f)

        self.conn.get.return_value.json.return_value = self.json_doc

        self.res_block_col = resourceblock.ResourceBlockCollection(
            self.conn, '/redfish/v1/CompositionService/ResourceBlocks',
            '1.0.2', None)

    def test__parse_attributes(self):
        path = '/redfish/v1/CompositionService/ResourceBlocks/ComputeBlock1'
        self.res_block_col._parse_attributes(self.json_doc)
        self.assertEqual('1.0.2', self.res_block_col.redfish_version)
        self.assertEqual(
            'Resource Block Collection',
            self.res_block_col.name)
        self.assertEqual((path,), self.res_block_col.members_identities)

    @mock.patch.object(resourceblock, 'ResourceBlock', autospec=True)
    def test_get_member(self, mock_resourceblock):
        path = '/redfish/v1/CompositionService/ResourceBlocks/ComputeBlock1'
        self.res_block_col.get_member(path)
        mock_resourceblock.assert_called_once_with(
            self.res_block_col._conn, path,
            redfish_version=self.res_block_col.redfish_version,
            registries=None, root=self.res_block_col.root)

    @mock.patch.object(resourceblock, 'ResourceBlock', autospec=True)
    def test_get_members(self, mock_resourceblock):
        path = '/redfish/v1/CompositionService/ResourceBlocks/ComputeBlock1'
        members = self.res_block_col.get_members()
        mock_resourceblock.assert_called_once_with(
            self.res_block_col._conn, path,
            redfish_version=self.res_block_col.redfish_version,
            registries=None, root=self.res_block_col.root)
        self.assertIsInstance(members, list)
        self.assertEqual(1, len(members))
