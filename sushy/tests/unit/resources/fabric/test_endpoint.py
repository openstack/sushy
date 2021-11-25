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
from sushy.resources.fabric import endpoint
from sushy.tests.unit import base


class EndpointTestCase(base.TestCase):

    def setUp(self):
        super(EndpointTestCase, self).setUp()
        self.conn = mock.Mock()
        with open('sushy/tests/unit/json_samples/'
                  'endpoint.json') as f:
            self.json_doc = json.load(f)

        self.conn.get.return_value.json.return_value = self.json_doc

        self.fab_endpoint = endpoint.Endpoint(
            self.conn, '/redfish/v1/Fabrics/SAS/Endpoints/Drive1',
            redfish_version='1.0.2')

    def test__parse_atrtributes(self):
        self.fab_endpoint._parse_attributes(self.json_doc)
        self.assertEqual('Drive1', self.fab_endpoint.identity)
        self.assertEqual('SAS Drive', self.fab_endpoint.name)
        self.assertEqual(sushy.Protocol.SAS,
                         self.fab_endpoint.endpoint_protocol)
        self.assertEqual(sushy.EntityType.DRIVE,
                         self.fab_endpoint.connected_entities[0].entity_type)
        self.assertEqual(sushy.EntityRole.TARGET,
                         self.fab_endpoint.connected_entities[0].entity_role)
        con_entity = self.fab_endpoint.connected_entities[0]
        self.assertEqual(sushy.DurableNameFormat.NAA,
                         con_entity.identifiers[0].durable_name_format)
        self.assertEqual('32ADF365C6C1B7C3',
                         con_entity.identifiers[0].durable_name)
