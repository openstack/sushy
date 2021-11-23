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

# Values comes from the Redfish Chassis json-schema:
# https://redfish.dmtf.org/schemas/v1/Chassis.v1_17_0.json

import enum


class ChassisType(enum.Enum):
    """Chassis Types constants"""

    RACK = 'Rack'
    """An equipment rack, typically a 19-inch wide freestanding unit."""

    BLADE = 'Blade'
    """An enclosed or semi-enclosed, typically vertically-oriented, system
    chassis that must be plugged into a multi-system chassis to function
    normally."""

    ENCLOSURE = 'Enclosure'
    """A generic term for a chassis that does not fit any other description."""

    STAND_ALONE = 'StandAlone'
    """A single, free-standing system, commonly called a tower or desktop
    chassis."""

    RACK_MOUNT = 'RackMount'
    """A single-system chassis designed specifically for mounting in an
    equipment rack."""

    CARD = 'Card'
    """A loose device or circuit board intended to be installed in a system
    or other enclosure."""

    CARTRIDGE = 'Cartridge'
    """A small self-contained system intended to be plugged into a multi-
    system chassis."""

    ROW = 'Row'
    """A collection of equipment racks."""

    POD = 'Pod'
    """A collection of equipment racks in a large, likely transportable,
    container."""

    EXPANSION = 'Expansion'
    """A chassis that expands the capabilities or capacity of another
    chassis."""

    SIDECAR = 'Sidecar'
    """A chassis that mates mechanically with another chassis to expand its
    capabilities or capacity."""

    ZONE = 'Zone'
    """A logical division or portion of a physical chassis that contains
    multiple devices or systems that cannot be physically separated."""

    SLED = 'Sled'
    """An enclosed or semi-enclosed, system chassis that must be plugged
    into a multi-system chassis to function normally similar to a blade
    type chassis."""

    SHELF = 'Shelf'
    """An enclosed or semi-enclosed, typically horizontally-oriented, system
    chassis that must be plugged into a multi-system chassis to function
    normally."""

    DRAWER = 'Drawer'
    """An enclosed or semi-enclosed, typically horizontally-oriented, system
    chassis that can be slid into a multi-system chassis."""

    MODULE = 'Module'
    """A small, typically removable, chassis or card that contains devices
    for a particular subsystem or function."""

    COMPONENT = 'Component'
    """A small chassis, card, or device that contains devices for a
    particular subsystem or function."""

    IP_BASED_DRIVE = 'IPBasedDrive'
    """A chassis in a drive form factor with IP-based network connections."""

    RACK_GROUP = 'RackGroup'
    """A group of racks that form a single entity or share infrastructure."""

    STORAGE_ENCLOSURE = 'StorageEnclosure'
    """A chassis that encloses storage."""

    OTHER = 'Other'
    """A chassis that does not fit any of these definitions."""


# Backward compatibility
CHASSIS_TYPE_RACK = ChassisType.RACK
CHASSIS_TYPE_BLADE = ChassisType.BLADE
CHASSIS_TYPE_ENCLOSURE = ChassisType.ENCLOSURE
CHASSIS_TYPE_STAND_ALONE = ChassisType.STAND_ALONE
CHASSIS_TYPE_RACK_MOUNT = ChassisType.RACK_MOUNT
CHASSIS_TYPE_CARD = ChassisType.CARD
CHASSIS_TYPE_CARTRIDGE = ChassisType.CARTRIDGE
CHASSIS_TYPE_ROW = ChassisType.ROW
CHASSIS_TYPE_POD = ChassisType.POD
CHASSIS_TYPE_EXPANSION = ChassisType.EXPANSION
CHASSIS_TYPE_SIDECAR = ChassisType.SIDECAR
CHASSIS_TYPE_ZONE = ChassisType.ZONE
CHASSIS_TYPE_SLED = ChassisType.SLED
CHASSIS_TYPE_SHELF = ChassisType.SHELF
CHASSIS_TYPE_DRAWER = ChassisType.DRAWER
CHASSIS_TYPE_MODULE = ChassisType.MODULE
CHASSIS_TYPE_COMPONENT = ChassisType.COMPONENT
CHASSIS_TYPE_IP_BASED_DRIVE = ChassisType.IP_BASED_DRIVE
CHASSIS_TYPE_RACK_GROUP = ChassisType.RACK_GROUP
CHASSIS_TYPE_STORAGE_ENCLOSURE = ChassisType.STORAGE_ENCLOSURE
CHASSIS_TYPE_OTHER = ChassisType.OTHER


class IntrusionSensor(enum.Enum):
    """Chassis IntrusionSensor constants"""

    NORMAL = 'Normal'
    """No abnormal physical security condition is detected at this time."""

    HARDWARE_INTRUSION = 'HardwareIntrusion'
    """A door, lock, or other mechanism protecting the internal system
    hardware from being accessed is detected to be in an insecure state."""

    TAMPERING_DETECTED = 'TamperingDetected'
    """Physical tampering of the monitored entity is detected."""


# Backward compatibility
CHASSIS_INTRUSION_SENSOR_NORMAL = IntrusionSensor.NORMAL
CHASSIS_INTRUSION_SENSOR_HARDWARE_INTRUSION = \
    IntrusionSensor.HARDWARE_INTRUSION
CHASSIS_INTRUSION_SENSOR_TAMPERING_DETECTED = \
    IntrusionSensor.TAMPERING_DETECTED


class IntrusionSensorReArm(enum.Enum):
    """Chassis IntrusionSensorReArm constants"""

    MANUAL = 'Manual'
    """A manual re-arm of this sensor restores it to the normal state."""

    AUTOMATIC = 'Automatic'
    """Because no abnormal physical security condition is detected, this
    sensor is automatically restored to the normal state."""


# Backward compatibility
CHASSIS_INTRUSION_SENSOR_RE_ARM_MANUAL = IntrusionSensorReArm.MANUAL
CHASSIS_INTRUSION_SENSOR_RE_ARM_AUTOMATIC = IntrusionSensorReArm.AUTOMATIC
