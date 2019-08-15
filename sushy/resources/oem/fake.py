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
from sushy.resources import common
from sushy.resources.oem import base as oem_base

LOG = logging.getLogger(__name__)


class ProductionLocationField(base.CompositeField):
    facility_name = base.Field('FacilityName')
    country = base.Field('Country')


class ContosoActionsField(base.CompositeField):
    reset = common.ResetActionField('#Contoso.Reset')


class FakeOEMSystemExtension(oem_base.OEMResourceBase):

    data_type = base.Field('@odata.type')
    production_location = ProductionLocationField('ProductionLocation')
    _actions = ContosoActionsField('Actions')

    def get_reset_system_path(self):
        return self._actions.reset.target_uri


def get_extension(*args, **kwargs):
    return FakeOEMSystemExtension
