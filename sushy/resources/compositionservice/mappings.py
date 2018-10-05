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

from sushy.resources.compositionservice import constants as comp_cons
from sushy import utils


COMPOSITION_STATE_VALUE_MAP = {
    'Composing': comp_cons.COMPOSITION_STATE_COMPOSING,
    'ComposedAndAvailable': comp_cons.COMPOSITION_STATE_COMPOSED_AND_AVAILABLE,
    'Composed': comp_cons.COMPOSITION_STATE_COMPOSED,
    'Unused': comp_cons.COMPOSITION_STATE_UNUSED,
    'Failed': comp_cons.COMPOSITION_STATE_FAILED,
    'Unavailable': comp_cons.COMPOSITION_STATE_UNAVAILABLE
}

COMPOSITION_STATE_VALUE_MAP_REV = (
    utils.revert_dictionary(COMPOSITION_STATE_VALUE_MAP))

RESOURCE_BLOCK_TYPE_VALUE_MAP = {
    'Compute': comp_cons.RESOURCE_BLOCK_TYPE_COMPUTE,
    'Processor': comp_cons.RESOURCE_BLOCK_TYPE_PROCESSOR,
    'Memory': comp_cons.RESOURCE_BLOCK_TYPE_MEMORY,
    'Network': comp_cons.RESOURCE_BLOCK_TYPE_NETWORK,
    'Storage': comp_cons.RESOURCE_BLOCK_TYPE_STORAGE,
    'ComputerSystem': comp_cons.RESOURCE_BLOCK_TYPE_COMPUTERSYSTEM,
    'Expansion': comp_cons.RESOURCE_BLOCK_TYPE_EXPANSION
}

RESOURCE_BLOCK_TYPE_VALUE_MAP_REV = (
    utils.revert_dictionary(RESOURCE_BLOCK_TYPE_VALUE_MAP))
