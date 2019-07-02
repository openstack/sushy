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

# This is referred from Redfish standard schema.
# https://redfish.dmtf.org/schemas/Endpoint.v1_3_0.json

import logging

from sushy.resources import base
from sushy.resources import common
from sushy.resources.fabric import mappings as fab_maps
from sushy.resources import mappings as res_maps
from sushy import utils

LOG = logging.getLogger(__name__)


class IPv4AddressField(base.CompositeField):

    address = base.Field('Address')
    """This is the IPv4 Address."""

    gateway = base.Field('Gateway')
    """This is the IPv4 gateway for this address."""

    subnet_mask = base.Field('SubnetMask')
    """This is the IPv4 Subnet mask."""

    address_origin = base.MappedField('AddressOrigin',
                                      fab_maps.ADDRESS_ORIGIN_IPv4_VALUE_MAP)
    """This indicates how the address was determined."""


class IPv6AddressField(base.CompositeField):

    address = base.Field('Address')
    """This is the IPv6 Address."""

    prefix_length = base.Field('PrefixLength', adapter=utils.int_or_none)
    """This is the IPv6 Address Prefix Length."""

    address_origin = base.MappedField('AddressOrigin',
                                      fab_maps.ADDRESS_ORIGIN_IPv6_VALUE_MAP)
    """This indicates how the address was determined."""

    address_state = base.MappedField('AddressState',
                                     fab_maps.ADDRESS_STATE_VALUE_MAP)
    """The current state of this address as defined in RFC 4862."""


class IPTransportDetailsListField(base.ListField):
    """IP transport details

    This array contains details for each IP transport supported by this
    endpoint. The array structure can be used to model multiple IP addresses
    for this endpoint.
    """

    port = base.Field('Port', adapter=utils.int_or_none)
    """The UDP or TCP port number used by the Endpoint."""

    transport_protocol = base.MappedField('TransportProtocol',
                                          res_maps.PROTOCOL_TYPE_VALUE_MAP)
    """The protocol used by the connection entity."""

    ipv4_address = IPv4AddressField('IPv4Address')
    """The IPv4 address object."""

    ipv6_address = IPv6AddressField('IPv6Address')
    """The IPv6 address object."""


class PciIdField(base.CompositeField):

    device_id = base.Field('DeviceId')
    """The Device ID of this PCIe function."""

    subsystem_id = base.Field('SubsystemId')
    """The Subsystem ID of this PCIefunction."""

    subsystem_vendor_id = base.Field('SubsystemVendorId')
    """The Subsystem Vendor ID of thisPCIe function."""

    vendor_id = base.Field('VendorId')
    """The Vendor ID of this PCIe function."""


class ConnectedEntitiesListField(base.ListField):
    """All the entities connected to this endpoint."""

    pci_class_code = base.Field('PciClassCode')
    """The Class Code, Subclass code, and Programming Interface code of
    this PCIe function."""

    pci_function_number = base.Field('PciFunctionNumber',
                                     adapter=utils.int_or_none)
    """The PCI ID of the connected entity."""

    entity_pci_id = PciIdField('EntityPciId')
    """The PCI ID of the connected entity."""

    identifiers = common.IdentifiersListField('Identifiers', default=[])
    """Identifiers for the remote entity."""

    entity_role = base.MappedField('EntityRole',
                                   fab_maps.ENTITY_ROLE_VALUE_MAP)
    """The role of the connected entity."""

    entity_type = base.MappedField('EntityType',
                                   fab_maps.ENTITY_TYPE_VALUE_MAP)
    """The type of the connected entity."""


class Endpoint(base.ResourceBase):
    """This class represents a fabric endpoint.

    It represents the properties of an entity that sends or receives protocol
    defined messages over a transport.
    """

    identity = base.Field('Id', required=True)
    """Identifier for the endpoint"""

    name = base.Field('Name', required=True)
    """The endpoint name"""

    description = base.Field('Description')
    """The endpoint description"""

    status = common.StatusField('Status')
    """The endpoint status"""

    host_reservation_memory_bytes = base.Field('HostReservationMemoryBytes',
                                               adapter=utils.int_or_none)
    """The amount of memory in Bytes that the Host should allocate to connect
    to this endpoint.
    """

    endpoint_protocol = base.MappedField('EndpointProtocol',
                                         res_maps.PROTOCOL_TYPE_VALUE_MAP)
    """The protocol supported by this endpoint."""

    pci_id = PciIdField('PciId')
    """The PCI ID of the endpoint."""

    IP_transport_details = IPTransportDetailsListField('IPTransportDetails')
    """This array contains details for each IP transport supported by this
    endpoint. The array structure can be used to model multiple IP addresses
    for this endpoint."""

    connected_entities = ConnectedEntitiesListField('ConnectedEntities')
    """All entities connected to this endpoint."""


class EndpointCollection(base.ResourceCollectionBase):
    """Represents a collection of endpoints associated with the fabric."""

    @property
    def _resource_type(self):
        return Endpoint
