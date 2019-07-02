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

# Values come from the Redfish Fabric json-schema 1.0.4:
# http://redfish.dmtf.org/schemas/v1/Fabric.v1_0_4.json#/definitions/Fabric

# Address origin IPv4 constants

ADDRESS_ORIGIN_IPv4_BOOTP = 'Address is provided by a BOOTP service'
ADDRESS_ORIGIN_IPv4_DHCP = 'Address is provided by a DHCPv4 service'
ADDRESS_ORIGIN_IPv4_IPv4LINKLOCAL = 'Address valid only for this segment'
ADDRESS_ORIGIN_IPv4_STATIC = 'A static address as configured by the user'

# Address origin IPv6 constants

ADDRESS_ORIGIN_IPv6_DHCPv6 = 'Address is provided by a DHCPv6 service'
ADDRESS_ORIGIN_IPv6_LINKLOCAL = 'Address valid only for this network segment'
ADDRESS_ORIGIN_IPv6_SLAAC = 'Stateless Address Auto Configuration service'
ADDRESS_ORIGIN_IPv6_STATIC = 'A static address as configured by the user'

# Address state constants

ADDRESS_STATE_DEPRECATED = 'Deprecated'
"""This address is currently within it's valid lifetime, but is now outside of
it's preferred lifetime as defined in RFC 4862."""
ADDRESS_STATE_FAILED = 'Failed'
"""This address has failed Duplicate Address Detection testing as defined in
RFC 4862 section 5.4 and is not currently in use."""
ADDRESS_STATE_PREFERRED = 'Preferred'
"""This address is currently within both it's valid and preferred lifetimes as
defined in RFC 4862."""
ADDRESS_STATE_TENTATIVE = 'Tentative'
"""This address is currently undergoing Duplicate Address Detection testing as
defined in RFC 4862 section 5.4."""

# Entity role constants

ENTITY_ROLE_BOTH = 'The entity is acting as both an initiator and a target'
ENTITY_ROLE_INITIATOR = 'The entity is acting as an initiator'
ENTITY_ROLE_TARGET = 'The entity is acting as a target'

# Entity type constants

ENTITY_TYPE_PCI_BRIDGE = 'PCI(e) Bridge'
ENTITY_TYPE_DISPLAY_CONTROLLER = 'Display Controller'
ENTITY_TYPE_DRIVE = 'Disk Drive'
ENTITY_TYPE_NETWORK_CONTROLLER = 'Network Controller'
ENTITY_TYPE_PROCESSOR = 'Processor Device'
ENTITY_TYPE_ROOT_COMPLEX = 'Root Complex'
ENTITY_TYPE_STORAGE_EXPANDER = 'Storage Expander'
ENTITY_TYPE_STORAGE_INITIATOR = 'Storage Initiator'
ENTITY_TYPE_VOLUME = 'Volume'
