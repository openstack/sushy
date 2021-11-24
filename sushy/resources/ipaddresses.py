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

# Values come from the Redfish json-schema:
# https://redfish.dmtf.org/schemas/v1/IPAddresses.v1_1_3.json

import enum


class AddressState(enum.Enum):
    PREFERRED = 'Preferred'
    """This address is currently within both its RFC4862-defined valid and
    preferred lifetimes."""

    DEPRECATED = 'Deprecated'
    """This address is currently within its valid lifetime but is now
    outside its RFC4862-defined preferred lifetime."""

    TENTATIVE = 'Tentative'
    """This address is currently undergoing Duplicate Address Detection
    (DAD) testing, as defined in RFC4862, section 5.4."""

    FAILED = 'Failed'
    """This address has failed Duplicate Address Detection (DAD) testing, as
    defined in RFC4862, section 5.4, and is not currently in use."""


# Backward compatibility
ADDRESS_STATE_PREFERRED = AddressState.PREFERRED
ADDRESS_STATE_DEPRECATED = AddressState.DEPRECATED
ADDRESS_STATE_TENTATIVE = AddressState.TENTATIVE
ADDRESS_STATE_FAILED = AddressState.FAILED


class IPv4AddressOrigin(enum.Enum):
    STATIC = 'Static'
    """A user-configured static address."""

    DHCP = 'DHCP'
    """A DHCPv4 service-provided address."""

    BOOTP = 'BOOTP'
    """A BOOTP service-provided address."""

    LINK_LOCAL = 'IPv4LinkLocal'
    """The address is valid for only this network segment, or link."""


# Backward compatibility
ADDRESS_ORIGIN_IPv4_BOOTP = IPv4AddressOrigin.BOOTP
ADDRESS_ORIGIN_IPv4_DHCP = IPv4AddressOrigin.DHCP
ADDRESS_ORIGIN_IPv4_IPv4LINKLOCAL = IPv4AddressOrigin.LINK_LOCAL
ADDRESS_ORIGIN_IPv4_STATIC = IPv4AddressOrigin.STATIC


class IPv6AddressOrigin(enum.Enum):
    STATIC = 'Static'
    """A static user-configured address."""

    DHCP = 'DHCPv6'
    """A DHCPv6 service-provided address."""

    LINK_LOCAL = 'LinkLocal'
    """The address is valid for only this network segment, or link."""

    SLAAC = 'SLAAC'
    """A stateless autoconfiguration (SLAAC) service-provided address."""


# Backward compatibility
ADDRESS_ORIGIN_IPv6_DHCPv6 = IPv6AddressOrigin.DHCP
ADDRESS_ORIGIN_IPv6_LINKLOCAL = IPv6AddressOrigin.LINK_LOCAL
ADDRESS_ORIGIN_IPv6_SLAAC = IPv6AddressOrigin.SLAAC
ADDRESS_ORIGIN_IPv6_STATIC = IPv6AddressOrigin.STATIC
