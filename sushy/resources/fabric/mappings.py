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

from sushy.resources.fabric import constants as fab_cons
from sushy import utils

FABRIC_TYPE_VALUE_MAP = {
    'AHCI': fab_cons.FABRIC_TYPE_AHCI,
    'FC': fab_cons.FABRIC_TYPE_FC,
    'FCP': fab_cons.FABRIC_TYPE_FCP,
    'FCoE': fab_cons.FABRIC_TYPE_FCoE,
    'FICON': fab_cons.FABRIC_TYPE_FICON,
    'FTP': fab_cons.FABRIC_TYPE_FTP,
    'HTTP': fab_cons.FABRIC_TYPE_HTTP,
    'HTTPS': fab_cons.FABRIC_TYPE_HTTPS,
    'I2C': fab_cons.FABRIC_TYPE_I2C,
    'NFSv3': fab_cons.FABRIC_TYPE_NFSv3,
    'NFSv4': fab_cons.FABRIC_TYPE_NFSv4,
    'NVMe': fab_cons.FABRIC_TYPE_NVMe,
    'NVMeOverFabrics': fab_cons.FABRIC_TYPE_NVMeOverFabrics,
    'OEM': fab_cons.FABRIC_TYPE_OEM,
    'PCIe': fab_cons.FABRIC_TYPE_PCIe,
    'RoCE': fab_cons.FABRIC_TYPE_RoCE,
    'RoCEv2': fab_cons.FABRIC_TYPE_RoCEv2,
    'SAS': fab_cons.FABRIC_TYPE_SAS,
    'SATA': fab_cons.FABRIC_TYPE_SATA,
    'SFTP': fab_cons.FABRIC_TYPE_SFTP,
    'SMB': fab_cons.FABRIC_TYPE_SMB,
    'UHCI': fab_cons.FABRIC_TYPE_UHCI,
    'USB': fab_cons.FABRIC_TYPE_USB,
    'iSCSI': fab_cons.FABRIC_TYPE_iSCSI,
    'iWARP': fab_cons.FABRIC_TYPE_iWARP,
}

FABRIC_TYPE_VALUE_MAP_REV = utils.revert_dictionary(FABRIC_TYPE_VALUE_MAP)
