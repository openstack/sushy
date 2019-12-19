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
# http://redfish.dmtf.org/schemas/v1/SimpleStorage.v1_2_0.json

import logging

from sushy.resources import base
from sushy.resources import common
from sushy.resources import constants as res_cons
from sushy import utils


LOG = logging.getLogger(__name__)


class DeviceListField(base.ListField):
    """The storage device/s associated with SimpleStorage."""

    name = base.Field('Name', required=True)
    """The name of the storage device"""

    capacity_bytes = base.Field('CapacityBytes', adapter=utils.int_or_none)
    """The size of the storage device."""

    status = common.StatusField('Status')
    """Describes the status and health of a storage device."""


class SimpleStorage(base.ResourceBase):
    """This class represents a simple storage.

    It represents the properties of a storage controller and its
    directly-attached devices. A storage device can be a disk drive or optical
    media device.
    """

    identity = base.Field('Id', required=True)
    """The SimpleStorage identity string"""

    name = base.Field('Name')
    """The name of the resource"""

    devices = DeviceListField('Devices', default=[])
    """The storage devices associated with this resource."""


class SimpleStorageCollection(base.ResourceCollectionBase):
    """Represents a collection of simple storage associated with system."""

    @property
    def _resource_type(self):
        return SimpleStorage

    @property
    @utils.cache_it
    def disks_sizes_bytes(self):
        """Sizes of each Disk in bytes in SimpleStorage collection resource.

        Returns the list of cached values until it (or its parent resource)
        is refreshed.
        """
        return sorted(device.capacity_bytes
                      for simpl_stor in self.get_members()
                      for device in simpl_stor.devices
                      if (device.status.state == res_cons.STATE_ENABLED
                          and device.capacity_bytes is not None))

    @property
    def max_size_bytes(self):
        """Max size available (in bytes) among all enabled Disk resources.

        Returns the cached value until it (or its parent resource) is
        refreshed.
        """
        return utils.max_safe(self.disks_sizes_bytes)
