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

from sushy import exceptions
from sushy.resources import base
from sushy.resources import common
from sushy.resources.system.storage import mappings as store_maps
from sushy import utils

LOG = logging.getLogger(__name__)


class ActionsField(base.CompositeField):
    initialize = common.InitializeActionField('#Volume.Initialize')


class Volume(base.ResourceBase):
    """This class adds the Storage Volume resource"""

    identity = base.Field('Id', required=True)
    """The Volume identity string"""

    name = base.Field('Name')
    """The name of the resource"""

    capacity_bytes = base.Field('CapacityBytes', adapter=utils.int_or_none)
    """The size in bytes of this Volume."""

    volume_type = base.MappedField('VolumeType',
                                   store_maps.VOLUME_TYPE_TYPE_MAP)
    """The type of this volume."""

    raid_type = base.MappedField('RAIDType', store_maps.RAID_TYPE_TYPE_MAP)
    """The RAID type of this volume."""

    encrypted = base.Field('Encrypted', adapter=bool)
    """Is this Volume encrypted."""

    identifiers = common.IdentifiersListField('Identifiers', default=[])
    """The Durable names for the volume."""

    block_size_bytes = base.Field('BlockSizeBytes', adapter=int)
    """The size of the smallest addressable unit of this volume in bytes."""

    operation_apply_time_support = common.OperationApplyTimeSupportField()
    """Indicates if a client is allowed to request for a specific apply
    time of a create, delete, or action operation of a given resource"""

    _actions = ActionsField('Actions', required=True)

    def _get_initialize_action_element(self):
        initialize_action = self._actions.initialize
        if not initialize_action:
            raise exceptions.MissingActionError(action='#Volume.Initialize',
                                                resource=self._path)
        return initialize_action

    def get_allowed_initialize_volume_values(self):
        """Get the allowed values for initializing the volume.

        :returns: A set with the allowed values.
        """
        action = self._get_initialize_action_element()

        if not action.allowed_values:
            LOG.warning('Could not figure out the allowed values for the '
                        'initialize volume action for Volume %s',
                        self.identity)
            return set(store_maps.VOLUME_INIT_TYPE_MAP_REV)

        return set([store_maps.VOLUME_INIT_TYPE_MAP[v] for v in
                    set(store_maps.VOLUME_INIT_TYPE_MAP).
                    intersection(action.allowed_values)])

    def initialize_volume(self, value):
        """Initialize the volume.

        :param value: The InitializeType value.
        :raises: InvalidParameterValueError, if the target value is not
            allowed.
        """
        valid_values = self.get_allowed_initialize_volume_values()
        if value not in valid_values:
            raise exceptions.InvalidParameterValueError(
                parameter='value', value=value, valid_values=valid_values)
        value = store_maps.VOLUME_INIT_TYPE_MAP_REV[value]
        target_uri = self._get_initialize_action_element().target_uri
        self._conn.post(target_uri, data={'InitializeType': value},
                        blocking=True)

    def delete_volume(self, payload=None):
        """Delete the volume.

        :param payload: May contain @Redfish.OperationApplyTime property
        :raises: ConnectionError
        :raises: HTTPError
        """
        self._conn.delete(self._path, data=payload, blocking=True)


class VolumeCollection(base.ResourceCollectionBase):
    """This class represents the Storage Volume collection"""

    @property
    def _resource_type(self):
        return Volume

    @property
    @utils.cache_it
    def volumes_sizes_bytes(self):
        """Sizes of all Volumes in bytes in VolumeCollection resource.

        Returns the list of cached values until it (or its parent resource)
        is refreshed.
        """
        return sorted(vol.capacity_bytes for vol in self.get_members())

    @property
    def max_volume_size_bytes(self):
        """Max size available (in bytes) among all Volume resources.

        Returns the cached value until it (or its parent resource) is
        refreshed.
        """
        return utils.max_safe(self.volumes_sizes_bytes)

    # NOTE(etingof): for backward compatibility
    max_size_bytes = max_volume_size_bytes

    operation_apply_time_support = common.OperationApplyTimeSupportField()
    """Indicates if a client is allowed to request for a specific apply
    time of a create, delete, or action operation of a given resource"""

    def create_volume(self, payload):
        """Create a volume.

        :param payload: The payload representing the new volume to create.
        :raises: ConnectionError
        :raises: HTTPError
        :returns: Newly created Volume resource or None if no Location header
        """
        r = self._conn.post(self._path, data=payload, blocking=True)
        location = r.headers.get('Location')
        if r.status_code == 201:
            if location:
                self.refresh()
                return self.get_member(location)
