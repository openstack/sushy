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

import logging

from sushy import exceptions
from sushy.resources import base
from sushy.resources import common
from sushy.resources.system import constants as sys_cons
from sushy.resources.system import mappings as sys_maps
from sushy.resources.system import processor


LOG = logging.getLogger(__name__)


class ActionsField(base.CompositeField):
    reset = common.ResetActionField('#ComputerSystem.Reset')


class BootField(base.CompositeField):
    allowed_values = base.Field(
        'BootSourceOverrideTarget@Redfish.AllowableValues',
        adapter=list)

    enabled = base.MappedField('BootSourceOverrideEnabled',
                               sys_maps.BOOT_SOURCE_ENABLED_MAP)

    mode = base.MappedField('BootSourceOverrideMode',
                            sys_maps.BOOT_SOURCE_MODE_MAP)

    target = base.MappedField('BootSourceOverrideTarget',
                              sys_maps.BOOT_SOURCE_TARGET_MAP)


class MemorySummaryField(base.CompositeField):
    health = base.Field(['Status', 'HealthRollup'])
    """The overall health state of memory.

    This signifies health state of memory along with its dependent resources.
    """

    size_gib = base.Field('TotalSystemMemoryGiB', adapter=int)
    """The size of memory of the system in GiB.

    This signifies the total installed, operating system-accessible memory
    (RAM), measured in GiB.
    """


class System(base.ResourceBase):

    asset_tag = base.Field('AssetTag')
    """The system asset tag"""

    bios_version = base.Field('BiosVersion')
    """The system BIOS version"""

    boot = BootField('Boot', required=True)
    """A dictionary containg the current boot device, frequency and mode"""

    description = base.Field('Description')
    """The system description"""

    hostname = base.Field('HostName')
    """The system hostname"""

    identity = base.Field('Id', required=True)
    """The system identity string"""

    # TODO(lucasagomes): Create mappings for the indicator_led
    indicator_led = base.Field('IndicatorLED')
    """Whether the indicator LED is lit or off"""

    manufacturer = base.Field('Manufacturer')
    """The system manufacturer"""

    name = base.Field('Name')
    """The system name"""

    part_number = base.Field('PartNumber')
    """The system part number"""

    power_state = base.MappedField('PowerState',
                                   sys_maps.SYSTEM_POWER_STATE_MAP)
    """The system power state"""

    serial_number = base.Field('SerialNumber')
    """The system serial number"""

    sku = base.Field('SKU')
    """The system stock-keeping unit"""

    # TODO(lucasagomes): Create mappings for the system_type
    system_type = base.Field('SystemType')
    """The system type"""

    uuid = base.Field('UUID')
    """The system UUID"""

    memory_summary = MemorySummaryField('MemorySummary')
    """The summary info of memory of the system in general detail"""

    _processors = None  # ref to ProcessorCollection instance

    _actions = ActionsField('Actions', required=True)

    def __init__(self, connector, identity, redfish_version=None):
        """A class representing a ComputerSystem

        :param connector: A Connector instance
        :param identity: The identity of the System resource
        :param redfish_version: The version of RedFish. Used to construct
            the object according to schema of the given version.
        """
        super(System, self).__init__(connector, identity, redfish_version)

    def _get_reset_action_element(self):
        reset_action = self._actions.reset
        # TODO(dtantsur): make this check also declarative?
        if not reset_action:
            raise exceptions.MissingActionError(action='#ComputerSystem.Reset',
                                                resource=self._path)
        return reset_action

    def get_allowed_reset_system_values(self):
        """Get the allowed values for resetting the system.

        :returns: A set with the allowed values.
        """
        reset_action = self._get_reset_action_element()

        if not reset_action.allowed_values:
            LOG.warning('Could not figure out the allowed values for the '
                        'reset system action for System %s', self.identity)
            return set(sys_maps.RESET_SYSTEM_VALUE_MAP_REV)

        return set([sys_maps.RESET_SYSTEM_VALUE_MAP[v] for v in
                    set(sys_maps.RESET_SYSTEM_VALUE_MAP).
                    intersection(reset_action.allowed_values)])

    def reset_system(self, value):
        """Reset the system.

        :param value: The target value.
        :raises: InvalidParameterValueError, if the target value is not
            allowed.
        """
        valid_resets = self.get_allowed_reset_system_values()
        if value not in valid_resets:
            raise exceptions.InvalidParameterValueError(
                parameter='value', value=value, valid_values=valid_resets)

        value = sys_maps.RESET_SYSTEM_VALUE_MAP_REV[value]
        target_uri = self._get_reset_action_element().target_uri

        # TODO(lucasagomes): Check the return code and response body ?
        #                    Probably we should call refresh() as well.
        self._conn.post(target_uri, data={'ResetType': value})

    def get_allowed_system_boot_source_values(self):
        """Get the allowed values for changing the boot source.

        :returns: A set with the allowed values.
        """
        if not self.boot.allowed_values:
            LOG.warning('Could not figure out the allowed values for '
                        'configuring the boot source for System %s',
                        self.identity)
            return set(sys_maps.BOOT_SOURCE_TARGET_MAP_REV)

        return set([sys_maps.BOOT_SOURCE_TARGET_MAP[v] for v in
                    set(sys_maps.BOOT_SOURCE_TARGET_MAP).
                    intersection(self.boot.allowed_values)])

    def set_system_boot_source(self, target,
                               enabled=sys_cons.BOOT_SOURCE_ENABLED_ONCE,
                               mode=None):
        """Set the boot source.

        Set the boot source to use on next reboot of the System.

        :param target: The target boot source.
        :param enabled: The frequency, whether to set it for the next
            reboot only (BOOT_SOURCE_ENABLED_ONCE) or persistent to all
            future reboots (BOOT_SOURCE_ENABLED_CONTINUOUS) or disabled
            (BOOT_SOURCE_ENABLED_DISABLED).
        :param mode: The boot mode, UEFI (BOOT_SOURCE_MODE_UEFI) or
            BIOS (BOOT_SOURCE_MODE_BIOS).
        :raises: InvalidParameterValueError, if any information passed is
            invalid.
        """
        valid_targets = self.get_allowed_system_boot_source_values()
        if target not in valid_targets:
            raise exceptions.InvalidParameterValueError(
                parameter='target', value=target, valid_values=valid_targets)

        if enabled not in sys_maps.BOOT_SOURCE_ENABLED_MAP_REV:
            raise exceptions.InvalidParameterValueError(
                parameter='enabled', value=enabled,
                valid_values=list(sys_maps.BOOT_SOURCE_TARGET_MAP_REV))

        data = {
            'Boot': {
                'BootSourceOverrideTarget':
                    sys_maps.BOOT_SOURCE_TARGET_MAP_REV[target],
                'BootSourceOverrideEnabled':
                    sys_maps.BOOT_SOURCE_ENABLED_MAP_REV[enabled]
            }
        }

        if mode is not None:
            if mode not in sys_maps.BOOT_SOURCE_MODE_MAP_REV:
                raise exceptions.InvalidParameterValueError(
                    parameter='mode', value=mode,
                    valid_values=list(sys_maps.BOOT_SOURCE_MODE_MAP_REV))

            data['Boot']['BootSourceOverrideMode'] = (
                sys_maps.BOOT_SOURCE_MODE_MAP_REV[mode])

        # TODO(lucasagomes): Check the return code and response body ?
        #                    Probably we should call refresh() as well.
        self._conn.patch(self.path, data=data)

    # TODO(lucasagomes): All system have a Manager and Chassis object,
    # include a get_manager() and get_chassis() once we have an abstraction
    # for those resources.

    def _get_processor_collection_path(self):
        """Helper function to find the ProcessorCollection path"""
        processor_col = self.json.get('Processors')
        if not processor_col:
            raise exceptions.MissingAttributeError(attribute='Processors',
                                                   resource=self._path)
        return processor_col.get('@odata.id')

    @property
    def processors(self):
        """Property to provide reference to `ProcessorCollection` instance

        It is calculated once when the first time it is queried. On refresh,
        this property gets reset.
        """
        if self._processors is None:
            self._processors = processor.ProcessorCollection(
                self._conn, self._get_processor_collection_path(),
                redfish_version=self.redfish_version)

        return self._processors

    def refresh(self):
        super(System, self).refresh()
        self._processors = None


class SystemCollection(base.ResourceCollectionBase):

    @property
    def _resource_type(self):
        return System

    def __init__(self, connector, path, redfish_version=None):
        """A class representing a ComputerSystemCollection

        :param connector: A Connector instance
        :param path: The canonical path to the System collection resource
        :param redfish_version: The version of RedFish. Used to construct
            the object according to schema of the given version.
        """
        super(SystemCollection, self).__init__(connector, path,
                                               redfish_version)
