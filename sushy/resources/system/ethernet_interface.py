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
# https://redfish.dmtf.org/schemas/EthernetInterface.v1_4_0.json

import logging

from sushy.resources import base
from sushy.resources import common
from sushy.resources import constants as res_cons
from sushy import utils

LOG = logging.getLogger(__name__)


class EthernetInterface(base.ResourceBase):
    """This class adds the EthernetInterface resource"""

    identity = base.Field('Id', required=True)
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

    status = common.StatusField("Status")
    """Describes the status and health of this interface."""


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
            if eth.mac_address is not None and eth.status is not None:
                if eth.status.health == res_cons.Health.OK:
                    mac_dict[eth.mac_address] = eth.status.state
        return mac_dict
