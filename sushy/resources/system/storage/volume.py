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
# http://redfish.dmtf.org/schemas/v1/Volume.v1_0_3.json

import logging

from sushy.resources import base
from sushy import utils

LOG = logging.getLogger(__name__)


class Volume(base.ResourceBase):
    """This class adds the Storage Volume resource"""

    identity = base.Field('Id', required=True)
    """The Volume identity string"""

    name = base.Field('Name')
    """The name of the resource"""

    capacity_bytes = base.Field('CapacityBytes', adapter=utils.int_or_none)
    """The size in bytes of this Volume."""


class VolumeCollection(base.ResourceCollectionBase):
    """This class represents the Storage Volume collection"""

    _max_size_bytes = None

    @property
    def _resource_type(self):
        return Volume

    @property
    def max_size_bytes(self):
        """Max size available in bytes among all Volumes of this collection."""
        if self._max_size_bytes is None:
            self._max_size_bytes = (
                utils.max_safe([vol.capacity_bytes
                                for vol in self.get_members()]))
        return self._max_size_bytes

    def _do_refresh(self, force=False):
        # invalidate the attribute
        self._max_size_bytes = None
