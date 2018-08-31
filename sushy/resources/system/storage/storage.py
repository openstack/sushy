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
# http://redfish.dmtf.org/schemas/v1/Storage.v1_4_0.json

import logging

from sushy.resources import base
from sushy.resources.system.storage import drive
from sushy.resources.system.storage import volume
from sushy import utils


LOG = logging.getLogger(__name__)


class Storage(base.ResourceBase):
    """This class represents the storage subsystem resources.

    A storage subsystem represents a set of storage controllers (physical or
    virtual) and the resources such as drives and volumes that can be accessed
    from that subsystem.
    """

    identity = base.Field('Id', required=True)
    """The Storage identity string"""

    name = base.Field('Name')
    """The name of the resource"""

    drives_identities = base.Field('Drives',
                                   adapter=utils.get_members_identities)
    """A tuple with the drive identities"""

    _drives_max_size_bytes = None
    _drives = None
    _volumes = None  # reference to VolumeCollection instance

    def get_drive(self, drive_identity):
        """Given the drive identity return a ``Drive`` object

        :param identity: The identity of the ``Drive``
        :returns: The ``Drive`` object
        :raises: ResourceNotFoundError
        """
        return drive.Drive(self._conn, drive_identity,
                           redfish_version=self.redfish_version)

    @property
    def drives(self):
        """Return a list of `Drive` objects present in the storage resource.

        It is set once when the first time it is queried. On subsequent
        invocations, it returns a cached list of `Drives` objects until it is
        marked stale.

        :returns: A list of `Drive` objects
        :raises: ResourceNotFoundError
        """
        if self._drives is None:
            self._drives = [
                self.get_drive(id_) for id_ in self.drives_identities]
        return self._drives

    @property
    def drives_max_size_bytes(self):
        """Max size available in bytes among all Drives of this collection."""
        if self._drives_max_size_bytes is None:
            self._drives_max_size_bytes = (
                utils.max_safe(drv.capacity_bytes for drv in self.drives))
        return self._drives_max_size_bytes

    @property
    def volumes(self):
        """Property to reference `VolumeCollection` instance

        It is set once when the first time it is queried. On refresh,
        this property is marked as stale (greedy-refresh not done at that
        point). Here only the actual refresh of the sub-resource happens,
        if resource is stale.
        """
        if self._volumes is None:
            self._volumes = volume.VolumeCollection(
                self._conn, utils.get_sub_resource_path_by(self, 'Volumes'),
                redfish_version=self.redfish_version)

        self._volumes.refresh(force=False)
        return self._volumes

    def _do_refresh(self, force=False):
        """Do resource specific refresh activities."""
        # Note(deray): undefine the attribute here for fresh evaluation in
        # subsequent calls to it's exposed property.
        self._drives_max_size_bytes = None
        self._drives = None
        # invalidate the nested resource
        if self._volumes is not None:
            self._volumes.invalidate(force)


class StorageCollection(base.ResourceCollectionBase):
    """This class represents the collection of Storage resources"""

    _max_drive_size_bytes = None
    _max_volume_size_bytes = None

    @property
    def _resource_type(self):
        return Storage

    @property
    def max_drive_size_bytes(self):
        """Max size available (in bytes) among all device resources."""
        if self._max_drive_size_bytes is None:
            self._max_drive_size_bytes = max(
                storage_.drives_max_size_bytes
                for storage_ in self.get_members())
        return self._max_drive_size_bytes

    @property
    def max_volume_size_bytes(self):
        """Max size available (in bytes) among all Volumes under this."""
        if self._max_volume_size_bytes is None:
            self._max_volume_size_bytes = max(
                storage_.volumes.max_size_bytes
                for storage_ in self.get_members())
        return self._max_volume_size_bytes

    def _do_refresh(self, force=False):
        """Do resource specific refresh activities"""
        # Note(deray): undefine the attributes here for fresh evaluation in
        # subsequent calls to their exposed properties.
        self._max_drive_size_bytes = None
        self._max_volume_size_bytes = None
