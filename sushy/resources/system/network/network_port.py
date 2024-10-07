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
# https://redfish.dmtf.org/schemas/v1/NetworkPort.v1_2_1.json

from sushy.resources import base
from sushy.resources import common
from sushy.resources.system.network import constants


class NetworkPortCollection(base.ResourceCollectionBase):

    @property
    def _resource_type(self):
        return NetworkPort


class NetworkPort(base.ResourceBase):
    associated_network_addresses = base.Field(
        "AssociatedNetworkAddresses", adapter=list
    )
    """The array of configured network addresses that are associated."""

    current_link_speed_mbps = base.Field(
        "CurrentLinkSpeedMbps", adapter=int
    )
    """The network port current link speed."""

    description = base.Field('Description')
    """The network port description"""

    flow_control_configuration = base.MappedField('FlowControlConfiguration',
                                                  constants.FlowControl)
    """The locally configured 802.3x flow control setting."""

    flow_control_status = base.MappedField('FlowControlStatus',
                                           constants.FlowControl)
    """The 802.3x flow control behavior negotiated with the link partner"""

    identity = base.Field('Id', required=True)
    """The network port identity"""

    link_status = base.MappedField('LinkStatus', constants.LinkStatus)
    """The link status of the network port."""

    name = base.Field(
        "Name", required=True
    )
    """The network port name"""

    physical_port_number = base.Field("PhysicalPortNumber", adapter=int)
    """The physical port number label for this port."""

    status = common.StatusField('Status')
    """The network port status"""
