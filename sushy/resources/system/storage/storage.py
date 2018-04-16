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
from sushy import utils

LOG = logging.getLogger(__name__)


class Storage(base.ResourceBase):
    """This class represents resources that represent a storage subsystem.

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

    def get_drive(self, drive_identity):
        """Given the drive identity return a ``Drive`` object

        :param identity: The identity of the ``Drive``
        :returns: The ``Drive`` object
        :raises: ResourceNotFoundError
        """
        return drive.Drive(self._conn, drive_identity,
                           redfish_version=self.redfish_version)

    @property
    def drives_max_size_bytes(self):
        """Max size available in bytes among all Drives of this collection."""
        if self._drives_max_size_bytes is None:
            self._drives_max_size_bytes = (
                utils.max_safe(self.get_drive(drive_id).capacity_bytes
                               for drive_id in self.drives_identities))
        return self._drives_max_size_bytes

    def _do_refresh(self, force=False):
        """Do resource specific refresh activities

        On refresh, all sub-resources are marked as stale, i.e.
        greedy-refresh not done for them unless forced by ``force``
        argument.
        """
        self._drives_max_size_bytes = None
