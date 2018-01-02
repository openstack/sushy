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
# http://redfish.dmtf.org/schemas/EthernetInterface.v1_3_0.json

import logging

from sushy.resources import base
from sushy.resources.system import constants as sys_cons
from sushy.resources.system import mappings as sys_map

LOG = logging.getLogger(__name__)


class HealthStatusField(base.CompositeField):
    state = base.MappedField(
        'State', sys_map.HEALTH_STATE_VALUE_MAP)
    health = base.Field('Health')


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

    status = HealthStatusField("Status")


class EthernetInterfaceCollection(base.ResourceCollectionBase):

    _summary = None

    @property
    def _resource_type(self):
        return EthernetInterface

    @property
    def summary(self):
        """Summary of MAC addresses and interfaces state

        This filters the MACs whose health is OK,
        which means the MACs in both 'Enabled' and 'Disabled' States
        are returned.

        :returns: dictionary in the format
            {'aa:bb:cc:dd:ee:ff': 'Enabled',
            'aa:bb:aa:aa:aa:aa': 'Disabled'}
        """
        if self._summary is None:
            mac_dict = {}
            for eth in self.get_members():
                if (eth.mac_address is not None and eth.status is not None):
                    if (eth.status.health ==
                            sys_map.HEALTH_VALUE_MAP_REV.get(
                                sys_cons.HEALTH_OK)):
                        state = sys_map.HEALTH_STATE_VALUE_MAP_REV.get(
                            eth.status.state)
                        mac_dict[eth.mac_address] = state
            self._summary = mac_dict
        return self._summary

    def _do_refresh(self, force=False):
        """Do custom resource specific refresh activities

        On refresh, all sub-resources are marked as stale, i.e.
        greedy-refresh not done for them unless forced by ``force``
        argument.
        """
        self._summary = None
