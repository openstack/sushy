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
from sushy.resources import common
from sushy.resources import constants as res_cons
from sushy.resources.system.storage import constants
from sushy.resources.system.storage import controller
from sushy.resources.system.storage import drive
from sushy.resources.system.storage import volume
from sushy import utils


LOG = logging.getLogger(__name__)


class StorageControllersListField(base.ListField):
    """The set of storage controllers represented by this resource."""

    member_id = base.Field('MemberId', required=True)
    """Uniquely identifies the member within the collection."""

    name = base.Field('Name', required=True)
    """The name of the storage controller"""

    status = common.StatusField('Status')
    """Describes the status and health of the resource and its children."""

    identifiers = common.IdentifiersListField('Identifiers', default=[])
    """The Durable names for the storage controller."""

    speed_gbps = base.Field('SpeedGbps')
    """The maximum speed of the storage controller's device interface."""

    controller_protocols = base.MappedListField(
        'SupportedControllerProtocols', res_cons.Protocol)
    """The protocols by which this storage controller can be communicated to"""

    device_protocols = base.MappedListField('SupportedDeviceProtocols',
                                            res_cons.Protocol)
    """The protocols which the controller can use tocommunicate with devices"""

    raid_types = base.MappedListField('SupportedRAIDTypes', constants.RAIDType)
    """The set of RAID types supported by the storage controller."""


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

    status = common.StatusField('Status')
    """Describes the status and health of the resource and its children."""

    def get_drive(self, drive_identity):
        """Given the drive identity return a ``Drive`` object

        :param drive_identity: The identity of the ``Drive``
        :returns: The ``Drive`` object
        :raises: ResourceNotFoundError
        """
        return drive.Drive(self._conn, drive_identity,
                           redfish_version=self.redfish_version,
                           registries=self.registries, root=self.root)

    @property
    @utils.cache_it
    def drives(self):
        """Return a list of `Drive` objects present in the storage resource.

        It is set once when the first time it is queried. On subsequent
        invocations, it returns a cached list of `Drives` objects until it is
        marked stale.

        :returns: A list of `Drive` objects
        :raises: ResourceNotFoundError
        """
        return [self.get_drive(id_) for id_ in self.drives_identities]

    @property
    @utils.cache_it
    def drives_sizes_bytes(self):
        """Sizes of all Drives in bytes in Storage resource.

        Returns the list of cached values until it (or its parent resource)
        is refreshed.
        """
        return sorted(drv.capacity_bytes for drv in self.drives)

    @property
    def drives_max_size_bytes(self):
        """Max size available in bytes among all Drives of this collection."""
        return utils.max_safe(self.drives_sizes_bytes)

    @property
    @utils.cache_it
    def volumes(self):
        """Property to reference `VolumeCollection` instance

        It is set once when the first time it is queried. On refresh,
        this property is marked as stale (greedy-refresh not done at that
        point). Here only the actual refresh of the sub-resource happens,
        if resource is stale.
        """
        return volume.VolumeCollection(
            self._conn, utils.get_sub_resource_path_by(self, 'Volumes'),
            redfish_version=self.redfish_version, root=self.root)

    storage_controllers = StorageControllersListField('StorageControllers',
                                                      default=[])
    """The storage devices associated with this resource.

    Deprecated since Redfish v1.13 to allow storage controllers be their own
    resource. Use `controllers` where available.
    """

    @property
    @utils.cache_it
    def controllers(self):
        """The storage controllers allocated to this storage subsystem.

        Replaces `storage_controllers` since Redfish v1.9 to allow storage
        controllers be their own resource.
        """
        return controller.ControllerCollection(
            self._conn,
            utils.get_sub_resource_path_by(self, "Controllers"),
            redfish_version=self.redfish_version,
            registries=self.registries, root=self.root)


class StorageCollection(base.ResourceCollectionBase):
    """This class represents the collection of Storage resources"""

    @property
    def _resource_type(self):
        return Storage

    @property
    @utils.cache_it
    def drives_sizes_bytes(self):
        """Sizes of each Drive in bytes in Storage collection resource.

        Returns the list of cached values until it (or its parent resource)
        is refreshed.
        """
        return sorted(drive_size for storage_ in self.get_members()
                      for drive_size in storage_.drives_sizes_bytes)

    @property
    def max_drive_size_bytes(self):
        """Max size available (in bytes) among all Drive resources.

        Returns the cached value until it (or its parent resource) is
        refreshed.
        """
        return utils.max_safe(self.drives_sizes_bytes)

    @property
    @utils.cache_it
    def volumes_sizes_bytes(self):
        """Sizes of each Volume in bytes in Storage collection resource.

        Returns the list of cached values until it (or its parent resource)
        is refreshed.
        """
        return sorted(volume_size for storage_ in self.get_members()
                      for volume_size in storage_.volumes.volumes_sizes_bytes)

    @property
    def max_volume_size_bytes(self):
        """Max size available (in bytes) among all Volume resources.

        Returns the cached value until it (or its parent resource) is
        refreshed.
        """
        return utils.max_safe(self.volumes_sizes_bytes)
