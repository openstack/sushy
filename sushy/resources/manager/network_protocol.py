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

# This is referred from Redfish standard schema.
# https://redfish.dmtf.org/schemas/ManagerNetworkProtocol.v1_10_1.json

import logging

from sushy.resources import base
from sushy.resources import common
from sushy.resources.manager import constants

LOG = logging.getLogger(__name__)


class ProtocolField(base.CompositeField):
    def __init__(self, proto: constants.NetworkProtocolType, *args, **kwargs):
        super().__init__(proto.value, *args, **kwargs)

    port = base.Field('Port')
    protocol_enabled = base.Field('ProtocolEnabled')


class NTPProtocolField(ProtocolField):
    ntp_servers = base.Field('NTPServers', adapter=list)


class ManagerNetworkProtocol(base.ResourceBase):

    identity = base.Field('Id', required=True)
    """The manager network protocol identity string"""

    name = base.Field('Name')
    """The name of the resource"""

    description = base.Field('Description')
    """Description"""

    hostname = base.Field('HostName')
    """The DNS host name of the manager, without the domain."""

    fqdn = base.Field('FQDN')
    """The fully qualified domain name for the manager."""

    dhcp = ProtocolField(constants.NetworkProtocolType.DHCPv4)
    """Settings for the DHCPv4 protocol."""

    dhcpv6 = ProtocolField(constants.NetworkProtocolType.DHCPv6)
    """Settings for the DHCPv6 protocol."""

    ntp = NTPProtocolField(constants.NetworkProtocolType.NTP)
    """Settings for the NTP protocol."""

    http = ProtocolField(constants.NetworkProtocolType.HTTP)
    """Settings for the HTTP protocol."""

    https = ProtocolField(constants.NetworkProtocolType.HTTPS)
    """Settings for the HTTPS protocol."""

    ssh = ProtocolField(constants.NetworkProtocolType.SSH)
    """Settings for the SSH protocol."""

    ipmi = ProtocolField(constants.NetworkProtocolType.IPMI)
    """Settings for the IPMI-over-LAN protocol."""

    status = common.StatusField('Status')
    """Describes the status and health of this resource."""

    def set_protocol_enabled(self, protocol: constants.NetworkProtocolType,
                             enabled: bool):
        """Enable or disable a protocol.

        :param protocol: Which protocol to enable or disable.
        :param enabled: Whether the protocol should be enabled.
        """
        self._conn.patch(self.path,
                         data={protocol.value: {'ProtocolEnabled': enabled}})
        self.refresh(force=True)
