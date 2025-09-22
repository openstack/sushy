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

from dateutil import parser

from sushy import exceptions
from sushy.resources import base
from sushy.resources.chassis import chassis
from sushy.resources import common
from sushy.resources import constants as res_cons
from sushy.resources.manager import manager
from sushy.resources.manager import virtual_media
from sushy.resources import settings
from sushy.resources.system import bios
from sushy.resources.system import constants as sys_cons
from sushy.resources.system import ethernet_interface
from sushy.resources.system import pcie_device
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
                               sys_cons.BootSourceOverrideEnabled)

    mode = base.MappedField('BootSourceOverrideMode',
                            sys_cons.BootSourceOverrideMode)

    target = base.MappedField('BootSourceOverrideTarget', sys_cons.BootSource)

    http_boot_uri = base.Field('HttpBootUri')

    def _load(self, body, resource, nested_in=None):
        """Load the boot field, checking Settings fallback for missing values.

        Some newer BMCs move some boot values to a nested Settings field
        which is defined by an attribute on the response body. So we need
        to check there if any boot field values are None in the main
        resource.
        """
        # Load the field normally first
        instance = super()._load(body, resource, nested_in)

        if instance is None:
            return None

        # Check if we have Settings available and any values might be missing
        if (hasattr(resource, '_settings')
                and resource._settings
                and resource._settings.resource_uri):

            try:
                settings_resp = resource._conn.get(
                    resource._settings.resource_uri)
                settings_data = settings_resp.json()
                settings_boot = settings_data.get('Boot', {})

                if not settings_boot:
                    return instance

                # Check and populate allowed_values if missing
                allowable_key = ('BootSourceOverrideTarget@'
                                 'Redfish.AllowableValues')
                if (instance.allowed_values is None
                        and allowable_key in settings_boot):
                    settings_allowed_values = settings_boot[allowable_key]
                    if settings_allowed_values:
                        instance.allowed_values = list(settings_allowed_values)

                # Check and populate enabled if missing/None
                if (instance.enabled is None
                        and 'BootSourceOverrideEnabled' in settings_boot):
                    enabled_value = settings_boot['BootSourceOverrideEnabled']
                    if enabled_value:
                        try:
                            instance.enabled = (
                                sys_cons.BootSourceOverrideEnabled(
                                    enabled_value))
                        except ValueError:
                            pass  # Keep as None if value is not valid

                # Check and populate mode if missing/None
                if (instance.mode is None
                        and 'BootSourceOverrideMode' in settings_boot):
                    mode_value = settings_boot['BootSourceOverrideMode']
                    if mode_value:
                        try:
                            instance.mode = sys_cons.BootSourceOverrideMode(
                                mode_value)
                        except ValueError:
                            pass  # Keep as None if value is not valid

                # Check and populate target if missing/None
                if (instance.target is None
                        and 'BootSourceOverrideTarget' in settings_boot):
                    target_value = settings_boot['BootSourceOverrideTarget']
                    if target_value:
                        try:
                            instance.target = sys_cons.BootSource(target_value)
                        except ValueError:
                            pass  # Keep as None if value is not valid

                # Check and populate http_boot_uri if missing/None
                if (instance.http_boot_uri is None
                        and 'HttpBootUri' in settings_boot):
                    instance.http_boot_uri = settings_boot['HttpBootUri']

                if any([instance.allowed_values, instance.enabled,
                        instance.mode, instance.target,
                        instance.http_boot_uri]):
                    LOG.debug('Retrieved boot field values from Settings '
                              'resource for System %s',
                              getattr(resource, 'identity', 'unknown'))

            except Exception as exc:
                LOG.warning('Failed to retrieve boot field values from '
                            'Settings resource for System %s: %s',
                            getattr(resource, 'identity', 'unknown'), exc)

        return instance


class BootProgressField(base.CompositeField):

    last_boot_seconds_count = base.Field('LastBootTimeSeconds',
                                         adapter=utils.int_or_none)
    """The number of seconds the last boot took to reach OSRunning."""

    last_state = base.MappedField('LastState', sys_cons.BootProgressStates)
    """The last recorded boot progress states."""

    last_state_updated_at = base.Field('LastStateTime',
                                       adapter=parser.parse)
    """The date-time value when the last state field was updated."""

    oem_last_state = base.Field('OemLastState')
    """The OEM last state time to describe OEM specific state information."""


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

    indicator_led = base.MappedField('IndicatorLED', res_cons.IndicatorLED)
    """Whether the indicator LED is lit or off"""

    manufacturer = base.Field('Manufacturer')
    """The system manufacturer"""

    model = base.Field('Model')
    """The system model"""

    name = base.Field('Name')
    """The system name"""

    part_number = base.Field('PartNumber')
    """The system part number"""

    power_state = base.MappedField('PowerState', res_cons.PowerState)
    """The system power state"""

    serial_number = base.Field('SerialNumber')
    """The system serial number"""

    sku = base.Field('SKU')
    """The system stock-keeping unit"""

    status = common.StatusField('Status')
    """The system status"""

    system_type = base.MappedField('SystemType', sys_cons.SystemType)
    """The system type"""

    uuid = base.Field('UUID')
    """The system UUID"""

    memory_summary = MemorySummaryField('MemorySummary')
    """The summary info of memory of the system in general detail"""

    maintenance_window = settings.MaintenanceWindowField(
        '@Redfish.MaintenanceWindow')
    """Indicates if a given resource has a maintenance window assignment
    for applying settings or operations"""

    _settings = settings.SettingsField()
    """Settings Resource is used to represent the future intended state
    of a Resource
    Ref: http://redfish.dmtf.org/schemas/DSP0266_1.7.0.html#settings-resource
    """
    _supermicro_models_cd_vmedia = frozenset(['ars-111gl-nhr'])

    _actions = ActionsField('Actions', required=True)

    boot_progress = BootProgressField('BootProgress')
    """The last updated boot progress indicator"""

    def __init__(self, connector, identity, redfish_version=None,
                 registries=None, root=None):
        """A class representing a ComputerSystem

        :param connector: A Connector instance
        :param identity: The identity of the System resource
        :param redfish_version: The version of RedFish. Used to construct
            the object according to schema of the given version.
        :param registries: Dict of registries to be used in any resource
            that needs registries to parse messages.
        :param root: Sushy root object. Empty for Sushy root itself.
        """
        super().__init__(
            connector, identity,
            redfish_version=redfish_version,
            registries=registries,
            root=root)

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
            return set(res_cons.ResetType)

        return {v for v in res_cons.ResetType
                if v.value in reset_action.allowed_values}

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

        value = res_cons.ResetType(value).value
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
            return set(sys_cons.BootSource)

        return {v for v in sys_cons.BootSource
                if v.value in self.boot.allowed_values}

    def set_system_boot_options(self, target=None, enabled=None, mode=None,
                                http_boot_uri=None):
        """Set boot source and/or boot frequency and/or boot mode.

        Set the boot source and/or boot frequency and/or boot mode to use
        on next reboot of the System.

        :param target: The target boot source,
            a :py:class:`sushy.BootSource` value. Optional.
        :param enabled: How long the override is enabled,
            a :py:class:`sushy.BootSourceOverrideEnabled` value. Optional.
        :param mode: The boot mode,
            a :py:class:`sushy.BootSourceOverrideMode` value. Optional.
        :param http_boot_uri: The requested HTTP Boot URI to transmit to the
            BMC. Only valid when BootSourceOverrideTarget is set to UefiHTTP,
            when utilizing the ``target`` parameter. If no value is supplied,
            and the target is set to UefiHTTP, then an empty value will be
            sent to the BMC to remove any prior setting, allowing the host
            to load configuration from DHCP.
            If not explicitly set, any value will be removed from a BMC when
            UefiHttp boot is not engaged.

        :raises: InvalidParameterValueError, if any information passed is
            invalid.
        """
        data = collections.defaultdict(dict)
        settings_data = collections.defaultdict(dict)

        if self._settings and self._settings.resource_uri:
            settings_resp = self._conn.get(self._settings.resource_uri)
            settings_boot_section = settings_resp.json().get('Boot', {})
        else:
            settings_resp = None
            settings_boot_section = {}

        if target is not None:
            valid_targets = self.get_allowed_system_boot_source_values()
            if target not in valid_targets:
                raise exceptions.InvalidParameterValueError(
                    parameter='target', value=target,
                    valid_values=valid_targets)

            target = sys_cons.BootSource(target)
            # NOTE(janders) on SuperMicro X11 and X12 machines, virtual media
            # is presented as an "USB CD" drive as opposed to a CD drive.
            # On Supermicro ARS-111GL-NHR however, a more common "CD" device
            # is used. On both "families" of hardware, both "USB CD" and "CD"
            # are present in the list of boot devices, however only selecting
            # the appropriate one for the platform as the boot source results
            # in a successful boot from vMedia. Unless the appropriate option
            # for a given model is selected, boot fails even if vMedia is
            # inserted. This code detects a case where a SuperMicro machine is
            # about to attempt boot from CD and overrides the boot device to
            # UsbCd if required, depending on the model. This makes boot from
            # vMedia work as expected on both variants.
            if (self.manufacturer and self.manufacturer.lower() == 'supermicro'
                    and self.model.lower() not in
                    self._supermicro_models_cd_vmedia
                    and target == sys_cons.BootSource.CD
                    and sys_cons.BootSource.USB_CD.value
                    in self.boot.allowed_values):
                LOG.debug('Boot from vMedia was requested on a SuperMicro'
                          'machine. Overriding boot device from %s to %s.',
                          target, sys_cons.BootSource.USB_CD)
                target = sys_cons.BootSource.USB_CD
            if (settings_resp and "BootSourceOverrideTarget" in
                    settings_boot_section):
                settings_data['Boot']['BootSourceOverrideTarget'] = \
                    target.value
            else:
                data['Boot']['BootSourceOverrideTarget'] = target.value

        if enabled is not None:
            try:
                fishy_freq = sys_cons.BootSourceOverrideEnabled(enabled).value
            except ValueError:
                raise exceptions.InvalidParameterValueError(
                    parameter='enabled', value=enabled,
                    valid_values=list(sys_cons.BootSourceOverrideEnabled))
            if (settings_resp and "BootSourceOverrideEnabled" in
                    settings_boot_section):
                settings_data['Boot']['BootSourceOverrideEnabled'] = fishy_freq
            else:
                data['Boot']['BootSourceOverrideEnabled'] = fishy_freq

        if mode is not None:
            try:
                fishy_mode = sys_cons.BootSourceOverrideMode(mode).value
            except ValueError:
                raise exceptions.InvalidParameterValueError(
                    parameter='mode', value=mode,
                    valid_values=list(sys_cons.BootSourceOverrideMode))
            if (settings_resp and "BootSourceOverrideMode" in
                    settings_boot_section):
                settings_data['Boot']['BootSourceOverrideMode'] = fishy_mode
            else:
                data['Boot']['BootSourceOverrideMode'] = fishy_mode

        if target == sys_cons.BootSource.UEFI_HTTP:
            # The http_boot_uri value *can* be set independently of the
            # target, but the BMC will just ignore it unless the target
            # is set. So we should only, and explicitly set it when we've
            # been requested to boot from UefiHTTP.
            if not http_boot_uri:
                # This should clear out any old entries, as no URI translates
                # to the intent of "use whatever the dhcp server says".
                http_boot_uri = None

            if (settings_resp and "HttpBootUri" in settings_boot_section):
                settings_data['Boot']['HttpBootUri'] = http_boot_uri
            else:
                data['Boot']['HttpBootUri'] = http_boot_uri
        elif not http_boot_uri:
            # We're not doing boot from URL, we should cleanup any setting
            # which may be from a prior step/call.
            if settings_boot_section.get('HttpBootUri'):
                # If the setting is present, and has any value, unset it.
                data['Boot']['HttpBootUri'] = None

        # TODO(lucasagomes): Check the return code and response body ?
        #                    Probably we should call refresh() as well.
        if settings_data.get('Boot'):
            etag = settings_resp.headers.get('ETag')
            path = self._settings.resource_uri
            self._conn.patch(path, data=settings_data,
                             etag=etag)
        if data.get('Boot'):
            etag = self._get_etag()
            path = self.path
            self._conn.patch(path, data=data, etag=etag)

    # TODO(etingof): we should remove this method, eventually
    def set_system_boot_source(
            self, target, enabled=sys_cons.BootSourceOverrideEnabled.ONCE,
            mode=None):
        """Set boot source and/or boot frequency and/or boot mode.

        Set the boot source and/or boot frequency and/or boot mode to use
        on next reboot of the System.

        This method is obsoleted by `set_system_boot_options`.

        :param target: The target boot source,
            a :py:class:`sushy.BootSource` value.
        :param enabled: The frequency, whether to set it for the next
            a :py:class:`sushy.BootSourceOverrideEnabled` value.
            Default is `ONCE`.
        :param mode: The boot mode,
            a :py:class:`sushy.BootSourceOverrideMode` value.
        :raises: InvalidParameterValueError, if any information passed is
            invalid.
        """
        self.set_system_boot_options(target, enabled, mode)

    def set_indicator_led(self, state):
        """Set IndicatorLED to the given state.

        :param state: Desired LED state, an IndicatorLED value.
        :raises: InvalidParameterValueError, if any information passed is
            invalid.
        """
        try:
            state = res_cons.IndicatorLED(state).value
        except ValueError:
            raise exceptions.InvalidParameterValueError(
                parameter='state', value=state,
                valid_values=' ,'.join(i.value for i in res_cons.IndicatorLED))

        etag = self._get_etag()
        data = {'IndicatorLED': state}

        self._conn.patch(self.path, data=data, etag=etag)
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
            registries=self.registries, root=self.root)

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
            registries=self.registries, root=self.root)

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
            registries=self.registries, root=self.root)

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
            registries=self.registries, root=self.root)

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
            registries=self.registries, root=self.root)

    @property
    @utils.cache_it
    def managers(self):
        """A list of managers for this system.

        Returns a list of `Manager` objects representing the managers
        that manage this system.

        :raises: MissingAttributeError if '@odata.id' field is missing.
        :returns: A list of `Manager` instances
        """
        try:
            paths = utils.get_sub_resource_path_by(
                self, ["Links", "ManagedBy"], is_collection=True)
        except exceptions.MissingAttributeError as exc_orig:
            LOG.warning('Unable to find ManagedBy attribute for System %s, '
                        'retrying with Managers attribute', self.identity)
            try:
                paths = utils.get_sub_resource_path_by(
                    self, ["Links", "Managers"], is_collection=True)
            except exceptions.MissingAttributeError:
                LOG.error('Both ManagedBy and Managers attributes missing for '
                          'System %s, aborting', self.identity)
                # NOTE(janders) last_error may record only Managers and not
                # ManagedBy MissingAttributeError with this approach
                raise exc_orig
        return [manager.Manager(self._conn, path,
                                redfish_version=self.redfish_version,
                                registries=self.registries, root=self.root)
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
                                registries=self.registries, root=self.root)
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
            registries=self.registries, root=self.root)

    @property
    @utils.cache_it
    def virtual_media(self):
        """Property to reference `VirtualMedia` instance

        :returns: A `VirtualMediaCollection` instance.
        """
        return virtual_media.VirtualMediaCollection(
            self._conn, utils.get_sub_resource_path_by(self, 'VirtualMedia'),
            redfish_version=self.redfish_version, registries=self.registries,
            root=self.root)

    @property
    @utils.cache_it
    def pcie_devices(self):
        """Property to reference PCIeDeviceCollection instance"""
        try:
            pcie_path = utils.get_sub_resource_path_by(self, "PCIeDevices")
            return pcie_device.PCIeDeviceCollection(
                self._conn, pcie_path,
                redfish_version=self.redfish_version,
                registries=self.registries, root=self.root)
        except exceptions.MissingAttributeError:
            # Check if PCIeDevices is embedded in System JSON
            if (hasattr(self, 'json') and self.json
                    and 'PCIeDevices' in self.json):
                pcie_devices_data = self.json['PCIeDevices']
                if isinstance(pcie_devices_data, list) and pcie_devices_data:
                    return pcie_device.PCIeDeviceCollection(
                        self._conn, "/embedded",
                        redfish_version=self.redfish_version,
                        registries=self.registries, root=self.root,
                        embedded_data=pcie_devices_data)
            return pcie_device.PCIeDeviceCollection(
                self._conn, "/empty",
                redfish_version=self.redfish_version,
                registries=self.registries, root=self.root)


class SystemCollection(base.ResourceCollectionBase):

    @property
    def _resource_type(self):
        return System

    def __init__(self, connector, path, redfish_version=None, registries=None,
                 root=None):
        """A class representing a ComputerSystemCollection

        :param connector: A Connector instance
        :param path: The canonical path to the System collection resource
        :param redfish_version: The version of RedFish. Used to construct
            the object according to schema of the given version.
        :param registries: Dict of Redfish Message Registry objects to be
            used in any resource that needs registries to parse messages
        :param root: Sushy root object. Empty for Sushy root itself.
        """
        super().__init__(
            connector, path, redfish_version=redfish_version,
            registries=registries, root=root)
