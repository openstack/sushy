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
# http://redfish.dmtf.org/schemas/v1/Drive.v1_4_0.json

import logging

from sushy import exceptions
from sushy.resources import base
from sushy.resources import common
from sushy.resources import constants as res_cons
from sushy.resources.system.storage import volume
from sushy import utils

LOG = logging.getLogger(__name__)


class Drive(base.ResourceBase):
    """This class represents a disk drive or other physical storage medium."""

    block_size_bytes = base.Field('BlockSizeBytes', adapter=utils.int_or_none)
    """The size of the smallest addressable unit of this drive in bytes"""

    capacity_bytes = base.Field('CapacityBytes', adapter=utils.int_or_none)
    """The size in bytes of this Drive"""

    identifiers = common.IdentifiersListField('Identifiers', default=[])
    """The Durable names for the drive"""

    identity = base.Field('Id', required=True)
    """The Drive identity string"""

    indicator_led = base.MappedField('IndicatorLED', res_cons.IndicatorLED)
    """Whether the indicator LED is lit or off"""

    manufacturer = base.Field('Manufacturer')
    """This is the manufacturer of this drive"""

    media_type = base.Field('MediaType')
    """The type of media contained in this drive"""

    model = base.Field('Model')
    """This is the model number for the drive"""

    name = base.Field('Name')
    """The name of the resource"""

    part_number = base.Field('PartNumber')
    """The part number for this drive"""

    protocol = base.MappedField('Protocol', res_cons.Protocol)
    """Protocol this drive is using to communicate to the storage controller"""

    revision = base.Field("Revision")
    """The firmware/hardware version of the drive."""

    serial_number = base.Field('SerialNumber')
    """The serial number for this drive"""

    status = common.StatusField('Status')
    """This type describes the status and health of the drive"""

    @property
    @utils.cache_it
    def volumes(self):
        """A list of volumes that this drive is part of.

        Volumes that this drive either wholly or only partially contains.

        :raises: MissingAttributeError if '@odata.id' field is missing.
        :returns: A list of `Volume` instances
        """
        paths = utils.get_sub_resource_path_by(
            self, ["Links", "Volumes"], is_collection=True)

        return [volume.Volume(self._conn, path,
                              redfish_version=self.redfish_version,
                              registries=self.registries)
                for path in paths]

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
