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

from sushy.resources.compositionservice import compositionservice
from sushy.resources.compositionservice import resourceblock
from sushy.resources.compositionservice import resourcezone
from sushy.resources import constants as res_cons
from sushy.tests.unit import base


class CompositionServiceTestCase(base.TestCase):

    def setUp(self):
        super(CompositionServiceTestCase, self).setUp()
        self.conn = mock.Mock()
        with open(
            'sushy/tests/unit/json_samples/compositionservice.json') as f:
            self.json_doc = json.load(f)

        self.conn.get.return_value.json.return_value = self.json_doc

        self.comp_ser = compositionservice.CompositionService(
            self.conn,
            '/redfish/v1/CompositionService',
            redfish_version='1.0.2')

    def test__parse_attributes(self):
        self.comp_ser._parse_attributes(self.json_doc)
        self.assertFalse(self.comp_ser.allow_overprovisioning)
        self.assertTrue(self.comp_ser.allow_zone_affinity)
        self.assertTrue(self.comp_ser.description, 'CompositionService1')
        self.assertEqual(
            'CompositionService',
            self.comp_ser.identity)
        self.assertEqual(
            'Composition Service',
            self.comp_ser.name)
        self.assertEqual(res_cons.STATE_ENABLED, self.comp_ser.status.state)
        self.assertEqual(res_cons.HEALTH_OK, self.comp_ser.status.health)
        self.assertTrue(self.comp_ser.service_enabled)

    @mock.patch.object(resourceblock, 'ResourceBlockCollection', autospec=True)
    def test_get_resource_blocks(self, mock_resourceblock_col):
        _ = self.comp_ser.resource_blocks
        mock_resourceblock_col.assert_called_once_with(
            self.comp_ser._conn,
            self.comp_ser._get_resource_blocks_collection_path,
            self.comp_ser.redfish_version, None)

    @mock.patch.object(resourcezone, 'ResourceZoneCollection', autospec=True)
    def test_get_resource_zones(self, mock_resourcezone_col):
        _ = self.comp_ser.resource_zones
        mock_resourcezone_col.assert_called_once_with(
            self.comp_ser._conn,
            self.comp_ser._get_resource_zones_collection_path,
            self.comp_ser.redfish_version, None)
