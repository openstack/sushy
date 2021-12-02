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

import datetime
import json
from unittest import mock

import sushy
from sushy.resources.certificateservice import certificate
from sushy.tests.unit import base


class CertificateTestCase(base.TestCase):

    def setUp(self):
        super().setUp()
        self.conn = mock.Mock()
        with open('sushy/tests/unit/json_samples/certificate.json') as f:
            self.json_doc = json.load(f)

        self.conn.get.return_value.json.return_value = self.json_doc

        self.ident = \
            "/redfish/v1/Managers/BMC/NetworkProtocol/HTTPS/Certificates/1"
        self.cert = certificate.Certificate(
            self.conn, self.ident,
            redfish_version='1.0.2')

    def test__parse_attributes(self):
        self.cert._parse_attributes(self.json_doc)
        self.assertEqual('1.0.2', self.cert.redfish_version)
        self.assertEqual("HTTPS Certificate", self.cert.name)
        self.assertIn('BEGIN CERTIFICATE', self.cert.certificate_string)
        self.assertEqual(sushy.CertificateType.PEM,
                         self.cert.certificate_type)
        self.assertEqual("manager.contoso.org",
                         self.cert.issuer.common_name)
        self.assertEqual("manager.contoso.org",
                         self.cert.subject.common_name)
        self.assertEqual([sushy.KeyUsage.KEY_ENCIPHERMENT,
                          sushy.KeyUsage.SERVER_AUTHENTICATION],
                         self.cert.key_usage)
        self.assertEqual(datetime.datetime(2018, 9, 7, 13, 22, 5,
                                           tzinfo=datetime.timezone.utc),
                         self.cert.valid_not_before)
        self.assertEqual(datetime.datetime(2019, 9, 7, 13, 22, 5,
                                           tzinfo=datetime.timezone.utc),
                         self.cert.valid_not_after)
        self.assertTrue(self.cert.serial_number)
        self.assertTrue(self.cert.fingerprint)
        self.assertEqual("TPM_ALG_SHA1", self.cert.fingerprint_hash_algorithm)
        self.assertEqual("sha256WithRSAEncryption",
                         self.cert.signature_algorithm)


class CertificateCollectionTestCase(base.TestCase):

    def setUp(self):
        super().setUp()
        self.conn = mock.Mock()
        with open('sushy/tests/unit/json_samples'
                  '/certificate_collection.json') as f:
            self.json_coll = json.load(f)

        with open('sushy/tests/unit/json_samples/certificate.json') as f:
            self.json_cert = json.load(f)

        self.conn.get.return_value.json.side_effect = [self.json_coll,
                                                       self.json_cert]

        self.ident = \
            "/redfish/v1/Managers/BMC/NetworkProtocol/HTTPS/Certificates"
        self.cert_coll = certificate.CertificateCollection(
            self.conn, self.ident,
            redfish_version='1.0.2')

    def test_get_member(self):
        member = f"{self.ident}/1"
        cert = self.cert_coll.get_member(member)
        self.assertEqual("1", cert.identity)
        self.conn.get.assert_has_calls([
            mock.call(path=self.ident),
            mock.call().json(),
            mock.call(path=member),
            mock.call().json(),
        ])

    def test_delete_member(self):
        member = f"{self.ident}/1"
        self.cert_coll.delete_member(member)
        self.conn.delete.assert_called_once_with(member)

    def test_create_member(self):
        # Another loading of collection is because of a refresh
        self.conn.get.return_value.json.side_effect = [self.json_coll,
                                                       self.json_cert]

        member = f"{self.ident}/1"
        self.conn.post.return_value.headers = {'Location': member}

        result = self.cert_coll.create_member(
            certificate_string='abcd',
            certificate_type=sushy.CertificateType.PEM)
        self.assertEqual("1", result.identity)

        self.conn.get.assert_has_calls([
            mock.call(path=self.ident),
            mock.call().json(),
            mock.call(path=self.ident),
            mock.call().json(),
            mock.call(path=member),
            mock.call().json(),
        ])
        self.conn.post.assert_called_once_with(
            self.ident, data={'CertificateString': 'abcd',
                              'CertificateType': 'PEM'})

    def test_create_member_no_location(self):
        self.conn.get.return_value.json.side_effect = [self.json_coll]
        self.conn.post.return_value.headers = {}

        result = self.cert_coll.create_member(
            certificate_string='abcd',
            certificate_type=sushy.CertificateType.PEM)
        self.assertIsNone(result)

        self.conn.get.assert_has_calls([
            mock.call(path=self.ident),
            mock.call().json(),
            mock.call(path=self.ident),
            mock.call().json(),
        ])
        self.conn.post.assert_called_once_with(
            self.ident, data={'CertificateString': 'abcd',
                              'CertificateType': 'PEM'})
