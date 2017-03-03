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
from sushy.resources.manager import manager
from sushy.resources.system import system


class Sushy(base.ResourceBase):

    identity = base.Field('Id', required=True)
    """The Redfish root service identity"""

    name = base.Field('Name')
    """The Redfish root service name"""

    uuid = base.Field('UUID')
    """The Redfish root service UUID"""

    _systems_path = base.Field(['Systems', '@odata.id'], required=True)
    """SystemCollection path"""

    _managers_path = base.Field(['Managers', '@odata.id'], required=True)
    """ManagerCollection path"""

    def __init__(self, base_url, username=None, password=None,
                 root_prefix='/redfish/v1/', verify=True):
        """A class representing a RootService

        :param base_url: The base URL to the Redfish controller. It
            should include scheme and authority portion of the URL. For
            example: https://mgmt.vendor.com
        :param username: User account with admin/server-profile access
            privilege
        :param password: User account password
        :param root_prefix: The default URL prefix. This part includes
            the root service and version. Defaults to /redfish/v1
        :param verify: Either a boolean value, a path to a CA_BUNDLE
            file or directory with certificates of trusted CAs. If set to
            True the driver will verify the host certificates; if False
            the driver will ignore verifying the SSL certificate; if it's
            a path the driver will use the specified certificate or one of
            the certificates in the directory. Defaults to True.
        """
        self._root_prefix = root_prefix
        super(Sushy, self).__init__(
            connector.Connector(base_url, username, password, verify),
            path=self._root_prefix)

    def _parse_attributes(self):
        super(Sushy, self)._parse_attributes()
        self.redfish_version = self.json.get('RedfishVersion')

    def get_system_collection(self):
        """Get the SystemCollection object

        :raises: MissingAttributeError, if the collection attribute is
            not found
        :returns: a SystemCollection object
        """
        return system.SystemCollection(self._conn, self._systems_path,
                                       redfish_version=self.redfish_version)

    def get_system(self, identity):
        """Given the identity return a System object

        :param identity: The identity of the System resource
        :returns: The System object
        """
        return system.System(self._conn, identity,
                             redfish_version=self.redfish_version)

    def get_manager_collection(self):
        """Get the ManagerCollection object

        :raises: MissingAttributeError, if the collection attribute is
            not found
        :returns: a ManagerCollection object
        """
        return manager.ManagerCollection(self._conn, self._managers_path,
                                         redfish_version=self.redfish_version)

    def get_manager(self, identity):
        """Given the identity return a Manager object

        :param identity: The identity of the Manager resource
        :returns: The Manager object
        """
        return manager.Manager(self._conn, identity,
                               redfish_version=self.redfish_version)
