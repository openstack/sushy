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

# This is referred from Redfish standard schema.
# https://redfish.dmtf.org/schemas/v1/SwitchCollection.json

from sushy.resources import base


class DellSwitchConnectionListField(base.ListField):

    description = base.Field('Description')
    """The description of the Dell switch connection instance resource"""

    fqdd = base.Field('FQDD')
    """The fully qualified device device descriptor of IDRAC or NIC"""

    identity = base.Field('Id', required=True)
    """The switch connection identity string"""

    instance_id = base.Field('InstanceID', required=True)
    """The switch connection instance identity string"""

    name = base.Field('Name', required=True)
    """The switch connection name"""

    stale_data = base.Field('StaleData', required=True)
    """The switch connection data status"""

    switch_connection_id = base.Field('SwitchConnectionID', required=True)
    """The switch connection device identity string"""

    switch_port_connection_id = base.Field('SwitchPortConnectionID',
                                           required=True)
    """The switch connection port identity string"""


class DellSwitchConnectionCollection(base.ResourceBase):

    @property
    def _resource_type(self):
        return DellSwitchConnectionListField
    description = base.Field('Description')
    """The description of the Dell switch connection collection instance
    resource"""

    members = DellSwitchConnectionListField('Members', default=[])
    """Uniquely identifies the member within the collection."""
