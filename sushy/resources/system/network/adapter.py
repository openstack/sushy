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
# https://redfish.dmtf.org/schemas/v1/NetworkAdapter.v1_3_0.json

from sushy.resources import base
from sushy.resources import common
from sushy.resources.system.network import device_function
from sushy.resources.system.network import port
from sushy import utils


class NetworkAdapter(base.ResourceBase):
    description = base.Field('Description')
    """Human-readable description of the resource"""

    identity = base.Field('Id', required=True)
    """The network adapter identity string"""

    manufacturer = base.Field("Manufacturer")
    """The manufacturer of this network adapter"""

    model = base.Field("Model")
    """The model of this network adapter"""

    name = base.Field('Name')
    """The name of the network adapter"""

    part_number = base.Field("PartNumber")
    """The part number of the network adapter"""

    serial_number = base.Field("SerialNumber")
    """The serial number of the network adapter"""

    status = common.StatusField("Status")
    """The status"""

    @property
    @utils.cache_it
    def network_device_functions(self):
        """Property to reference `NetworkDeviceFunctionCollection` instance

        It is set once when the first time it is queried. On refresh,
        this property is marked as stale (greedy-refresh not done).
        Here the actual refresh of the sub-resource happens, if stale.
        """

        return device_function.NetworkDeviceFunctionCollection(
            self._conn,
            path=utils.get_sub_resource_path_by(
                self,
                "NetworkDeviceFunctions"
            ),
            redfish_version=self.redfish_version,
            registries=self.registries,
            root=self.root
        )

    @property
    @utils.cache_it
    def network_ports(self):
        """Property to reference `NetworkPortCollection` instance

        It is set once when the first time it is queried. On refresh,
        this property is marked as stale (greedy-refresh not done).
        Here the actual refresh of the sub-resource happens, if stale.
        """

        return port.NetworkPortCollection(
            self._conn,
            path=utils.get_sub_resource_path_by(self, "NetworkPorts"),
            redfish_version=self.redfish_version,
            registries=self.registries,
            root=self.root
        )


class NetworkAdapterCollection(base.ResourceCollectionBase):

    @property
    def _resource_type(self):
        return NetworkAdapter
