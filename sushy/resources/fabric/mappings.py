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

PROTOCOL_TYPE_VALUE_MAP = {
    'AHCI': fab_cons.PROTOCOL_TYPE_AHCI,
    'FC': fab_cons.PROTOCOL_TYPE_FC,
    'FCP': fab_cons.PROTOCOL_TYPE_FCP,
    'FCoE': fab_cons.PROTOCOL_TYPE_FCoE,
    'FICON': fab_cons.PROTOCOL_TYPE_FICON,
    'FTP': fab_cons.PROTOCOL_TYPE_FTP,
    'HTTP': fab_cons.PROTOCOL_TYPE_HTTP,
    'HTTPS': fab_cons.PROTOCOL_TYPE_HTTPS,
    'I2C': fab_cons.PROTOCOL_TYPE_I2C,
    'NFSv3': fab_cons.PROTOCOL_TYPE_NFSv3,
    'NFSv4': fab_cons.PROTOCOL_TYPE_NFSv4,
    'NVMe': fab_cons.PROTOCOL_TYPE_NVMe,
    'NVMeOverFabrics': fab_cons.PROTOCOL_TYPE_NVMeOverFabrics,
    'OEM': fab_cons.PROTOCOL_TYPE_OEM,
    'PCIe': fab_cons.PROTOCOL_TYPE_PCIe,
    'RoCE': fab_cons.PROTOCOL_TYPE_RoCE,
    'RoCEv2': fab_cons.PROTOCOL_TYPE_RoCEv2,
    'SAS': fab_cons.PROTOCOL_TYPE_SAS,
    'SATA': fab_cons.PROTOCOL_TYPE_SATA,
    'SFTP': fab_cons.PROTOCOL_TYPE_SFTP,
    'SMB': fab_cons.PROTOCOL_TYPE_SMB,
    'UHCI': fab_cons.PROTOCOL_TYPE_UHCI,
    'USB': fab_cons.PROTOCOL_TYPE_USB,
    'iSCSI': fab_cons.PROTOCOL_TYPE_iSCSI,
    'iWARP': fab_cons.PROTOCOL_TYPE_iWARP,
}


ADDRESS_ORIGIN_IPv4_VALUE_MAP = {
    'BOOTP': fab_cons.ADDRESS_ORIGIN_IPv4_BOOTP,
    'DHCP': fab_cons.ADDRESS_ORIGIN_IPv4_DHCP,
    'IPv4LinkLocal': fab_cons.ADDRESS_ORIGIN_IPv4_IPv4LINKLOCAL,
    'Static': fab_cons.ADDRESS_ORIGIN_IPv4_STATIC,
}


ADDRESS_ORIGIN_IPv6_VALUE_MAP = {
    'DHCPv6': fab_cons.ADDRESS_ORIGIN_IPv6_DHCPv6,
    'LinkLocal': fab_cons.ADDRESS_ORIGIN_IPv6_LINKLOCAL,
    'SLAAC': fab_cons.ADDRESS_ORIGIN_IPv6_SLAAC,
    'Static': fab_cons.ADDRESS_ORIGIN_IPv6_STATIC,
}


ADDRESS_STATE_VALUE_MAP = {
    'Deprecated': fab_cons.ADDRESS_STATE_DEPRECATED,
    'Failed': fab_cons.ADDRESS_STATE_FAILED,
    'Preferred': fab_cons.ADDRESS_STATE_PREFERRED,
    'Tentative': fab_cons.ADDRESS_STATE_TENTATIVE,
}


DUR_NAME_FORMAT_VALUE_MAP = {
    'EUI': fab_cons.DURABLE_NAME_FORMAT_EUI,
    'FC_WWN': fab_cons.DURABLE_NAME_FORMAT_FC_WWN,
    'NAA': fab_cons.DURABLE_NAME_FORMAT_NAA,
    'NQN': fab_cons.DURABLE_NAME_FORMAT_NQN,
    'NSID': fab_cons.DURABLE_NAME_FORMAT_NSID,
    'UUID': fab_cons.DURABLE_NAME_FORMAT_UUID,
    'iQN': fab_cons.DURABLE_NAME_FORMAT_iQN,
}


ENTITY_ROLE_VALUE_MAP = {
    'Both': fab_cons.ENTITY_ROLE_BOTH,
    'Initiator': fab_cons.ENTITY_ROLE_INITIATOR,
    'Target': fab_cons.ENTITY_ROLE_TARGET,
}

ENTITY_ROLE_VALUE_MAP_REV = utils.revert_dictionary(ENTITY_ROLE_VALUE_MAP)


ENTITY_TYPE_VALUE_MAP = {
    'Bridge': fab_cons.ENTITY_TYPE_PCI_BRIDGE,
    'DisplayController': fab_cons.ENTITY_TYPE_DISPLAY_CONTROLLER,
    'Drive': fab_cons.ENTITY_TYPE_DRIVE,
    'NetworkController': fab_cons.ENTITY_TYPE_NETWORK_CONTROLLER,
    'Processor': fab_cons.ENTITY_TYPE_PROCESSOR,
    'RootComplex': fab_cons.ENTITY_TYPE_ROOT_COMPLEX,
    'StorageExpander': fab_cons.ENTITY_TYPE_STORAGE_EXPANDER,
    'StorageInitiator': fab_cons.ENTITY_TYPE_STORAGE_INITIATOR,
    'Volume': fab_cons.ENTITY_TYPE_VOLUME,
}

ENTITY_TYPE_VALUE_MAP_REV = utils.revert_dictionary(ENTITY_TYPE_VALUE_MAP)
