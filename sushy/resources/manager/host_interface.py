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
# https://redfish.dmtf.org/schemas/HostInterface.v1_4_0.json

import logging

from sushy.resources import base
from sushy.resources import common
from sushy.resources.manager import constants as mgr_cons
from sushy.resources.manager import network_protocol
from sushy.resources.system import ethernet_interface
from sushy.resources.system import system
from sushy import utils

LOG = logging.getLogger(__name__)


class CredentialBootstrappingField(base.CompositeField):

    enabled = base.Field('Enabled')
    """Whether credential bootstrapping is enabled."""

    enable_after_reset = base.Field('EnableAfterReset')
    """Whether credential bootstrapping should be enabled after a reset."""

    role_id = base.Field('RoleId')
    """The role used for credential bootstrapping."""

    expiration_window_enabled = base.Field('ExpirationWindowEnabled')
    """Whether credential bootstrapping is automatically disabled
    for this interface after a period of time."""

    expiration_window_minutes = base.Field('ExpirationWindowMinutes')
    """The time window, in minutes, that credential bootstrapping remains
    enabled after the system firmware transitions to the operating system."""


class HostInterface(base.ResourceBase):

    identity = base.Field('Id', required=True)
    """The host interface identity string"""

    name = base.Field('Name', required=True)
    """The name of the resource"""

    description = base.Field('Description')
    """Description"""

    host_interface_type = base.MappedField(
        'HostInterfaceType', mgr_cons.HostInterfaceType)
    """The type of host interface."""

    interface_enabled = base.Field('InterfaceEnabled')
    """Whether the interface is enabled."""

    externally_accessible = base.Field('ExternallyAccessible')
    """Whether the interface is accessible by external entities."""

    authentication_modes = base.MappedListField(
        'AuthenticationModes', mgr_cons.AuthenticationMode, default=[])
    """The authentication modes available on this interface."""

    auth_none_role_id = base.Field('AuthNoneRoleId')
    """The role used when no authentication on this interface is performed.

    Absent if ``AuthNone`` is not supported by the service for the
    ``AuthenticationModes`` property.
    """

    status = common.StatusField('Status')
    """Describes the status and health of this resource."""

    credential_bootstrapping = CredentialBootstrappingField(
        'CredentialBootstrapping')
    """The credential bootstrapping settings for this interface."""

    def set_interface_enabled(self, enabled):
        """Enable or disable the host interface.

        :param enabled: Whether the interface should be enabled.
        """
        self._conn.patch(self.path,
                         data={'InterfaceEnabled': enabled})
        self.invalidate()

    @property
    @utils.cache_it
    def network_protocol(self):
        """Property to reference the ManagerNetworkProtocol instance.

        :raises: MissingAttributeError if the link does not exist
        :returns: A `ManagerNetworkProtocol` instance
        """
        return network_protocol.ManagerNetworkProtocol(
            self._conn,
            utils.get_sub_resource_path_by(self, 'NetworkProtocol'),
            redfish_version=self.redfish_version,
            registries=self.registries, root=self.root)

    @property
    @utils.cache_it
    def systems(self):
        """A list of computer systems associated with this host interface.

        :raises: MissingAttributeError if the link does not exist
        :returns: A list of `System` instances
        """
        paths = utils.get_sub_resource_path_by(
            self, ["Links", "ComputerSystems"], is_collection=True)

        return [system.System(self._conn, path,
                              redfish_version=self.redfish_version,
                              registries=self.registries, root=self.root)
                for path in paths]

    @property
    @utils.cache_it
    def host_ethernet_interfaces(self):
        """Property to reference the host-side EthernetInterfaceCollection.

        :raises: MissingAttributeError if the link does not exist
        :returns: An `EthernetInterfaceCollection`
        """
        return ethernet_interface.EthernetInterfaceCollection(
            self._conn,
            utils.get_sub_resource_path_by(self, 'HostEthernetInterfaces'),
            redfish_version=self.redfish_version,
            registries=self.registries, root=self.root)

    @property
    @utils.cache_it
    def manager_ethernet_interface(self):
        """Property to reference the manager-side EthernetInterface.

        :raises: MissingAttributeError if the link does not exist
        :returns: An `EthernetInterface`
        """
        return ethernet_interface.EthernetInterface(
            self._conn,
            utils.get_sub_resource_path_by(
                self, 'ManagerEthernetInterface'),
            redfish_version=self.redfish_version,
            registries=self.registries, root=self.root)


class HostInterfaceCollection(base.ResourceCollectionBase):

    @property
    def _resource_type(self):
        return HostInterface

    def disable_all(self):
        """Disable all host interfaces in the collection."""
        for member in self.get_members():
            member.set_interface_enabled(False)
