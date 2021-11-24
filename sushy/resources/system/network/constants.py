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

# Values comes from the Redfish System json-schema:
# https://redfish.dmtf.org/schemas/v1/NetworkDeviceFunction.v1_7_0.json
# https://redfish.dmtf.org/schemas/v1/NetworkPort.v1_4_1.json
# Using Network prefix since some names are too generic.

import enum


class NetworkAuthenticationMethod(enum.Enum):

    NONE = 'None'
    """No iSCSI authentication is used."""

    CHAP = 'CHAP'
    """iSCSI Challenge Handshake Authentication Protocol (CHAP)
    authentication is used."""

    MUTUAL_CHAP = 'MutualCHAP'
    """iSCSI Mutual Challenge Handshake Authentication Protocol (CHAP)
    authentication is used."""


class NetworkBootMode(enum.Enum):

    DISABLED = 'Disabled'
    """Do not indicate to UEFI/BIOS that this device is bootable."""

    PXE = 'PXE'
    """Boot this device by using the embedded PXE support.  Only applicable
    if the NetDevFuncType is `Ethernet` or `InfiniBand`."""

    SCSI = 'iSCSI'
    """Boot this device by using the embedded iSCSI boot support and
    configuration.  Only applicable if the NetDevFuncType is `iSCSI` or
    `Ethernet`."""

    FIBRE_CHANNEL = 'FibreChannel'
    """Boot this device by using the embedded Fibre Channel support and
    configuration.  Only applicable if the NetDevFuncType is
    `FibreChannel`."""

    FIBRE_CHANNEL_OVER_ETHERNET = 'FibreChannelOverEthernet'
    """Boot this device by using the embedded Fibre Channel over Ethernet
    (FCoE) boot support and configuration.  Only applicable if the
    NetDevFuncType is `FibreChannelOverEthernet`."""


class IPAddressType(enum.Enum):

    IPV4 = 'IPv4'
    """IPv4 addressing is used for all IP-fields in this object."""

    IPV6 = 'IPv6'
    """IPv6 addressing is used for all IP-fields in this object."""


class FlowControl(enum.Enum):

    NONE = 'None'
    """No IEEE 802.3x flow control is enabled on this port."""

    TX = 'TX'
    """This station can initiate IEEE 802.3x flow control."""

    RX = 'RX'
    """The link partner can initiate IEEE 802.3x flow control."""

    TX_RX = 'TX_RX'
    """This station or the link partner can initiate IEEE 802.3x flow
    control."""


class NetworkDeviceTechnology(enum.Enum):

    DISABLED = 'Disabled'
    """Neither enumerated nor visible to the operating system."""

    ETHERNET = 'Ethernet'
    """Appears to the operating system as an Ethernet device."""

    FIBRE_CHANNEL = 'FibreChannel'
    """Appears to the operating system as a Fibre Channel device."""

    iSCSI = 'iSCSI'
    """Appears to the operating system as an iSCSI device."""

    FIBRE_CHANNEL_OVER_ETHERNET = 'FibreChannelOverEthernet'
    """Appears to the operating system as an FCoE device."""

    INFINI_BAND = 'InfiniBand'
    """Appears to the operating system as an InfiniBand device."""


class LinkStatus(enum.Enum):

    DOWN = 'Down'
    """The port is enabled but link is down."""

    UP = 'Up'
    """The port is enabled and link is good (up)."""

    STARTING = 'Starting'
    """This link on this interface is starting.  A physical link has been
    established, but the port is not able to transfer data."""

    TRAINING = 'Training'
    """This physical link on this interface is training."""
