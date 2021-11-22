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

# Values come from the Redfish ResourceBlock json-schema.
# https://redfish.dmtf.org/schemas/ResourceBlock.v1_3_0.json

import enum


class CompositionState(enum.Enum):
    COMPOSING = 'Composing'
    """Intermediate state indicating composition is in progress."""

    COMPOSED_AND_AVAILABLE = 'ComposedAndAvailable'
    """Indicates the Resource Block is currently participating in one or
    more compositions, and is available to be used in more compositions."""

    COMPOSED = 'Composed'
    """Final successful state of a Resource Block which has participated in
    composition."""

    UNUSED = 'Unused'
    """Indicates the Resource Block is free and can participate in
    composition."""

    FAILED = 'Failed'
    """The final composition resulted in failure and manual intervention may
    be required to fix it."""

    UNAVAILABLE = 'Unavailable'
    """Indicates the Resource Block has been made unavailable by the
    service, such as due to maintenance being performed on the Resource
    Block."""


# Backward compatibility
COMPOSITION_STATE_COMPOSING = CompositionState.COMPOSING
COMPOSITION_STATE_COMPOSED_AND_AVAILABLE = \
    CompositionState.COMPOSED_AND_AVAILABLE
COMPOSITION_STATE_COMPOSED = CompositionState.COMPOSED
COMPOSITION_STATE_UNUSED = CompositionState.UNUSED
COMPOSITION_STATE_FAILED = CompositionState.FAILED
COMPOSITION_STATE_UNAVAILABLE = CompositionState.UNAVAILABLE


class ResourceBlockType(enum.Enum):
    COMPUTE = 'Compute'
    """This Resource Block contains both Processor and Memory resources in a
    manner that creates a compute complex."""

    PROCESSOR = 'Processor'
    """This Resource Block contains Processor resources."""

    MEMORY = 'Memory'
    """This Resource Block contains Memory resources."""

    NETWORK = 'Network'
    """This Resource Block contains Network resources, such as Ethernet
    Interfaces."""

    STORAGE = 'Storage'
    """This Resource Block contains Storage resources, such as Storage and
    Simple Storage."""

    COMPUTER_SYSTEM = 'ComputerSystem'
    """This Resource Block contains ComputerSystem resources."""

    EXPANSION = 'Expansion'
    """This Resource Block is capable of changing over time based on its
    configuration.  Different types of devices within this Resource Block
    can be added and removed over time."""


# Backward compatibility
RESOURCE_BLOCK_TYPE_COMPUTE = ResourceBlockType.COMPUTE
RESOURCE_BLOCK_TYPE_PROCESSOR = ResourceBlockType.PROCESSOR
RESOURCE_BLOCK_TYPE_MEMORY = ResourceBlockType.MEMORY
RESOURCE_BLOCK_TYPE_NETWORK = ResourceBlockType.NETWORK
RESOURCE_BLOCK_TYPE_STORAGE = ResourceBlockType.STORAGE
RESOURCE_BLOCK_TYPE_COMPUTERSYSTEM = ResourceBlockType.COMPUTER_SYSTEM
RESOURCE_BLOCK_TYPE_EXPANSION = ResourceBlockType.EXPANSION
