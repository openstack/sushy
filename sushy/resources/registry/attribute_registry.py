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

# The Redfish standard schema that defines the AttributeRegistry is at:
# https://redfish.dmtf.org/schemas/v1/AttributeRegistry.v1_3_5.json

import logging

from sushy.resources import base

LOG = logging.getLogger(__name__)


class AttributeListField(base.ListField):

    name = base.Field('AttributeName', required=True)
    """The unique name for the attribute"""

    default_value = base.Field('DefaultValue')
    """The default value for the attribute"""

    attribute_type = base.Field('Type')
    """The attribute type"""

    unique = base.Field('IsSystemUniqueProperty', adapter=bool)
    """Indicates whether this attribute is unique for this system"""

    display_name = base.Field('DisplayName')
    """User-readable display string for attribute in the defined language"""

    immutable = base.Field('Immutable', adapter=bool)
    """An indication of whether this attribute is immutable"""

    read_only = base.Field('ReadOnly', adapter=bool)
    """An indication of whether this attribute is read-only"""

    reset_required = base.Field('ResetRequired', adapter=bool)
    """An indication of whether this attribute is read-only"""

    lower_bound = base.Field('LowerBound')
    """The lower limit for an integer attribute"""

    max_length = base.Field('MaxLength')
    """The maximum character length of the string attribute"""

    min_length = base.Field('MinLength')
    """The minimum character length of the string attribute"""

    upper_bound = base.Field('UpperBound')
    """The upper limit for an integer attribute"""

    allowable_values = base.Field('Value')
    """An array of the possible values for enumerated attribute values"""


class AttributeRegistryEntryField(base.CompositeField):

    attributes = AttributeListField('Attributes')
    """List of attributes in this registry"""

    # Vendors may have aditional items such as Dependencies, Menus, etc.
    # Only get the attributes.


class AttributeRegistry(base.ResourceBase):

    identity = base.Field('Id', required=True)
    """The Attribute registry identity string"""

    name = base.Field('Name', required=True)
    """The name of the attribute registry"""

    description = base.Field('Description')
    """Human-readable description of the registry"""

    language = base.Field('Language', required=True)
    """RFC 5646 compliant language code for the registry"""

    owning_entity = base.Field('OwningEntity', required=True)
    """Organization or company that publishes this registry"""

    registry_version = base.Field('RegistryVersion', required=True)
    """The version of this registry"""

    supported_systems = base.Field('SupportedSystems')
    """The system that this registry supports"""

    registry_entries = AttributeRegistryEntryField('RegistryEntries')
    """Field containing Attributes, Dependencies, Menus etc."""
