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

import enum


class CertificateType(enum.Enum):
    PEM = 'PEM'
    """A Privacy Enhanced Mail (PEM)-encoded single certificate."""

    PEM_CHAIN = 'PEMchain'
    """A Privacy Enhanced Mail (PEM)-encoded certificate chain."""

    PKCS7 = 'PKCS7'
    """A Privacy Enhanced Mail (PEM)-encoded PKCS7 certificate."""


class CertificateUsageType(enum.Enum):
    USER = 'User'
    """This certificate is a user certificate like those associated with a
    manager account."""

    WEB = 'Web'
    """This certificate is a web or HTTPS certificate like those used for
    event destinations."""

    SSH = 'SSH'
    """This certificate is used for SSH."""

    DEVICE = 'Device'
    """This certificate is a device type certificate like those associated
    with SPDM and other standards."""

    PLATFORM = 'Platform'
    """This certificate is a platform type certificate like those associated
    with SPDM and other standards."""

    BIOS = 'BIOS'
    """This certificate is a BIOS certificate like those associated with
    UEFI."""


class KeyUsage(enum.Enum):
    DIGITAL_SIGNATURE = 'DigitalSignature'
    """Verifies digital signatures, other than signatures on certificates
    and CRLs."""

    NON_REPUDIATION = 'NonRepudiation'
    """Verifies digital signatures, other than signatures on certificates
    and CRLs, and provides a non-repudiation service that protects
    against the signing entity falsely denying some action."""

    KEY_ENCIPHERMENT = 'KeyEncipherment'
    """Enciphers private or secret keys."""

    DATA_ENCIPHERMENT = 'DataEncipherment'
    """Directly enciphers raw user data without an intermediate symmetric
    cipher."""

    KEY_AGREEMENT = 'KeyAgreement'
    """Key agreement."""

    KEY_CERT_SIGN = 'KeyCertSign'
    """Verifies signatures on public key certificates."""

    CRL_SIGNING = 'CRLSigning'
    """Verifies signatures on certificate revocation lists (CRLs)."""

    ENCIPHER_ONLY = 'EncipherOnly'
    """Enciphers data while performing a key agreement."""

    DECIPHER_ONLY = 'DecipherOnly'
    """Deciphers data while performing a key agreement."""

    SERVER_AUTHENTICATION = 'ServerAuthentication'
    """TLS WWW server authentication."""

    CLIENT_AUTHENTICATION = 'ClientAuthentication'
    """TLS WWW client authentication."""

    CODE_SIGNING = 'CodeSigning'
    """Signs downloadable executable code."""

    EMAIL_PROTECTION = 'EmailProtection'
    """Email protection."""

    TIMESTAMPING = 'Timestamping'
    """Binds the hash of an object to a time."""

    OCSP_SIGNING = 'OCSPSigning'
    """Signs OCSP responses."""
