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

from sushy.resources import constants as res_cons

PROTOCOL_TYPE_VALUE_MAP = {
    'AHCI': res_cons.PROTOCOL_TYPE_AHCI,
    'FC': res_cons.PROTOCOL_TYPE_FC,
    'FCP': res_cons.PROTOCOL_TYPE_FCP,
    'FCoE': res_cons.PROTOCOL_TYPE_FCoE,
    'FICON': res_cons.PROTOCOL_TYPE_FICON,
    'FTP': res_cons.PROTOCOL_TYPE_FTP,
    'HTTP': res_cons.PROTOCOL_TYPE_HTTP,
    'HTTPS': res_cons.PROTOCOL_TYPE_HTTPS,
    'I2C': res_cons.PROTOCOL_TYPE_I2C,
    'NFSv3': res_cons.PROTOCOL_TYPE_NFSv3,
    'NFSv4': res_cons.PROTOCOL_TYPE_NFSv4,
    'NVMe': res_cons.PROTOCOL_TYPE_NVMe,
    'NVMeOverFabrics': res_cons.PROTOCOL_TYPE_NVMeOverFabrics,
    'OEM': res_cons.PROTOCOL_TYPE_OEM,
    'PCIe': res_cons.PROTOCOL_TYPE_PCIe,
    'RoCE': res_cons.PROTOCOL_TYPE_RoCE,
    'RoCEv2': res_cons.PROTOCOL_TYPE_RoCEv2,
    'SAS': res_cons.PROTOCOL_TYPE_SAS,
    'SATA': res_cons.PROTOCOL_TYPE_SATA,
    'SFTP': res_cons.PROTOCOL_TYPE_SFTP,
    'SMB': res_cons.PROTOCOL_TYPE_SMB,
    'UHCI': res_cons.PROTOCOL_TYPE_UHCI,
    'USB': res_cons.PROTOCOL_TYPE_USB,
    'iSCSI': res_cons.PROTOCOL_TYPE_iSCSI,
    'iWARP': res_cons.PROTOCOL_TYPE_iWARP,
}
