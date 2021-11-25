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

# Values come from the Redfish Fabric json-schema:
# https://redfish.dmtf.org/schemas/v1/Fabric.v1_2_2.json
# https://redfish.dmtf.org/schemas/v1/Endpoint.v1_6_1.json

import enum


class EntityRole(enum.Enum):
    """Entity role constants"""

    INITIATOR = 'Initiator'
    """The entity sends commands, messages, or other types of requests to
    other entities on the fabric, but cannot receive commands from other
    entities."""

    TARGET = 'Target'
    """The entity receives commands, messages, or other types of requests
    from other entities on the fabric, but cannot send commands to other
    entities."""

    BOTH = 'Both'
    """The entity can both send and receive commands, messages, and other
    requests to or from other entities on the fabric."""


# Backward compatibility
ENTITY_ROLE_INITIATOR = EntityRole.INITIATOR
ENTITY_ROLE_TARGET = EntityRole.TARGET
ENTITY_ROLE_BOTH = EntityRole.BOTH


class EntityType(enum.Enum):
    """Entity type constants"""

    STORAGE_INITIATOR = 'StorageInitiator'
    """The entity is a storage initiator."""

    ROOT_COMPLEX = 'RootComplex'
    """The entity is a PCI(e) root complex."""

    NETWORK_CONTROLLER = 'NetworkController'
    """The entity is a network controller."""

    DRIVE = 'Drive'
    """The entity is a drive."""

    STORAGE_EXPANDER = 'StorageExpander'
    """The entity is a storage expander."""

    DISPLAY_CONTROLLER = 'DisplayController'
    """The entity is a display controller."""

    BRIDGE = 'Bridge'
    """The entity is a PCI(e) bridge."""

    PROCESSOR = 'Processor'
    """The entity is a processor."""

    VOLUME = 'Volume'
    """The entity is a volume."""

    ACCELERATION_FUNCTION = 'AccelerationFunction'
    """The entity is an acceleration function realized through a device,
    such as an FPGA."""

    MEDIA_CONTROLLER = 'MediaController'
    """The entity is a media controller."""

    MEMORY_CHUNK = 'MemoryChunk'
    """The entity is a memory chunk."""

    SWITCH = 'Switch'
    """The entity is a switch, not an expander.  Use `Expander` for
    expanders."""

    FABRIC_BRIDGE = 'FabricBridge'
    """The entity is a fabric bridge."""

    MANAGER = 'Manager'
    """The entity is a manager."""

    STORAGE_SUBSYSTEM = 'StorageSubsystem'
    """The entity is a storage subsystem."""


# Backward compatibility
ENTITY_TYPE_STORAGE_INITIATOR = EntityType.STORAGE_INITIATOR
ENTITY_TYPE_ROOT_COMPLEX = EntityType.ROOT_COMPLEX
ENTITY_TYPE_NETWORK_CONTROLLER = EntityType.NETWORK_CONTROLLER
ENTITY_TYPE_DRIVE = EntityType.DRIVE
ENTITY_TYPE_STORAGE_EXPANDER = EntityType.STORAGE_EXPANDER
ENTITY_TYPE_DISPLAY_CONTROLLER = EntityType.DISPLAY_CONTROLLER
ENTITY_TYPE_PCI_BRIDGE = EntityType.BRIDGE
ENTITY_TYPE_PROCESSOR = EntityType.PROCESSOR
ENTITY_TYPE_VOLUME = EntityType.VOLUME
