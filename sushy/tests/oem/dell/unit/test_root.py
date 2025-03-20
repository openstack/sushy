# Copyright 2017 Red Hat, Inc.
# All Rights Reserved.
#
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

from oslotest.base import BaseTestCase
from sushy import main


class RootTestCase(BaseTestCase):

    @mock.patch('sushy.auth.SessionOrBasicAuth', autospec=True)
    @mock.patch('sushy.connector.Connector', autospec=True)
    @mock.patch('sushy.resources.sessionservice.sessionservice.'
                'SessionService', autospec=True)
    def setUp(self, mock_session_service, mock_connector, mock_auth):
        super().setUp()
        self.conn = mock.Mock()
        self.sess_serv = mock.Mock()
        self.sess_serv.create_session.return_value = (None, None)
        mock_session_service.return_value = self.sess_serv
        mock_connector.return_value = self.conn
        with open('sushy/tests/oem/dell/unit/json_samples/root.json') as f:
            self.conn.get.return_value.json.return_value = json.load(f)
        self.root = main.Sushy('http://foo.bar:1234',
                               verify=True, auth=mock_auth)

    def test_oem_vendors(self):
        self.assertEqual(['Dell'], self.root.oem_vendors)
