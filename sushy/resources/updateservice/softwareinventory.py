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
# https://redfish.dmtf.org/schemas/SoftwareInventory.v1_2_0.json

import logging

from sushy.resources import base
from sushy.resources import common

LOG = logging.getLogger(__name__)


class SoftwareInventory(base.ResourceBase):

    identity = base.Field('Id', required=True)
    """The software inventory identity"""

    lowest_supported_version = base.Field('LowestSupportedVersion')
    """The lowest supported version of the software"""

    manufacturer = base.Field('Manufacturer')
    """The manufacturer of the software"""

    name = base.Field('Name', required=True)
    """The software inventory name"""

    release_date = base.Field('ReleaseDate')
    """Release date of the software"""

    related_item = base.Field('RelatedItem')
    """The ID(s) of the resources associated with the software inventory
    item"""

    status = common.StatusField('Status')
    """The status of the software inventory"""

    software_id = base.Field('SoftwareId')
    """The identity of the software"""

    uefi_device_paths = base.Field('UefiDevicePaths')
    """Represents the UEFI Device Path(s)"""

    updateable = base.Field('Updateable')
    """Indicates whether this software can be updated by the update
    service"""

    version = base.Field('Version')
    """The version of the software"""

    def __init__(self, connector, identity,
                 redfish_version=None, registries=None):
        """A class representing a SoftwareInventory

        :param connector: A Connector instance
        :param identity: The identity of the SoftwareInventory resources
        :param redfish_version: The version of RedFish. Used to construct
            the object according to schema of given version.
        :param registries: Dict of Redfish Message Registry objects to be
            used in any resource that needs registries to parse messages
        """
        super(SoftwareInventory, self).__init__(
            connector, identity, redfish_version, registries)


class SoftwareInventoryCollection(base.ResourceCollectionBase):

    name = base.Field('Name')
    """The software inventory collection name"""

    description = base.Field('Description')
    """The software inventory collection description"""

    @property
    def _resource_type(self):
        return SoftwareInventory

    def __init__(self, connector, identity,
                 redfish_version=None, registries=None):
        """A class representing a SoftwareInventoryCollection

        :param connector: A Connector instance
        :param identity: The identity of SoftwareInventory resource
        :param redfish_version: The version of RedFish. Used to construct
            the object according to schema of given version.
        :param registries: Dict of Redfish Message Registry objects to be
            used in any resource that needs registries to parse messages
        """
        super(SoftwareInventoryCollection, self).__init__(
            connector, identity, redfish_version, registries)
