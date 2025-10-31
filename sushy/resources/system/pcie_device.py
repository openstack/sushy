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
# https://redfish.dmtf.org/schemas/v1/PCIeDevice.v1_19_0.json
# Per DMTF DSP0268_2025.2 Section 6.96 PCIeDevice 1.19.0
# Per DMTF DSP0268_2025.2 Section 6.97 PCIeFunction 1.6.0
import logging

from sushy import exceptions
from sushy.resources import base
from sushy.resources import common
from sushy.resources.system import constants as sys_cons
from sushy import utils

LOG = logging.getLogger(__name__)


class PCIeInterfaceField(base.CompositeField):
    """PCIe interface information for the device."""

    lanes_in_use = base.Field('LanesInUse', adapter=utils.int_or_none)
    """The number of PCIe lanes in use by this device."""

    max_lanes = base.Field('MaxLanes', adapter=utils.int_or_none)
    """The number of PCIe lanes supported by this device."""

    max_pcie_type = base.Field('MaxPCIeType')
    """The highest version of the PCIe specification supported by this
device."""
    pcie_type = base.Field('PCIeType')
    """The version of the PCIe specification in use by this device."""


class SlotField(base.CompositeField):
    """Slot information for the PCIe device."""

    lanes = base.Field('Lanes', adapter=utils.int_or_none)
    """The number of PCIe lanes supported by this slot."""

    location = base.Field('Location')
    """The location of the PCIe slot."""

    pcie_type = base.Field('PCIeType')
    """The PCIe specification this slot supports."""

    slot_type = base.MappedField('SlotType', sys_cons.SlotType)
    """The PCIe slot type."""

    hot_pluggable = base.Field('HotPluggable', adapter=bool)
    """An indication of whether this PCIe slot supports hotplug."""

    lane_splitting = base.MappedField('LaneSplitting',
                                      sys_cons.LaneSplittingType)
    """The lane splitting strategy used in the PCIe slot."""


class PCIeFunction(base.ResourceBase):
    """Represents a PCIe function associated within a PCIe device."""

    identity = base.Field('Id', required=True)
    """The PCIe function identity string"""

    name = base.Field('Name')
    """The PCIe function name"""

    description = base.Field('Description')
    """The PCIe function description"""

    function_id = base.Field('FunctionId', adapter=utils.int_or_none)
    """The PCIe function number within a given PCIe device."""

    function_type = base.MappedField('FunctionType', sys_cons.FunctionType)
    """The type of the PCIe function (Physical or Virtual)."""

    function_protocol = base.MappedField('FunctionProtocol',
                                         sys_cons.FunctionProtocol)
    """The PCIe function protocol (PCIe or CXL)."""

    device_class = base.MappedField('DeviceClass', sys_cons.DeviceClass)
    """The class for this PCIe function
    (NetworkController, MassStorageController, etc.)."""

    device_id = base.Field('DeviceId')
    """The Device ID of this PCIe function."""

    vendor_id = base.Field('VendorId')
    """The Vendor ID of this PCIe function."""

    subsystem_id = base.Field('SubsystemId')
    """The Subsystem ID of this PCIe function."""

    subsystem_vendor_id = base.Field('SubsystemVendorId')
    """The Subsystem Vendor ID of this PCIe function."""

    revision_id = base.Field('RevisionId')
    """The Revision ID of this PCIe function."""

    class_code = base.Field('ClassCode')
    """The Class Code of this PCIe function."""

    bus_number = base.Field('BusNumber')
    """The bus number of this PCIe function."""

    device_number = base.Field('DeviceNumber')
    """The device number of this PCIe function."""

    function_number = base.Field('FunctionNumber')
    """The function number of this PCIe function."""

    segment_number = base.Field('SegmentNumber')
    """The segment number of this PCIe function."""

    enabled = base.Field('Enabled', adapter=bool)
    """An indication of whether this PCIe device function is enabled."""

    status = common.StatusField('Status')
    """The status and health of the resource and its subordinate resources."""

    links = base.Field('Links')
    """Links to related resources."""


class PCIeFunctionCollection(base.ResourceCollectionBase):
    """Represents a collection of PCIe functions associated with a device."""

    @property
    def _resource_type(self):
        return PCIeFunction

    @property
    @utils.cache_it
    def function_count(self):
        """The number of PCIe functions in the collection.

        Returns the cached value until it (or its parent resource)
        is refreshed.
        """
        return len(self.get_members())


class PCIeDevice(base.ResourceBase):
    """Represents a PCIe device associated with a system."""

    identity = base.Field('Id', required=True)
    """The PCIe device identity string"""

    name = base.Field('Name')
    """The PCIe device name"""

    description = base.Field('Description')
    """The PCIe device description"""

    manufacturer = base.Field('Manufacturer')
    """The manufacturer of this PCIe device."""

    model = base.Field('Model')
    """The model number for the PCIe device."""

    serial_number = base.Field('SerialNumber')
    """The serial number for this PCIe device."""

    part_number = base.Field('PartNumber')
    """The part number for this PCIe device."""

    sku = base.Field('SKU')
    """The stock-keeping unit for this PCIe device."""

    device_type = base.MappedField('DeviceType', sys_cons.PCIeDeviceType)
    """The device type for this PCIe device."""

    firmware_version = base.Field('FirmwareVersion')
    """The version of firmware for this PCIe device."""

    asset_tag = base.Field('AssetTag')
    """The user-assigned asset tag for this PCIe device."""

    status = common.StatusField('Status')
    """The status and health of the resource and its subordinate resources."""

    pcie_interface = PCIeInterfaceField('PCIeInterface')
    """The PCIe interface details for this device."""

    slot = SlotField('Slot')
    """Information about the slot for this PCIe device."""

    links = base.Field('Links')
    """Links to related resources."""

    @property
    @utils.cache_it
    def pcie_functions(self):
        """Property to reference PCIeFunctionCollection instance

        Returns a PCIeFunctionCollection representing the PCIe functions
        associated with this PCIe device.

        :raises: MissingAttributeError if PCIeFunctions is not supported
        :returns: PCIeFunctionCollection instance
        """
        try:
            return PCIeFunctionCollection(
                self._conn,
                utils.get_sub_resource_path_by(self, "PCIeFunctions"),
                redfish_version=self.redfish_version,
                registries=self.registries, root=self.root)
        except exceptions.MissingAttributeError:
            # Return empty collection if PCIeFunctions is not supported
            return PCIeFunctionCollection(
                self._conn, "/empty",
                redfish_version=self.redfish_version,
                registries=self.registries, root=self.root)


class PCIeDeviceCollection(base.ResourceCollectionBase):
    @property
    def _resource_type(self):
        return PCIeDevice

    @property
    @utils.cache_it
    def device_count(self):
        """The number of PCIe devices in the collection.

        Returns the cached value until it (or its parent resource)
        is refreshed.
        """
        return len(self.get_members())

    def __init__(self, connector, path, redfish_version=None, registries=None,
                 root=None, embedded_data=None):
        if path == "/empty":
            self._conn = connector
            self._path = path
            self._json = {'Members': []}
            self.redfish_version = redfish_version
            self._registries = registries
            self._root = root
            self._is_stale = False
            return

        if embedded_data is not None:
            self._conn = connector
            self._path = path
            self._json = {'Members': embedded_data}
            self.redfish_version = redfish_version
            self._registries = registries
            self._root = root
            self._is_stale = False
            return

        super().__init__(connector, path, redfish_version, registries, root)

    @property
    def members_identities(self):
        if self._path == "/empty":
            return []
        if hasattr(self, '_json') and self._json and 'Members' in self._json:
            return tuple(m['@odata.id'] for m in self._json['Members']
                         if isinstance(m, dict) and '@odata.id' in m)
        return super().members_identities

    def get_members(self):
        if self._path == "/empty":
            return []

        # Handle embedded PCIeDevices case
        if hasattr(self, '_json') and self._json and 'Members' in self._json:
            device_objects = []
            for member in self._json['Members']:
                if isinstance(member, dict) and '@odata.id' in member:
                    device_path = member['@odata.id']
                    try:
                        # Fetch device data and create object
                        device_response = self._conn.get(device_path)
                        if device_response:
                            device_obj = PCIeDevice(
                                self._conn, device_path,
                                redfish_version=self.redfish_version,
                                registries=self._registries, root=self._root
                            )
                            device_obj._json = device_response.json()
                            device_objects.append(device_obj)
                    except Exception as e:
                        LOG.warning(
                            'Error fetching PCIe device at path %s: %s',
                            device_path, str(e))
                        continue  # Skip failed devices but continue processing
            return device_objects

        # Standard collection behavior
        return super().get_members()
