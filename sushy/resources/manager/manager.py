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

import logging

from sushy import exceptions
from sushy.resources import base
from sushy.resources import common
from sushy.resources.manager import mappings as mgr_maps

LOG = logging.getLogger(__name__)


class ActionsField(base.CompositeField):
    reset = common.ResetActionField('#Manager.Reset')


class RemoteAccessField(base.CompositeField):
    service_enabled = base.Field('ServiceEnabled')

    max_concurrent_sessions = base.Field('MaxConcurrentSessions')

    connect_types_supported = base.Field('ConnectTypesSupported',
                                         adapter=list)


class Manager(base.ResourceBase):

    firmware_version = base.Field('FirmwareVersion')
    """The manager firmware version"""

    graphical_console = RemoteAccessField('GraphicalConsole')
    """A dictionary containing the remote access support service via
       graphical console (e.g. KVMIP) and max concurrent sessions
    """

    serial_console = RemoteAccessField('SerialConsole')
    """A dictionary containing the remote access support service via
       serial console (e.g. Telnet, SSH, IPMI) and max concurrent sessions
    """

    command_shell = RemoteAccessField('CommandShell')
    """A dictionary containing the remote access support service via
       command shell (e.g. Telnet, SSH) and max concurrent sessions
    """

    description = base.Field('Description')
    """The manager description"""

    identity = base.Field('Id', required=True)
    """The manager identity string"""

    name = base.Field('Name')
    """The manager name"""

    model = base.Field('Model')
    """The manager model"""

    manager_type = base.MappedField('ManagerType',
                                    mgr_maps.MANAGER_TYPE_VALUE_MAP)
    """The manager type"""

    uuid = base.Field('UUID')
    """The manager UUID"""

    _actions = ActionsField('Actions', required=True)

    def __init__(self, connector, identity, redfish_version=None):
        """A class representing a Manager

        :param connector: A Connector instance
        :param identity: The identity of the Manager resource
        :param redfish_version: The version of RedFish. Used to construct
            the object according to schema of the given version.
        """
        super(Manager, self).__init__(connector, identity, redfish_version)

    def get_supported_graphical_console_types(self):
        """Get the supported values for Graphical Console connection types.

        :returns: A set of supported values.
        """
        if (not self.graphical_console
                or not self.graphical_console.connect_types_supported):
            LOG.warning('Could not figure out the supported values for '
                        'remote access via graphical console for Manager %s',
                        self.identity)
            return set(mgr_maps.GRAPHICAL_CONSOLE_VALUE_MAP_REV)

        return set([mgr_maps.GRAPHICAL_CONSOLE_VALUE_MAP[v] for v in
                    set(mgr_maps.GRAPHICAL_CONSOLE_VALUE_MAP).
                    intersection(self.graphical_console.
                                 connect_types_supported)])

    def get_supported_serial_console_types(self):
        """Get the supported values for Serial Console connection types.

        :returns: A set of supported values.
        """
        if (not self.serial_console
                or not self.serial_console.connect_types_supported):
            LOG.warning('Could not figure out the supported values for '
                        'remote access via serial console for Manager %s',
                        self.identity)
            return set(mgr_maps.SERIAL_CONSOLE_VALUE_MAP_REV)

        return set([mgr_maps.SERIAL_CONSOLE_VALUE_MAP[v] for v in
                    set(mgr_maps.SERIAL_CONSOLE_VALUE_MAP).
                    intersection(self.serial_console.connect_types_supported)])

    def get_supported_command_shell_types(self):
        """Get the supported values for Command Shell connection types.

        :returns: A set of supported values.
        """
        if (not self.command_shell
                or not self.command_shell.connect_types_supported):
            LOG.warning('Could not figure out the supported values for '
                        'remote access via command shell for Manager %s',
                        self.identity)
            return set(mgr_maps.COMMAND_SHELL_VALUE_MAP_REV)

        return set([mgr_maps.COMMAND_SHELL_VALUE_MAP[v] for v in
                    set(mgr_maps.COMMAND_SHELL_VALUE_MAP).
                    intersection(self.command_shell.connect_types_supported)])

    def _get_reset_action_element(self):
        reset_action = self._actions.reset

        if not reset_action:
            raise exceptions.MissingActionError(action='#Manager.Reset',
                                                resource=self._path)
        return reset_action

    def get_allowed_reset_manager_values(self):
        """Get the allowed values for resetting the manager.

        :returns: A set of allowed values.
        :raises: MissingAttributeError, if Actions/#Manager.Reset attribute
            not present.
        """
        reset_action = self._get_reset_action_element()

        if not reset_action.allowed_values:
            LOG.warning('Could not figure out the allowed values for the '
                        'reset manager action for Manager %s', self.identity)
            return set(mgr_maps.RESET_MANAGER_VALUE_MAP_REV)

        return set([mgr_maps.RESET_MANAGER_VALUE_MAP[v] for v in
                    set(mgr_maps.RESET_MANAGER_VALUE_MAP).
                    intersection(reset_action.allowed_values)])

    def reset_manager(self, value):
        """Reset the manager.

        :param value: The target value.
        :raises: InvalidParameterValueError, if the target value is not
            allowed.
        """
        valid_resets = self.get_allowed_reset_manager_values()
        if value not in valid_resets:
            raise exceptions.InvalidParameterValueError(
                parameter='value', value=value, valid_values=valid_resets)

        value = mgr_maps.RESET_MANAGER_VALUE_MAP_REV[value]
        target_uri = self._get_reset_action_element().target_uri

        LOG.debug('Resetting the Manager %s ...', self.identity)
        self._conn.post(target_uri, data={'ResetType': value})
        LOG.info('The Manager %s is being reset', self.identity)


class ManagerCollection(base.ResourceCollectionBase):

    @property
    def _resource_type(self):
        return Manager

    def __init__(self, connector, path, redfish_version=None):
        """A class representing a ManagerCollection

        :param connector: A Connector instance
        :param path: The canonical path to the Manager collection resource
        :param redfish_version: The version of RedFish. Used to construct
            the object according to schema of the given version.
        """
        super(ManagerCollection, self).__init__(connector, path,
                                                redfish_version)
