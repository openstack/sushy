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
# https://redfish.dmtf.org/schemas/ResourceBlock.v1_1_0.json

import logging

from sushy.resources import base
from sushy.resources import common
from sushy.resources.compositionservice import constants

LOG = logging.getLogger(__name__)


class CompositionStatusField(base.CompositeField):

    composition_state = base.MappedField(
        'CompositionState',
        constants.CompositionState,
        required=True)
    """Inform the client, state of the resource block"""

    max_compositions = base.Field('MaxCompositions')
    """The maximum number of compositions"""

    number_of_compositions = base.Field('NumberOfCompositions')
    """The number of compositions"""

    reserved_state = base.Field('Reserved')
    """Inform the resource block has been identified by a client"""

    sharing_capable = base.Field('SharingCapable')
    """Indicates if this Resource Block is capable of participating in
    multiple compositions simultaneously"""

    sharing_enabled = base.Field('SharingEnabled')
    """Indicates if this Resource Block is allowed to participate in
    multiple compositions simultaneously"""


class ResourceBlock(base.ResourceBase):

    composition_status = CompositionStatusField(
        'CompositionStatus',
        required=True)
    """The composition state of resource block"""

    description = base.Field('Description')
    """The resource block description"""

    identity = base.Field('Id', required=True)
    """The resource block identity string"""

    name = base.Field('Name', required=True)
    """The resource block name"""

    resource_block_type = base.MappedField(
        'ResourceBlockType',
        constants.ResourceBlockType,
        required=True)
    """The type of resource block"""

    status = common.StatusField('Status')
    """The status of resource block"""

    def __init__(self, connector, identity, redfish_version=None,
                 registries=None, root=None):
        """A class representing a ResourceBlock

        :param connector: A Connector instance
        :param identity: The identity of the ResourceBlock resource
        :param redfish_version: The version of RedFish. Used to construct
            the object according to schema of given version.
        :param registries: Dict of Redfish Message Registry objects to be
            used in any resource that needs registries to parse messages
        :param root: Sushy root object. Empty for Sushy root itself.
        """
        super(ResourceBlock, self).__init__(
            connector, identity, redfish_version=redfish_version,
            registries=registries, root=root)


class ResourceBlockCollection(base.ResourceCollectionBase):

    name = base.Field('Name')
    """The resource block collection name"""

    description = base.Field('Description')
    """The resource block collection description"""

    @property
    def _resource_type(self):
        return ResourceBlock

    def __init__(self, connector, identity, redfish_version=None,
                 registries=None, root=None):
        """A class representing a ResourceBlockCollection

        :param connector: A Connector instance
        :param identity: A identity of the ResourceBlock resource
        :param redfish_version: The version of RedFish. Used to construct
            the object according to schema of given version.
        :param registries: Dict of Redfish Message Registry objects to be
            used in any resource that needs registries to parse messages
        :param root: Sushy root object. Empty for Sushy root itself.
        """
        super(ResourceBlockCollection, self).__init__(
            connector, identity, redfish_version=redfish_version,
            registries=registries, root=root)
