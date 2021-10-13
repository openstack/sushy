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

# AuthenticationMethod Types

AUTHENTICATION_METHOD_CHAP = 'iSCSI Challenge Handshake'\
                             'Authentication Protocol'
"""
iSCSI Challenge Handshake Authentication Protocol (CHAP)
authentication is used.
"""

AUTHENTICATION_METHOD_MUTUAL_CHAP = 'iSCSI Mutual Challenge Handshake'\
                                    'Authentication Protocol'
"""
iSCSI Mutual Challenge Handshake Authentication Protocol (CHAP)
authentication is used.
"""

AUTHENTICATION_METHOD_NONE = 'none'
"""No iSCSI authentication is used."""

# BootMode Types

BOOT_MODE_DISABLED = 'disabled'
"""Do not indicate to UEFI/BIOS that this device is bootable."""

BOOT_MODE_PXE = 'pxe'
"""Boot this device by PXE"""

# IP Address Types

IP_ADDRESS_TYPE_IPV4 = 'IPv4'
"""IPv4 addressing is used for all IP-fields in this object."""

IP_ADDRESS_TYPE_IPV6 = 'IPv6'
"""IPv6 addressing is used for all IP-fields in this object."""

# FlowControl Types

FLOW_CONTROL_NONE = 'none'
"""No IEEE 802.3x flow control is enabled on this port."""

FLOW_CONTROL_RX = 'rx'
"""IEEE 802.3x flow control may be initiated by the link partner."""

FLOW_CONTROL_TX = 'tx'
"""IEEE 802.3x flow control may be initiated by this station."""

FLOW_CONTROL_TX_RX = 'tx/rx'
"""
IEEE 802.3x flow control may be initiated
by this station or the link partner.
"""

# NetworkDeviceTechnology Types

NETWORK_DEVICE_TECHNOLOGY_DISABLED = 'disabled'
"""Neither enumerated nor visible to the operating system."""

NETWORK_DEVICE_TECHNOLOGY_ETHERNET = 'ethernet'
"""Appears to the operating system as an Ethernet device."""

NETWORK_DEVICE_TECHNOLOGY_FIBRE_CHANNEL = 'fibre channel'
"""Appears to the operating system as a Fibre Channel device."""

NETWORK_DEVICE_TECHNOLOGY_FCOE = 'fibre channel over ethernet'
"""Appears to the operating system as an FCoE device."""

NETWORK_DEVICE_TECHNOLOGY_ISCSI = 'Internet SCSI'
"""Appears to the operating system as an iSCSI device."""

# LinkStatus Types

LINK_STATUS_DOWN = 'down'
"""The port is enabled but link is down."""

LINK_STATUS_UP = 'up'
"""The port is enabled and link is good (up)."""
