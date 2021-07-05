# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# This is referred from Redfish standard schema.
# https://redfish.dmtf.org/schemas/CompositionService.v1_1_0.json

import logging

from sushy import exceptions
from sushy.resources import base
from sushy.resources import common
from sushy.resources.compositionservice import resourceblock
from sushy.resources.compositionservice import resourcezone
from sushy import utils

LOG = logging.getLogger(__name__)


class CompositionService(base.ResourceBase):

    allow_overprovisioning = base.Field('AllowOverprovisioning')
    """This indicates whether this service is allowed to overprovision"""

    allow_zone_affinity = base.Field('AllowZoneAffinity')
    """This indicates whether a client is allowed to request that given
    composition request"""

    description = base.Field('Description')
    """The composition service description"""

    identity = base.Field('Id', required=True)
    """The composition service identity string"""

    name = base.Field('Name', required=True)
    """The composition service name"""

    status = common.StatusField('Status')
    """The status of composition service"""

    service_enabled = base.Field('ServiceEnabled')
    """The status of composition service is enabled"""

    def __init__(self, connector, identity, redfish_version=None,
                 registries=None, root=None):
        """A class representing a CompositionService

        :param connector: A connector instance
        :param identity: The identity of the CompositionService resource
        :param redfish_version: The version of RedFish. Used to construct
            the object according to schema of given version
        :param registries: Dict of Redfish Message Registry objects to be
            used in any resource that needs registries to parse messages
        :param root: Sushy root object. Empty for Sushy root itself.
        """
        super(CompositionService, self).__init__(
            connector, identity, redfish_version=redfish_version,
            registries=registries, root=root)

    def _get_resource_blocks_collection_path(self):
        """Helper function to find the ResourceBlockCollections path"""
        res_block_col = self.json.get('ResourceBlocks')
        if not res_block_col:
            raise exceptions.MissingAttributeError(
                attribute='ResourceBlocks', resource=self._path)
        return res_block_col.get('@odata.id')

    def _get_resource_zones_collection_path(self):
        """Helper function to find the ResourceZoneCollections path"""
        res_zone_col = self.json.get('ResourceZones')
        if not res_zone_col:
            raise exceptions.MissingAttributeError(
                attribute='ResourceZones', resource=self._path)
        return res_zone_col.get('@odata.id')

    @property
    @utils.cache_it
    def resource_blocks(self):
        """Property to reference `ResourceBlockCollection` instance"""
        return resourceblock.ResourceBlockCollection(
            self._conn, self._get_resource_blocks_collection_path,
            redfish_version=self.redfish_version, registries=self.registries,
            root=self.root)

    @property
    @utils.cache_it
    def resource_zones(self):
        """Property to reference `ResourceZoneCollection` instance"""
        return resourcezone.ResourceZoneCollection(
            self._conn, self._get_resource_zones_collection_path,
            redfish_version=self.redfish_version, registries=self.registries,
            root=self.root)
