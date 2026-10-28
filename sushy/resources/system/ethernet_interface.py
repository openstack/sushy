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
# https://redfish.dmtf.org/schemas/EthernetInterface.v1_12_5.json

import logging

from sushy.resources import base
from sushy.resources import common
from sushy.resources import constants as res_cons
from sushy.resources import ipaddresses as ip_cons
from sushy import utils

LOG = logging.getLogger(__name__)


class IPv4AddressField(base.ListField):
    address = base.Field('Address')
    subnet_mask = base.Field('SubnetMask')
    gateway = base.Field('Gateway')
    address_origin = base.MappedField('AddressOrigin',
                                      ip_cons.IPv4AddressOrigin)


class IPv6AddressField(base.ListField):
    address = base.Field('Address')
    prefix_length = base.Field('PrefixLength')
    address_origin = base.MappedField('AddressOrigin',
                                      ip_cons.IPv6AddressOrigin)
    address_state = base.MappedField('AddressState',
                                     ip_cons.AddressState)


class IPv4StaticAddressField(base.ListField):
    address = base.Field('Address')
    subnet_mask = base.Field('SubnetMask')
    gateway = base.Field('Gateway')


class IPv6StaticAddressField(base.ListField):
    address = base.Field('Address')
    prefix_length = base.Field('PrefixLength')


class IPv6StaticDefaultGatewayField(base.ListField):
    address = base.Field('Address')
    prefix_length = base.Field('PrefixLength')


class DHCPv4ConfigurationField(base.CompositeField):
    dhcp_enabled = base.Field('DHCPEnabled')
    use_dns_servers = base.Field('UseDNSServers')
    use_domain_name = base.Field('UseDomainName')
    use_gateway = base.Field('UseGateway')
    use_ntp_servers = base.Field('UseNTPServers')
    use_static_routes = base.Field('UseStaticRoutes')
    fallback_address = base.MappedField('FallbackAddress',
                                        ip_cons.DHCPFallback)


class DHCPv6ConfigurationField(base.CompositeField):
    operating_mode = base.MappedField('OperatingMode',
                                      ip_cons.DHCPv6OperatingMode)
    use_dns_servers = base.Field('UseDNSServers')
    use_domain_name = base.Field('UseDomainName')
    use_ntp_servers = base.Field('UseNTPServers')
    use_rapid_commit = base.Field('UseRapidCommit')


class EthernetInterface(base.ResourceBase):
    """This class adds the EthernetInterface resource"""

    identity = base.Field('Id')
    """The Ethernet Interface identity string"""

    name = base.Field('Name')
    """The name of the resource or array element"""

    description = base.Field('Description')
    """Description"""

    permanent_mac_address = base.Field('PermanentMACAddress')
    """This is the permanent MAC address assigned to this interface (port) """

    mac_address = base.Field('MACAddress')
    """This is the currently configured MAC address of the interface."""

    speed_mbps = base.Field('SpeedMbps')
    """This is the current speed in Mbps of this interface."""

    auto_neg = base.Field('AutoNeg')
    """Whether the speed and duplex are automatically negotiated."""

    full_duplex = base.Field('FullDuplex')
    """Whether full-duplex mode is enabled on this interface."""

    mtu_size = base.Field('MTUSize')
    """The currently configured maximum transmission unit (MTU)."""

    interface_enabled = base.Field('InterfaceEnabled')
    """Whether this interface is enabled."""

    host_name = base.Field('HostName')
    """The DNS host name without the domain."""

    fqdn = base.Field('FQDN')
    """The complete fully qualified domain name."""

    ipv4_addresses = IPv4AddressField('IPv4Addresses', default=[])
    """The IPv4 addresses currently in use by this interface."""

    ipv4_static_addresses = IPv4StaticAddressField(
        'IPv4StaticAddresses', default=[])
    """The statically-defined IPv4 addresses assigned to this interface."""

    ipv6_addresses = IPv6AddressField('IPv6Addresses', default=[])
    """The IPv6 addresses currently in use by this interface."""

    ipv6_static_addresses = IPv6StaticAddressField(
        'IPv6StaticAddresses', default=[])
    """The statically-defined IPv6 addresses assigned to this interface."""

    ipv6_static_default_gateways = IPv6StaticDefaultGatewayField(
        'IPv6StaticDefaultGateways', default=[])
    """The statically-defined IPv6 default gateways."""

    ipv6_default_gateway = base.Field('IPv6DefaultGateway')
    """The currently active IPv6 default gateway address."""

    name_servers = base.Field('NameServers', adapter=list)
    """The DNS servers in use by this interface."""

    static_name_servers = base.Field('StaticNameServers', adapter=list)
    """The statically-defined DNS server addresses."""

    dhcpv4 = DHCPv4ConfigurationField('DHCPv4')
    """DHCPv4 configuration for this interface."""

    dhcpv6 = DHCPv6ConfigurationField('DHCPv6')
    """DHCPv6 configuration for this interface."""

    status = common.StatusField("Status")
    """Describes the status and health of this interface."""

    def set_static_name_servers(self, servers):
        """Set the statically-defined DNS server addresses.

        :param servers: List of DNS server addresses.
        """
        self._conn.patch(self.path,
                         data={'StaticNameServers': servers})
        self.refresh(force=True)

    def set_dhcpv4_enabled(self, enabled):
        """Enable or disable DHCPv4.

        :param enabled: Whether DHCPv4 should be enabled.
        """
        self._conn.patch(self.path,
                         data={'DHCPv4': {'DHCPEnabled': enabled}})
        self.refresh(force=True)

    def set_dhcpv6_operating_mode(self, mode):
        """Set the DHCPv6 operating mode.

        :param mode: The DHCPv6 operating mode, one of
            :py:class:`sushy.DHCPv6OperatingMode`.
        """
        self._conn.patch(
            self.path,
            data={'DHCPv6': {
                'OperatingMode': ip_cons.DHCPv6OperatingMode(mode).value,
            }})
        self.refresh(force=True)

    def set_ipv4_static_addresses(self, addresses):
        """Set the statically-defined IPv4 addresses.

        :param addresses: List of dicts with keys ``Address``,
            ``SubnetMask``, and ``Gateway``.
        """
        self._conn.patch(self.path,
                         data={'IPv4StaticAddresses': addresses})
        self.refresh(force=True)

    def set_ipv6_static_addresses(self, addresses):
        """Set the statically-defined IPv6 addresses.

        :param addresses: List of dicts with keys ``Address``
            and ``PrefixLength``.
        """
        self._conn.patch(self.path,
                         data={'IPv6StaticAddresses': addresses})
        self.refresh(force=True)


class EthernetInterfaceCollection(base.ResourceCollectionBase):

    @property
    def _resource_type(self):
        return EthernetInterface

    @property
    @utils.cache_it
    def summary(self):
        """Summary of MAC addresses and interfaces state

        This filters the MACs whose health is OK,
        which means the MACs in both 'Enabled' and 'Disabled' States
        are returned.

        :returns: dictionary in the format
            {'aa:bb:cc:dd:ee:ff': sushy.State.ENABLED,
            'aa:bb:aa:aa:aa:aa': sushy.State.DISABLED}
        """
        mac_dict = {}
        for eth in self.get_members():
            if eth.mac_address and eth.status is not None:
                if eth.status.health == res_cons.Health.OK:
                    mac_dict[eth.mac_address] = eth.status.state
        return mac_dict
