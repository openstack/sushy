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
from sushy.resources.compositionservice import resourcezone
from sushy.resources import constants as res_cons
from sushy.tests.unit import base


class ResourceZoneTestCase(base.TestCase):

    def setUp(self):
        super(ResourceZoneTestCase, self).setUp()
        self.conn = mock.Mock()
        with open('sushy/tests/unit/json_samples/resourcezone.json') as f:
            self.json_doc = json.load(f)

        self.conn.get.return_value.json.return_value = self.json_doc

        self.res_zone = resourcezone.ResourceZone(
            self.conn,
            '/redfish/v1/CompositionService/ResourceZones/1',
            redfish_version='1.0.2')

    def test__parse_attributes(self):
        self.res_zone._parse_attributes(self.json_doc)
        self.assertEqual('ResourceZone1', self.res_zone.description)
        self.assertEqual('1', self.res_zone.identity)
        self.assertEqual('Resource Zone 1', self.res_zone.name)
        self.assertEqual(
            res_cons.STATE_ENABLED,
            self.res_zone.status.state)
        self.assertEqual(
            res_cons.HEALTH_OK,
            self.res_zone.status.health)
        exp_path = '/redfish/v1/CompositionService/ResourceZones/1'
        self.assertEqual(exp_path, self.res_zone.path)

    def test__parse_attributes_missing_identity(self):
        self.res_zone.json.pop('Id')
        self.assertRaisesRegex(
            exceptions.MissingAttributeError, 'attribute Id',
            self.res_zone._parse_attributes, self.json_doc)


class ResourceZoneCollectionTestCase(base.TestCase):

    def setUp(self):
        super(ResourceZoneCollectionTestCase, self).setUp()
        self.conn = mock.Mock()
        with open('sushy/tests/unit/json_samples/'
                  'resourcezone_collection.json') as f:
            self.json_doc = json.load(f)

        self.conn.get.return_value.json.return_value = self.json_doc

        self.res_zone_col = resourcezone.ResourceZoneCollection(
            self.conn, '/redfish/v1/CompositionService/ResourceZones',
            '1.0.2', None)

    def test__parse_attributes(self):
        path = '/redfish/v1/CompositionService/ResourceZones/1'
        self.res_zone_col._parse_attributes(self.json_doc)
        self.assertEqual('1.0.2', self.res_zone_col.redfish_version)
        self.assertEqual('Resource Zone Collection', self.res_zone_col.name)
        self.assertEqual((path,), self.res_zone_col.members_identities)

    @mock.patch.object(resourcezone, 'ResourceZone', autospec=True)
    def test_get_member(self, mock_resourcezone):
        path = '/redfish/v1/CompositionService/ResourceZones/1'
        self.res_zone_col.get_member(path)
        mock_resourcezone.assert_called_once_with(
            self.res_zone_col._conn, path,
            self.res_zone_col.redfish_version, None)

    @mock.patch.object(resourcezone, 'ResourceZone', autospec=True)
    def test_get_members(self, mock_resourcezone):
        path = '/redfish/v1/CompositionService/ResourceZones/1'
        members = self.res_zone_col.get_members()
        mock_resourcezone.assert_called_once_with(
            self.res_zone_col._conn, path,
            self.res_zone_col.redfish_version, None)
        self.assertIsInstance(members, list)
        self.assertEqual(1, len(members))
