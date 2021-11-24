#    Copyright (c) 2021 Anexia Internetdienstleistungs GmbH
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

from sushy.resources.system.network import constants as net_cons

AUTHENTICATION_METHOD_TYPE_MAP = {
    'CHAP': net_cons.AUTHENTICATION_METHOD_CHAP,
    'MutualCHAP': net_cons.AUTHENTICATION_METHOD_MUTUAL_CHAP,
    'None': net_cons.AUTHENTICATION_METHOD_NONE
}

BOOT_MODE_TYPE_MAP = {
    'Disabled': net_cons.BOOT_MODE_DISABLED,
    'FibreChannel': net_cons.NETWORK_DEVICE_TECHNOLOGY_FIBRE_CHANNEL,
    'FibreChannelOverEthernet': net_cons.NETWORK_DEVICE_TECHNOLOGY_FCOE,
    'PXE': net_cons.BOOT_MODE_PXE,
    'iSCSI': net_cons.NETWORK_DEVICE_TECHNOLOGY_ISCSI
}

IP_ADDRESS_TYPE_MAP = {
    'IPv4': net_cons.IP_ADDRESS_TYPE_IPV4,
    'IPv6': net_cons.IP_ADDRESS_TYPE_IPV6,
}

LINK_STATUS_TYPE_MAP = {
    'Up': net_cons.LINK_STATUS_UP,
    'Down': net_cons.LINK_STATUS_DOWN,
}

FLOW_CONTROL_TYPE_MAP = {
    'None': net_cons.FLOW_CONTROL_NONE,
    'TX': net_cons.FLOW_CONTROL_TX,
    'RX': net_cons.FLOW_CONTROL_RX,
    'TX_RX': net_cons.FLOW_CONTROL_TX_RX,
}

NETWORK_TECHNOLOGY_TYPE_MAP = {
    'Disabled': net_cons.NETWORK_DEVICE_TECHNOLOGY_DISABLED,
    'Ethernet': net_cons.NETWORK_DEVICE_TECHNOLOGY_ETHERNET,
    'FibreChannel': net_cons.NETWORK_DEVICE_TECHNOLOGY_FIBRE_CHANNEL,
    'iSCSI': net_cons.NETWORK_DEVICE_TECHNOLOGY_ISCSI,
    'FibreChannelOverEthernet': net_cons.NETWORK_DEVICE_TECHNOLOGY_FCOE
}
