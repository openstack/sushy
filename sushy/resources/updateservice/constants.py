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

from sushy.resources import constants as res_cons

# Transfer Protocol Type constants

UPDATE_PROTOCOL_CIFS = res_cons.PROTOCOL_TYPE_CIFS
UPDATE_PROTOCOL_FTP = res_cons.PROTOCOL_TYPE_FTP
UPDATE_PROTOCOL_SFTP = res_cons.PROTOCOL_TYPE_SFTP
UPDATE_PROTOCOL_HTTP = res_cons.PROTOCOL_TYPE_HTTP
UPDATE_PROTOCOL_HTTPS = res_cons.PROTOCOL_TYPE_HTTPS
UPDATE_PROTOCOL_SCP = res_cons.PROTOCOL_TYPE_SCP
UPDATE_PROTOCOL_TFTP = res_cons.PROTOCOL_TYPE_TFTP
UPDATE_PROTOCOL_OEM = res_cons.PROTOCOL_TYPE_OEM
UPDATE_PROTOCOL_NFS = res_cons.PROTOCOL_TYPE_NFS
