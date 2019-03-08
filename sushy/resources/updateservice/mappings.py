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

from sushy.resources.updateservice import constants as ups_cons
from sushy import utils


TRANSFER_PROTOCOL_TYPE_VALUE_MAP = {
    'CIFS': ups_cons.UPDATE_PROTOCOL_CIFS,
    'FTP': ups_cons.UPDATE_PROTOCOL_FTP,
    'SFTP': ups_cons.UPDATE_PROTOCOL_SFTP,
    'HTTP': ups_cons.UPDATE_PROTOCOL_HTTP,
    'HTTPS': ups_cons.UPDATE_PROTOCOL_HTTPS,
    'SCP': ups_cons.UPDATE_PROTOCOL_SCP,
    'TFTP': ups_cons.UPDATE_PROTOCOL_TFTP,
    'OEM': ups_cons.UPDATE_PROTOCOL_OEM,
    'NFS': ups_cons.UPDATE_PROTOCOL_NFS,
    'NSF': ups_cons.UPDATE_PROTOCOL_NFS
}

TRANSFER_PROTOCOL_TYPE_VALUE_MAP_REV = (
    utils.revert_dictionary(TRANSFER_PROTOCOL_TYPE_VALUE_MAP))

TRANSFER_PROTOCOL_TYPE_VALUE_MAP_REV[ups_cons.UPDATE_PROTOCOL_NFS] = 'NFS'
