# Copyright 2017 Red Hat, Inc.
# All Rights Reserved.
#
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

from sushy import connector
from sushy.resources import base
from sushy.resources.system import system


class Sushy(base.ResourceBase):

    identity = None
    """The Redfish system identity"""

    name = None
    """The Redfish system name"""

    uuid = None
    """The Redfish system UUID"""

    def __init__(self, url, username=None, password=None, verify=True):
        super(Sushy, self).__init__(
            connector.Connector(url, username, password, verify))

    def _parse_attributes(self):
        self.identity = self.json.get('Id')
        self.name = self.json.get('Name')
        self.redfish_version = self.json.get('RedfishVersion')
        self.uuid = self.json.get('UUID')

    def get_system_collection(self):
        """Get the SystemCollection object

        :returns: a SystemCollection object
        """
        return system.SystemCollection(self._conn,
                                       redfish_version=self.redfish_version)

    def get_system(self, identity):
        """Given the identity return a System object

        :param identity: The identity of the System resource
        :returns: The System object
        """
        return system.System(self._conn, identity,
                             redfish_version=self.redfish_version)
