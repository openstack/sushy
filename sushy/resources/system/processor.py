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

import collections
import logging

from sushy.resources import base
from sushy.resources.system import mappings as sys_maps

# Representation of Summary of Processor information
ProcessorSummary = collections.namedtuple('ProcessorSummary',
                                          ['count', 'architecture'])
LOG = logging.getLogger(__name__)


class Processor(base.ResourceBase):

    identity = base.Field('Id', required=True)
    """The processor identity string"""

    socket = base.Field('Socket')
    """The socket or location of the processor"""

    # TODO(deray): Create mappings for the processor_type
    processor_type = base.Field('ProcessorType')
    """The type of processor"""

    processor_architecture = base.MappedField(
        'ProcessorArchitecture', sys_maps.PROCESSOR_ARCH_VALUE_MAP)
    """The architecture of the processor"""

    # TODO(deray): Create mappings for the instruction_set
    instruction_set = base.Field('InstructionSet')
    """The instruction set of the processor"""

    manufacturer = base.Field('Manufacturer')
    """The processor manufacturer"""

    model = base.Field('Model')
    """The product model number of this device"""

    max_speed_mhz = base.Field('MaxSpeedMHz', adapter=int)
    """The maximum clock speed of the processor in MHz."""

    total_cores = base.Field('TotalCores', adapter=int)
    """The total number of cores contained in this processor"""

    total_threads = base.Field('TotalThreads', adapter=int)
    """The total number of execution threads supported by this processor"""

    def __init__(self, connector, identity, redfish_version=None):
        """A class representing a Processor

        :param connector: A Connector instance
        :param identity: The identity of the processor
        :param redfish_version: The version of RedFish. Used to construct
            the object according to schema of the given version.
        """
        super(Processor, self).__init__(connector, identity, redfish_version)


class ProcessorCollection(base.ResourceCollectionBase):

    @property
    def _resource_type(self):
        return Processor

    _summary = None
    """The summary of processors of the system in general detail"""

    @property
    def summary(self):
        """Property to provide ProcessorSummary info

        It is calculated once when the first time it is queried. On refresh,
        this property gets reset.

        :returns: A namedtuple containing the ``count`` of processors
            in regards to logical CPUs, and their ``architecture``.
        """
        if self._summary is None:
            count, architecture = 0, None
            for proc in self.get_members():
                # Note(deray): It attempts to detect the number of CPU cores.
                # It returns the number of logical CPUs.
                if proc.total_threads is not None:
                    count += proc.total_threads

                # Note(deray): Bail out of checking the architecture info
                # if you have already got hold of any one of the processors'
                # architecture information.
                if (architecture is None
                        and proc.processor_architecture is not None):
                    architecture = proc.processor_architecture

            self._summary = ProcessorSummary(count=count,
                                             architecture=architecture)

        return self._summary

    def __init__(self, connector, path, redfish_version=None):
        """A class representing a ProcessorCollection

        :param connector: A Connector instance
        :param path: The canonical path to the Processor collection resource
        :param redfish_version: The version of RedFish. Used to construct
            the object according to schema of the given version.
        """
        super(ProcessorCollection, self).__init__(connector, path,
                                                  redfish_version)

    def refresh(self):
        """Refresh the resource"""
        super(ProcessorCollection, self).refresh()
        # Reset summary attribute
        self._summary = None
