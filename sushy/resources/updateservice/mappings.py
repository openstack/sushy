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
    'Common Internet File System Protocol':
    ups_cons.TRANSFER_PROTOCOL_TYPE_CIFS,
    'File Transfer Protocol': ups_cons.TRANSFER_PROTOCOL_TYPE_FTP,
    'Secure File Transfer Protocol': ups_cons.TRANSFER_PROTOCOL_TYPE_SFTP,
    'Hypertext Transfer Protocol': ups_cons.TRANSFER_PROTOCOL_TYPE_HTTP,
    'HTTP Secure Protocol': ups_cons.TRANSFER_PROTOCOL_TYPE_HTTPS,
    'Secure File Copy Protocol': ups_cons.TRANSFER_PROTOCOL_TYPE_SCP,
    'Trivial File Transfer Protocol': ups_cons.TRANSFER_PROTOCOL_TYPE_TFTP,
    'A protocol defined by the manufacturer':
    ups_cons.TRANSFER_PROTOCOL_TYPE_OEM,
    'Network File System Protocol': ups_cons.TRANSFER_PROTOCOL_TYPE_NFS
}

TRANSFER_PROTOCOL_TYPE_VALUE_MAP_REV = (
    utils.revert_dictionary(TRANSFER_PROTOCOL_TYPE_VALUE_MAP))

TRANSFER_PROTOCOL_TYPE_VALUE_MAP[
    'Network File System Protocol'] = ups_cons.TRANSFER_PROTOCOL_TYPE_NFS
