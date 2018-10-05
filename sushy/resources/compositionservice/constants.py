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

# Composition state related constants
COMPOSITION_STATE_COMPOSING = 'Composing'
COMPOSITION_STATE_COMPOSED_AND_AVAILABLE = 'ComposedAndAvailable'
COMPOSITION_STATE_COMPOSED = 'Composed'
COMPOSITION_STATE_UNUSED = 'Unused'
COMPOSITION_STATE_FAILED = 'Failed'
COMPOSITION_STATE_UNAVAILABLE = 'Unavailable'

# Resource Block type related constants
RESOURCE_BLOCK_TYPE_COMPUTE = 'Compute'
RESOURCE_BLOCK_TYPE_PROCESSOR = 'Processor'
RESOURCE_BLOCK_TYPE_MEMORY = 'Memory'
RESOURCE_BLOCK_TYPE_NETWORK = 'Network'
RESOURCE_BLOCK_TYPE_STORAGE = 'Storage'
RESOURCE_BLOCK_TYPE_COMPUTERSYSTEM = 'ComputerSystem'
RESOURCE_BLOCK_TYPE_EXPANSION = 'Expansion'
