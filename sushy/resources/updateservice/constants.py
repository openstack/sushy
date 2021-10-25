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

# Values come from the Redfish UpdateService json-schema.
# https://redfish.dmtf.org/schemas/UpdateService.v1_2_2.json#/definitions/TransferProtocolType

import enum


class UpdateTransferProtocolType(enum.Enum):
    """Transfer Protocol Type constants"""

    CIFS = 'CIFS'
    """Common Internet File System (CIFS)."""

    FTP = 'FTP'
    """File Transfer Protocol (FTP)."""

    SFTP = 'SFTP'
    """Secure File Transfer Protocol (SFTP)."""

    HTTP = 'HTTP'
    """Hypertext Transfer Protocol (HTTP)."""

    HTTPS = 'HTTPS'
    """Hypertext Transfer Protocol Secure (HTTPS)."""

    SCP = 'SCP'
    """Secure Copy Protocol (SCP)."""

    TFTP = 'TFTP'
    """Trivial File Transfer Protocol (TFTP)."""

    OEM = 'OEM'
    """A manufacturer-defined protocol."""

    NFS = 'NFS'
    """Network File System (NFS)."""

    # Deprecated alias:

    NSF = 'NFS'
    """Network File System (NFS)."""


UPDATE_PROTOCOL_CIFS = UpdateTransferProtocolType.CIFS
UPDATE_PROTOCOL_FTP = UpdateTransferProtocolType.FTP
UPDATE_PROTOCOL_SFTP = UpdateTransferProtocolType.SFTP
UPDATE_PROTOCOL_HTTP = UpdateTransferProtocolType.HTTP
UPDATE_PROTOCOL_HTTPS = UpdateTransferProtocolType.HTTPS
UPDATE_PROTOCOL_SCP = UpdateTransferProtocolType.SCP
UPDATE_PROTOCOL_TFTP = UpdateTransferProtocolType.TFTP
UPDATE_PROTOCOL_OEM = UpdateTransferProtocolType.OEM
UPDATE_PROTOCOL_NFS = UpdateTransferProtocolType.NFS
