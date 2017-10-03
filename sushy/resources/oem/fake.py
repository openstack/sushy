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

import logging

from sushy.resources import base
from sushy.resources.oem import base as oem_base

LOG = logging.getLogger(__name__)


class ProductionLocationField(oem_base.OEMCompositeField):
    facility_name = base.Field('FacilityName')
    country = base.Field('Country')


class FakeOEMSystemExtension(oem_base.OEMExtensionResourceBase):

    data_type = oem_base.OEMField('@odata.type')
    production_location = ProductionLocationField('ProductionLocation')
    reset_action = base.Field(['Actions', 'Oem', '#Contoso.Reset'])

    def __init__(self, resource, *args, **kwargs):
        """A class representing ComputerSystem OEM extension for Contoso

        :param resource: The parent System resource instance
        """
        super(FakeOEMSystemExtension, self).__init__(
            resource, 'Contoso', *args, **kwargs)

    def get_reset_system_path(self):
        return self.reset_action.get('target')
