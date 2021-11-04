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
# https://redfish.dmtf.org/schemas/Processor.v1_3_0.json

import collections
import logging

from sushy import exceptions
from sushy.resources import base
from sushy.resources import common
from sushy.resources.system import constants as sys_cons
from sushy import utils

# Representation of Summary of Processor information
ProcessorSummary = collections.namedtuple('ProcessorSummary',
                                          ['count', 'architecture'])
LOG = logging.getLogger(__name__)


class ProcessorIdField(base.CompositeField):

    effective_family = base.Field('EffectiveFamily')
    """The processor effective family"""

    effective_model = base.Field('EffectiveModel')
    """The processor effective model"""

    identification_registers = base.Field('IdentificationRegisters')
    """The processor identification registers"""

    microcode_info = base.Field('MicrocodeInfo')
    """The processor microcode info"""

    step = base.Field('Step')
    """The processor stepping"""

    vendor_id = base.Field('VendorID')
    """The processor vendor id"""


class Processor(base.ResourceBase):

    identity = base.Field('Id', required=True)
    """The processor identity string"""

    socket = base.Field('Socket')
    """The socket or location of the processor"""

    processor_type = base.MappedField('ProcessorType', sys_cons.ProcessorType)
    """The type of processor"""

    processor_architecture = base.MappedField('ProcessorArchitecture',
                                              sys_cons.ProcessorArchitecture)
    """The architecture of the processor"""

    instruction_set = base.MappedField('InstructionSet',
                                       sys_cons.InstructionSet)
    """The instruction set of the processor"""

    manufacturer = base.Field('Manufacturer')
    """The processor manufacturer"""

    model = base.Field('Model')
    """The product model number of this device"""

    max_speed_mhz = base.Field('MaxSpeedMHz', adapter=utils.int_or_none)
    """The maximum clock speed of the processor in MHz."""

    processor_id = ProcessorIdField('ProcessorId')
    """The processor id"""

    status = common.StatusField('Status')
    """The processor status"""

    total_cores = base.Field('TotalCores', adapter=utils.int_or_none)
    """The total number of cores contained in this processor"""

    total_threads = base.Field('TotalThreads', adapter=utils.int_or_none)
    """The total number of execution threads supported by this processor"""

    def __init__(self, connector, identity, redfish_version=None,
                 registries=None, root=None):
        """A class representing a Processor

        :param connector: A Connector instance
        :param identity: The identity of the processor
        :param redfish_version: The version of RedFish. Used to construct
            the object according to schema of the given version.
        :param registries: Dict of Redfish Message Registry objects to be
            used in any resource that needs registries to parse messages
        :param root: Sushy root object. Empty for Sushy root itself.
        """
        super(Processor, self).__init__(
            connector, identity, redfish_version=redfish_version,
            registries=registries, root=root)

    def _get_subprocessor_collection_path(self):
        """Helper function to find the SubProcessors path"""
        subproc_col = self.json.get('SubProcessors')
        if not subproc_col:
            raise exceptions.MissingAttributeError(
                attribute='SubProcessors', resource=self._path)
        return subproc_col.get('@odata.id')

    @property
    @utils.cache_it
    def sub_processors(self):
        """A reference to the collection of Sub-Processors"""
        return ProcessorCollection(
            self._conn, self._get_subprocessor_collection_path(),
            redfish_version=self.redfish_version, root=self.root)


class ProcessorCollection(base.ResourceCollectionBase):

    @property
    def _resource_type(self):
        return Processor

    @property
    @utils.cache_it
    def summary(self):
        """Property to provide ProcessorSummary info

        It is calculated once when the first time it is queried. On refresh,
        this property gets reset.

        :returns: A namedtuple containing the ``count`` of processors
            in regards to logical CPUs, and their ``architecture``.
        """
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

        return ProcessorSummary(count=count, architecture=architecture)

    def __init__(self, connector, path, redfish_version=None, registries=None,
                 root=None):
        """A class representing a ProcessorCollection

        :param connector: A Connector instance
        :param path: The canonical path to the Processor collection resource
        :param redfish_version: The version of RedFish. Used to construct
            the object according to schema of the given version.
        :param registries: Dict of Redfish Message Registry objects to be
            used in any resource that needs registries to parse messages
        :param root: Sushy root object. Empty for Sushy root itself.
        """
        super(ProcessorCollection, self).__init__(
            connector, path, redfish_version=redfish_version,
            registries=registries,
            root=root)
