# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

# This is referred from Redfish standard schema.
# https://redfish.dmtf.org/schemas/v1/Certificate.v1_4_0.json
# https://redfish.dmtf.org/schemas/v1/CertificateCollection.json

from dateutil import parser

from sushy.resources import base
from sushy.resources.certificateservice import constants as cert_cons


class Identifier(base.CompositeField):
    """The identifier information about a certificate."""

    city = base.Field('City')
    common_name = base.Field('CommonName')
    country = base.Field('Country')
    email = base.Field('Email')
    organization = base.Field('Organization')
    organizational_unit = base.Field('OrganizationalUnit')
    state = base.Field('State')


class Certificate(base.ResourceBase):

    identity = base.Field('Id', required=True)
    """The certificate identity string"""

    name = base.Field('Name')
    """The certificate name"""

    certificate_string = base.Field('CertificateString')
    """Certificate in the format defined by certificate_type"""

    certificate_type = base.MappedField('CertificateType',
                                        cert_cons.CertificateType)
    """The format of the certificate"""

    certificate_usage_type = base.MappedField('CertificateUsageType',
                                              cert_cons.CertificateUsageType)
    """The types or purposes for this certificate"""

    description = base.Field('Description')
    """Certificate description"""

    fingerprint = base.Field('Fingerprint')
    """The fingerprint of the certificate"""

    fingerprint_hash_algorithm = base.Field('FingerprintHashAlgorithm')
    """The hash algorithm for the fingerprint of the certificate"""

    issuer = Identifier('Issuer')
    """The issuer of the certificate"""

    key_usage = base.MappedListField('KeyUsage', cert_cons.KeyUsage)
    """The key usage extension, which defines the purpose of the public keys
    in this certificate"""

    serial_number = base.Field('SerialNumber')
    """The serial number of the certificate"""

    signature_algorithm = base.Field('SignatureAlgorithm')
    """The algorithm used for creating the signature of the certificate"""

    subject = Identifier('Subject')
    """The subject of the certificate"""

    uefi_signature_owner = base.Field('UefiSignatureOwner')
    """The UEFI signature owner for this certificate"""

    valid_not_after = base.Field('ValidNotAfter', adapter=parser.parse)
    """The date when the certificate is no longer valid"""

    valid_not_before = base.Field('ValidNotBefore', adapter=parser.parse)
    """The date when the certificate becomes valid"""

    # TODO(dtantsur): actions

    def delete(self):
        """Delete this certificate."""
        self._conn.delete(self._path)


# Yes, certificate collection is not the same thing as certificate locations.
# The latter is only used in CertificateService, while the former - in every
# place where certificates are supported, e.g. virtual media. For this reason
# there is no link from CertificateService to CertificateCollection.
class CertificateCollection(base.MutableResourceCollectionBase):

    _resource_type = Certificate

    def create_member(self, certificate_string, certificate_type):
        """Create a new member of this collection.

        :param certificate_string: the contents of the new certificate.
        :param certificate_type: the type of the new certificate, one of
            :py:class:`sushy.CertificateType`.
        """
        return self._create_member(dict(
            CertificateString=certificate_string,
            CertificateType=cert_cons.CertificateType(certificate_type).value,
        ))
