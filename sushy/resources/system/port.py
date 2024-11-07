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
# https://redfish.dmtf.org/schemas/v1/Port.v1_8_0.json

from sushy.resources import base
from sushy.resources import common
from sushy.resources.system.network import constants


class LLDPReceiveField(base.CompositeField):
    chassis_id = base.Field("ChassisId")
    """chassis ID received from the remote partner across this link."""

    port_id = base.Field("PortId")
    """A colon delimited string of hexadecimal octets identifying a port."""


class EthernetField(base.CompositeField):
    associated_mac_addresses = base.Field(
        "AssociatedMACAddresses", adapter=list
    )
    """The array of configured MAC addresses that are associated."""

    flow_control_configuration = base.MappedField(
        "FlowControlConfiguration", constants.FlowControl
    )
    """The locally configured 802.3x flow control setting."""

    flow_control_status = base.MappedField(
        "FlowControlStatus", constants.FlowControl
    )
    """The 802.3x flow control behavior negotiated with the link partner"""

    lldp_receive = LLDPReceiveField("LLDPReceive")
    """LLDP data being received on this link."""


class Port(base.ResourceBase):
    """This class adds the Port resource"""

    identity = base.Field("Id", required=True)
    """The Port identity string"""

    name = base.Field("Name", required=True)
    """The port name"""

    current_speed_gbps = base.Field("CurrentSpeedGbps", adapter=int)
    """The network port current link speed."""

    description = base.Field("Description")
    """The port description"""

    ethernet = EthernetField("Ethernet")
    """The Ethernet-specific properties of the port."""

    link_status = base.MappedField("LinkStatus", constants.PortLinkStatus)
    """The link status of the port."""

    port_id = base.Field("PortId")
    """The physical port id label for this port."""

    status = common.StatusField("Status")
    """The port status"""


class PortCollection(base.ResourceCollectionBase):
    @property
    def _resource_type(self):
        return Port
