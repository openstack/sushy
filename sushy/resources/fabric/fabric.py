# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

# This is referred from Redfish standard schema.
# http://redfish.dmtf.org/schemas/v1/Fabric.v1_0_4.json

from sushy.resources import base
from sushy.resources import common
from sushy.resources.fabric import mappings as fab_maps

import logging

LOG = logging.getLogger(__name__)


class Fabric(base.ResourceBase):
    """Fabric resource

    The Fabric represents a simple fabric consisting of one or more
    switches, zero or more endpoints, and zero or more zones.
    """

    identity = base.Field('Id', required=True)
    """Identifier for the fabric"""

    name = base.Field('Name', required=True)
    """The fabric name"""

    description = base.Field('Description')
    """The fabric description"""

    max_zones = base.Field('MaxZones')
    """The maximum number of zones the switch can currently configure"""

    status = common.StatusField('Status')
    """The fabric status"""

    fabric_type = base.MappedField('FabricType',
                                   fab_maps.FABRIC_TYPE_VALUE_MAP)
    """The protocol being sent over this fabric"""

    def __init__(self, connector, identity, redfish_version=None):
        """A class representing a Fabric

        :param connector: A Connector instance
        :param identity: The identity of the Fabric resource
        :param redfish_version: The version of RedFish. Used to construct
            the object according to schema of the given version.
        """
        super(Fabric, self).__init__(connector, identity, redfish_version)


class FabricCollection(base.ResourceCollectionBase):

    @property
    def _resource_type(self):
        return Fabric

    def __init__(self, connector, path, redfish_version=None):
        """A class representing a FabricCollection

        :param connector: A Connector instance
        :param path: The canonical path to the Fabric collection resource
        :param redfish_version: The version of RedFish. Used to construct
            the object according to schema of the given version.
        """
        super(FabricCollection, self).__init__(connector, path,
                                               redfish_version)
