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
from sushy import exceptions
from sushy.resources.certificateservice import certificate
from sushy.resources.certificateservice import certificateservice
from sushy.tests.unit import base


class CertificateServiceTestCase(base.TestCase):

    def setUp(self):
        super().setUp()
        self.conn = mock.Mock()
        with open('sushy/tests/unit/json_samples'
                  '/certificateservice.json') as f:
            self.json_service = json.load(f)

        with open('sushy/tests/unit/json_samples'
                  '/certificate_locations.json') as f:
            self.json_locations = json.load(f)

        self.conn.get.return_value.json.side_effect = [
            self.json_service,
            self.json_locations,
        ]

        self.certificateservice = certificateservice.CertificateService(
            self.conn, '/redfish/v1/CertificateService',
            redfish_version='1.0.4')

    def test__parse_attributes(self):
        self.certificateservice._parse_attributes(self.json_service)

        self.assertEqual(self.certificateservice.identity,
                         'CertificateService')
        self.assertEqual(self.certificateservice.name, 'Certificate Service')
        self.assertEqual(self.certificateservice._certificate_locations_path,
                         '/redfish/v1/CertificateService/CertificateLocations')

    @mock.patch.object(certificate.Certificate, '__init__', autospec=True,
                       return_value=None)
    def test_ceritificate_locations(self, mock_cert):
        locs = self.certificateservice.certificate_locations
        self.assertEqual([
            "/redfish/v1/Managers/BMC/NetworkProtocol/HTTPS/Certificates/1"
        ], locs.members_identities)
        cert = locs.get_member(
            "/redfish/v1/Managers/BMC/NetworkProtocol/HTTPS/Certificates/1")
        self.assertIsInstance(cert, certificate.Certificate)
        mock_cert.assert_called_once_with(
            cert,
            self.conn,
            "/redfish/v1/Managers/BMC/NetworkProtocol/HTTPS/Certificates/1",
            redfish_version='1.0.4',
            registries=self.certificateservice.registries,
            root=self.certificateservice.root)

    def test_replace_certificate(self):
        loc = "/redfish/v1/Managers/BMC/NetworkProtocol/HTTPS/Certificates/1"
        self.certificateservice.replace_certificate(
            loc, 'abcd', sushy.CertificateType.PEM)
        self.conn.post.assert_called_once_with(
            "/redfish/v1/CertificateService/Actions"
            "/CertificateService.ReplaceCertificate",
            data={'CertificateUri': loc,
                  'CertificateString': 'abcd',
                  'CertificateType': 'PEM'})

    def test_replace_certificate_wrong_type(self):
        loc = "/redfish/v1/Managers/BMC/NetworkProtocol/HTTPS/Certificates/1"
        self.assertRaises(exceptions.InvalidParameterValueError,
                          self.certificateservice.replace_certificate,
                          loc, 'abcd', 'Scrum Master Certificate')
