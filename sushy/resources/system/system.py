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

# This is referred from Redfish standard schema.
# https://redfish.dmtf.org/schemas/v1/ComputerSystem.v1_10_0.json

import collections
import logging

from sushy import exceptions
from sushy.resources import base
from sushy.resources.chassis import chassis
from sushy.resources import common
from sushy.resources.manager import manager
from sushy.resources import mappings as res_maps
from sushy.resources import settings
from sushy.resources.system import bios
from sushy.resources.system import constants as sys_cons
from sushy.resources.system import ethernet_interface
from sushy.resources.system import mappings as sys_maps
from sushy.resources.system import processor
from sushy.resources.system import secure_boot
from sushy.resources.system import simple_storage as sys_simple_storage
from sushy.resources.system.storage import storage as sys_storage
from sushy import utils


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

    size_gib = base.Field('TotalSystemMemoryGiB', adapter=utils.int_or_none)
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
    """A dictionary containing the current boot device, frequency and mode"""

    description = base.Field('Description')
    """The system description"""

    hostname = base.Field('HostName')
    """The system hostname"""

    identity = base.Field('Id', required=True)
    """The system identity string"""

    indicator_led = base.MappedField('IndicatorLED',
                                     res_maps.INDICATOR_LED_VALUE_MAP)
    """Whether the indicator LED is lit or off"""

    manufacturer = base.Field('Manufacturer')
    """The system manufacturer"""

    name = base.Field('Name')
    """The system name"""

    part_number = base.Field('PartNumber')
    """The system part number"""

    power_state = base.MappedField('PowerState',
                                   res_maps.POWER_STATE_VALUE_MAP)
    """The system power state"""

    serial_number = base.Field('SerialNumber')
    """The system serial number"""

    sku = base.Field('SKU')
    """The system stock-keeping unit"""

    status = common.StatusField('Status')
    """The system status"""

    system_type = base.MappedField('SystemType',
                                   sys_maps.SYSTEM_TYPE_VALUE_MAP)
    """The system type"""

    uuid = base.Field('UUID')
    """The system UUID"""

    memory_summary = MemorySummaryField('MemorySummary')
    """The summary info of memory of the system in general detail"""

    maintenance_window = settings.MaintenanceWindowField(
        '@Redfish.MaintenanceWindow')
    """Indicates if a given resource has a maintenance window assignment
    for applying settings or operations"""

    _actions = ActionsField('Actions', required=True)

    def __init__(self, connector, identity, redfish_version=None,
                 registries=None):
        """A class representing a ComputerSystem

        :param connector: A Connector instance
        :param identity: The identity of the System resource
        :param redfish_version: The version of RedFish. Used to construct
            the object according to schema of the given version.
        :param registries: Dict of registries to be used in any resource
            that needs registries to parse messages.
        """
        super(System, self).__init__(
            connector, identity, redfish_version, registries)

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

    def set_system_boot_options(self, target=None, enabled=None, mode=None):
        """Set boot source and/or boot frequency and/or boot mode.

        Set the boot source and/or boot frequency and/or boot mode to use
        on next reboot of the System.

        :param target: The target boot source, optional.
        :param enabled: The frequency, whether to set it for the next
            reboot only (BOOT_SOURCE_ENABLED_ONCE) or persistent to all
            future reboots (BOOT_SOURCE_ENABLED_CONTINUOUS) or disabled
            (BOOT_SOURCE_ENABLED_DISABLED), optional.
        :param mode: The boot mode (UEFI: BOOT_SOURCE_MODE_UEFI or
            BIOS: BOOT_SOURCE_MODE_BIOS), optional.
        :raises: InvalidParameterValueError, if any information passed is
            invalid.
        """
        data = collections.defaultdict(dict)

        if target is not None:
            valid_targets = self.get_allowed_system_boot_source_values()
            if target not in valid_targets:
                raise exceptions.InvalidParameterValueError(
                    parameter='target', value=target,
                    valid_values=valid_targets)

            fishy_target = sys_maps.BOOT_SOURCE_TARGET_MAP_REV[target]

            data['Boot']['BootSourceOverrideTarget'] = fishy_target

        if enabled is not None:
            if enabled not in sys_maps.BOOT_SOURCE_ENABLED_MAP_REV:
                raise exceptions.InvalidParameterValueError(
                    parameter='enabled', value=enabled,
                    valid_values=list(sys_maps.BOOT_SOURCE_ENABLED_MAP_REV))

            fishy_freq = sys_maps.BOOT_SOURCE_ENABLED_MAP_REV[enabled]

            data['Boot']['BootSourceOverrideEnabled'] = fishy_freq

        if mode is not None:
            if mode not in sys_maps.BOOT_SOURCE_MODE_MAP_REV:
                raise exceptions.InvalidParameterValueError(
                    parameter='mode', value=mode,
                    valid_values=list(sys_maps.BOOT_SOURCE_MODE_MAP_REV))

            fishy_mode = sys_maps.BOOT_SOURCE_MODE_MAP_REV[mode]

            data['Boot']['BootSourceOverrideMode'] = fishy_mode

        # TODO(lucasagomes): Check the return code and response body ?
        #                    Probably we should call refresh() as well.
        self._conn.patch(self.path, data=data)

    # TODO(etingof): we should remove this method, eventually
    def set_system_boot_source(
            self, target, enabled=sys_cons.BOOT_SOURCE_ENABLED_ONCE,
            mode=None):
        """Set boot source and/or boot frequency and/or boot mode.

        Set the boot source and/or boot frequency and/or boot mode to use
        on next reboot of the System.

        This method is obsoleted by `set_system_boot_options`.

        :param target: The target boot source.
        :param enabled: The frequency, whether to set it for the next
            reboot only (BOOT_SOURCE_ENABLED_ONCE) or persistent to all
            future reboots (BOOT_SOURCE_ENABLED_CONTINUOUS) or disabled
            (BOOT_SOURCE_ENABLED_DISABLED).
            Default is `BOOT_SOURCE_ENABLED_ONCE`.
        :param mode: The boot mode (UEFI: BOOT_SOURCE_MODE_UEFI or
            BIOS: BOOT_SOURCE_MODE_BIOS), optional.
        :raises: InvalidParameterValueError, if any information passed is
            invalid.
        """
        self.set_system_boot_options(target, enabled, mode)

    def set_indicator_led(self, state):
        """Set IndicatorLED to the given state.

        :param state: Desired LED state, lit (INDICATOR_LED_LIT), blinking
            (INDICATOR_LED_BLINKING), off (INDICATOR_LED_OFF)
        :raises: InvalidParameterValueError, if any information passed is
            invalid.
        """
        if state not in res_maps.INDICATOR_LED_VALUE_MAP_REV:
            raise exceptions.InvalidParameterValueError(
                parameter='state', value=state,
                valid_values=list(res_maps.INDICATOR_LED_VALUE_MAP_REV))

        data = {
            'IndicatorLED': res_maps.INDICATOR_LED_VALUE_MAP_REV[state]
        }

        self._conn.patch(self.path, data=data)
        self.invalidate()

    def _get_processor_collection_path(self):
        """Helper function to find the ProcessorCollection path"""
        return utils.get_sub_resource_path_by(self, 'Processors')

    @property
    @utils.cache_it
    def processors(self):
        """Property to reference `ProcessorCollection` instance

        It is set once when the first time it is queried. On refresh,
        this property is marked as stale (greedy-refresh not done).
        Here the actual refresh of the sub-resource happens, if stale.
        """
        return processor.ProcessorCollection(
            self._conn, self._get_processor_collection_path(),
            redfish_version=self.redfish_version,
            registries=self.registries)

    @property
    @utils.cache_it
    def ethernet_interfaces(self):
        """Property to reference `EthernetInterfaceCollection` instance

        It is set once when the first time it is queried. On refresh,
        this property is marked as stale (greedy-refresh not done).
        Here the actual refresh of the sub-resource happens, if stale.
        """
        return ethernet_interface.EthernetInterfaceCollection(
            self._conn,
            utils.get_sub_resource_path_by(self, "EthernetInterfaces"),
            redfish_version=self.redfish_version,
            registries=self.registries)

    @property
    @utils.cache_it
    def bios(self):
        """Property to reference `Bios` instance

        It is set once when the first time it is queried. On refresh,
        this property is marked as stale (greedy-refresh not done).
        Here the actual refresh of the sub-resource happens, if stale.
        """
        return bios.Bios(
            self._conn,
            utils.get_sub_resource_path_by(self, 'Bios'),
            redfish_version=self.redfish_version,
            registries=self.registries)

    @property
    @utils.cache_it
    def simple_storage(self):
        """A collection of simple storage associated with system.

        This returns a reference to `SimpleStorageCollection` instance.
        SimpleStorage represents the properties of a storage controller and its
        directly-attached devices.

        It is set once when the first time it is queried. On refresh,
        this property is marked as stale (greedy-refresh not done).
        Here the actual refresh of the sub-resource happens, if stale.

        :raises: MissingAttributeError if 'SimpleStorage/@odata.id' field
            is missing.
        :returns: `SimpleStorageCollection` instance
        """
        return sys_simple_storage.SimpleStorageCollection(
            self._conn, utils.get_sub_resource_path_by(self, "SimpleStorage"),
            redfish_version=self.redfish_version,
            registries=self.registries)

    @property
    @utils.cache_it
    def storage(self):
        """A collection of storage subsystems associated with system.

        This returns a reference to `StorageCollection` instance.
        A storage subsystem represents a set of storage controllers (physical
        or virtual) and the resources such as drives and volumes that can be
        accessed from that subsystem.

        It is set once when the first time it is queried. On refresh,
        this property is marked as stale (greedy-refresh not done).
        Here the actual refresh of the sub-resource happens, if stale.

        :raises: MissingAttributeError if 'Storage/@odata.id' field
            is missing.
        :returns: `StorageCollection` instance
        """
        return sys_storage.StorageCollection(
            self._conn, utils.get_sub_resource_path_by(self, "Storage"),
            redfish_version=self.redfish_version,
            registries=self.registries)

    @property
    @utils.cache_it
    def managers(self):
        """A list of managers for this system.

        Returns a list of `Manager` objects representing the managers
        that manage this system.

        :raises: MissingAttributeError if '@odata.id' field is missing.
        :returns: A list of `Manager` instances
        """
        paths = utils.get_sub_resource_path_by(
            self, ["Links", "ManagedBy"], is_collection=True)

        return [manager.Manager(self._conn, path,
                                redfish_version=self.redfish_version,
                                registries=self.registries)
                for path in paths]

    @property
    @utils.cache_it
    def chassis(self):
        """A list of chassis where this system resides.

        Returns a list of `Chassis` objects representing the chassis
        or cabinets where this system is mounted.

        :raises: MissingAttributeError if '@odata.id' field is missing.
        :returns: A list of `Chassis` instances
        """
        paths = utils.get_sub_resource_path_by(
            self, ["Links", "Chassis"], is_collection=True)

        return [chassis.Chassis(self._conn, path,
                                redfish_version=self.redfish_version,
                                registries=self.registries)
                for path in paths]

    @property
    @utils.cache_it
    def secure_boot(self):
        """Property to reference `SecureBoot` instance

        It is set once when the first time it is queried. On refresh,
        this property is marked as stale (greedy-refresh not done).
        Here the actual refresh of the sub-resource happens, if stale.
        """
        return secure_boot.SecureBoot(
            self._conn,
            utils.get_sub_resource_path_by(self, 'SecureBoot'),
            redfish_version=self.redfish_version,
            registries=self.registries)


class SystemCollection(base.ResourceCollectionBase):

    @property
    def _resource_type(self):
        return System

    def __init__(self, connector, path, redfish_version=None, registries=None):
        """A class representing a ComputerSystemCollection

        :param connector: A Connector instance
        :param path: The canonical path to the System collection resource
        :param redfish_version: The version of RedFish. Used to construct
            the object according to schema of the given version.
        :param registries: Dict of Redfish Message Registry objects to be
            used in any resource that needs registries to parse messages
        """
        super(SystemCollection, self).__init__(
            connector, path, redfish_version, registries)
