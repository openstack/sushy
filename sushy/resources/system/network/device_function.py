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

# This is referred from Redfish standard schema.
# https://redfish.dmtf.org/schemas/v1/NetworkDeviceFunction.v1_3_3.json

from sushy.resources import base
from sushy.resources import common
from sushy.resources.system.network import constants
from sushy.resources.system.network import port
from sushy import utils


class BootTargetsField(base.ListField):
    lun_id = base.Field("LUNID")
    """The logical unit number (LUN) ID from which to boot on the device"""

    priority = base.Field("BootPriority", adapter=utils.int_or_none)
    """The relative priority for this entry in the boot targets array."""

    wwpn = base.Field("WWPN")
    """The World Wide Port Name (WWPN) from which to boot."""


class VLANField(base.CompositeField):
    vlan_enabled = base.Field("VLANEnable", adapter=utils.bool_or_none)
    vlan_id = base.Field("VLANId", adapter=utils.int_or_none)


class ISCSIBootField(base.CompositeField):
    authentication_method = base.MappedField(
        'AuthenticationMethod', constants.NetworkAuthenticationMethod)
    """The configured capability of this network device function."""

    initiator_default_gateway = base.Field('InitiatorDefaultGateway')
    """The IPv6 or IPv4 iSCSI boot default gateway."""

    initiator_ip_address = base.Field('InitiatorIPAddress')
    """The IPv6 or IPv4 address of the iSCSI initiator."""

    initiator_netmask = base.Field('InitiatorNetmask')
    """The IPv6 or IPv4 netmask of the iSCSI boot initiator."""

    ip_address_type = base.MappedField(
        'IPAddressType', constants.IPAddressType)
    """The type of IP address being populated IP address fields."""

    primary_dns = base.Field('PrimaryDNS')
    """The IPv6 or IPv4 address of the primary DNS server."""

    primary_lun = base.Field('PrimaryLUN', adapter=utils.int_or_none)
    """The logical unit number (LUN) for the primary iSCSI boot target."""

    primary_target_ip_address = base.Field('PrimaryTargetIPAddress')
    """The IPv4 or IPv6 address for the primary iSCSI boot target."""

    primary_target_tcp_port = base.Field('PrimaryTargetTCPPort')
    """The TCP port for the primary iSCSI boot target."""

    primary_vlan_enabled = base.Field(
        'PrimaryVLANEnable',
        adapter=utils.bool_or_none
    )
    """An indication of whether the primary VLAN is enabled."""

    primary_vlan_id = base.Field("PrimaryVLANId", adapter=utils.int_or_none)
    """The 802.1q VLAN ID to use for iSCSI boot from the primary target."""

    secondary_dns = base.Field('SecondaryDNS')
    """The IPv6 or IPv4 address of the secondary DNS server."""

    secondary_lun = base.Field('SecondaryLUN', adapter=utils.int_or_none)
    """The logical unit number (LUN) for the secondary iSCSI boot target."""

    secondary_target_ip_address = base.Field('SecondaryTargetIPAddress')
    """The IPv4 or IPv6 address for the secondary iSCSI boot target."""

    secondary_target_tcp_port = base.Field('SecondaryTargetTCPPort')
    """The TCP port for the secondary iSCSI boot target."""

    secondary_vlan_enabled = base.Field(
        'SecondaryVLANEnable', adapter=utils.bool_or_none)
    """An indication of whether the secondary VLAN is enabled."""

    secondary_vlan_id = base.Field(
        "SecondaryVLANId",
        adapter=utils.int_or_none
    )
    """The 802.1q VLAN ID to use for iSCSI boot from the secondary target."""


class EthernetField(base.CompositeField):
    mac_address = base.Field("MACAddress")
    """The currently configured MAC address of the resource"""

    mtu_size = base.Field("MTUSize", adapter=utils.int_or_none)
    """The Maximum Transmission Unit (MTU) configured for this resource"""

    permanent_mac_address = base.Field("PermanentMACAddress")
    """The permanent MAC address assigned to this resource"""

    vlan = VLANField("VLAN")
    """The VLAN for this interface"""


class FibreChannelField(base.CompositeField):
    boot_targets = BootTargetsField("BootTargets")
    """An array of Fibre Channel boot targets configured for this resource."""


class NetworkDeviceFunction(base.ResourceBase):
    capabilities = base.MappedListField(
        'NetDevFuncCapabilities', constants.NetworkDeviceTechnology)
    """An array of capabilities for this network device function."""

    type = base.MappedField(
        'NetDevFuncType', constants.NetworkDeviceTechnology)
    """The configured capability of this network device function."""

    description = base.Field('Description')
    """The network device function description"""

    ethernet = EthernetField("Ethernet")
    """The Ethernet capabilities, status, and configuration values."""

    fibre_channel = FibreChannelField("FibreChannel")
    """The Fibre Channel capabilities, status, and configuration values."""

    identity = base.Field('Id', required=True)
    """Identifier for the network device function"""

    iscsi_boot = ISCSIBootField('iSCSIBoot')
    """
    The iSCSI boot capabilities, status, and configuration
    for a network device function.
    """

    max_virtual_functions = base.Field(
        'MaxVirtualFunctions',
        adapter=utils.int_or_none
    )
    """
    The number of virtual functions that are available
    for this network device function.
    """

    name = base.Field('Name', required=True)
    """The network device function name"""

    status = common.StatusField('Status')
    """The status of the resource"""

    @property
    @utils.cache_it
    def assignable_physical_ports(self):
        """An array of physical ports to which this resource may be assigned.

        Network ports to which this network device function may be assigned.

        :raises: MissingAttributeError if '@odata.id' field is missing.
        :returns: A list of `NetworkPort` instances
        """
        paths = utils.get_sub_resource_path_by(
            self, "AssignablePhysicalPorts", is_collection=True)

        return [port.NetworkPort(self._conn, path,
                                 redfish_version=self.redfish_version,
                                 registries=self.registries,
                                 root=self.root
                                 )
                for path in paths]


class NetworkDeviceFunctionCollection(base.ResourceCollectionBase):

    @property
    def _resource_type(self):
        return NetworkDeviceFunction
