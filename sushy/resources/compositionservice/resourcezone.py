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
# https://redfish.dmtf.org/schemas/Zone.v1_2_0.json

import logging

from sushy.resources import base
from sushy.resources import common

LOG = logging.getLogger(__name__)


class LinksField(base.CompositeField):

    endpoints = base.Field('Endpoints')
    """The references to the endpoints that are contained in this zone"""

    involved_switches = base.Field('InvolvedSwitches')
    """The references to the switches in this zone"""

    resource_blocks = base.Field('ResourceBlocks')
    """The references to the Resource Blocks that are used in this zone"""


class ResourceZone(base.ResourceBase):

    # Note(dnuka): This patch doesn't contain 100% of the ResourceZone

    description = base.Field('Description')
    """The resources zone description"""

    identity = base.Field('Id', required=True)
    """The resource zone identity string"""

    links = LinksField('Links')
    """The references to other resources that are related to this
    resource"""

    name = base.Field('Name', required=True)
    """The resource zone name"""

    status = common.StatusField('Status')
    """The resource zone status"""

    def __init__(self, connector, identity, redfish_version=None,
                 registries=None, root=None):
        """A class representing a ResourceZone

        :param connector: A Connector instance
        :param identity: The identity of the ResourceZone resource
        :param redfish_version: The version of RedFish. Used to construct
            the object according to schema of given version.
        :param registries: Dict of Redfish Message Registry objects to be
            used in any resource that needs registries to parse messages
        :param root: Sushy root object. Empty for Sushy root itself.
        """
        super(ResourceZone, self).__init__(
            connector, identity, redfish_version=redfish_version,
            registries=registries, root=root)


class ResourceZoneCollection(base.ResourceCollectionBase):

    name = base.Field('Name')
    """The resource zone collection name"""

    description = base.Field('Description')
    """The resource zone collection description"""

    @property
    def _resource_type(self):
        return ResourceZone

    def __init__(self, connector, identity, redfish_version=None,
                 registries=None, root=None):
        """A class representing a ResourceZoneCollection

        :param connector: A Connector instance
        :param identity: The identity of the ResourceZone resource
        :param redfish_version: The version of RedFish. Used to construct
            the object according to schema of given version.
        :param registries: Dict of Redfish Message Registry objects to be
            used in any resource that needs registries to parse messages
        :param root: Sushy root object. Empty for Sushy root itself.
        """
        super(ResourceZoneCollection, self).__init__(
            connector, identity, redfish_version=redfish_version,
            registries=registries, root=root)
