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

import abc
import logging

import six

from sushy.resources import base


LOG = logging.getLogger(__name__)


class OEMField(base.Field):
    """Marker class for OEM specific fields."""


def _collect_oem_fields(resource):
    """Collect OEM fields from resource.

    :param resource: OEMExtensionResourceBase instance.
    :returns: generator of tuples (key, field)
    """
    for attr in dir(resource.__class__):
        field = getattr(resource.__class__, attr)
        if isinstance(field, OEMField):
            yield (attr, field)


def _collect_base_fields(resource):
    """Collect base fields from resource.

    :param resource: OEMExtensionResourceBase instance.
    :returns: generator of tuples (key, field)
    """
    for attr in dir(resource.__class__):
        field = getattr(resource.__class__, attr)
        if not isinstance(field, OEMField) and isinstance(field, base.Field):
            yield (attr, field)


@six.add_metaclass(abc.ABCMeta)
class OEMCompositeField(base.CompositeField, OEMField):
    """CompositeField for OEM fields."""


class OEMListField(base.ListField, OEMField):
    """ListField for OEM fields."""


class OEMDictionaryField(base.DictionaryField, OEMField):
    """DictionaryField for OEM fields."""


class OEMMappedField(base.MappedField, OEMField):
    """MappedField for OEM fields."""


@six.add_metaclass(abc.ABCMeta)
class OEMExtensionResourceBase(object):

    def __init__(self, resource, oem_property_name, *args, **kwargs):
        """A class representing the base of any resource OEM extension

        Invokes the ``refresh()`` method for the first time from here
        (constructor).
        :param resource: The parent Sushy resource instance
        :param oem_property_name: the unique OEM identifier string
        """
        if not resource:
            raise ValueError('"resource" argument cannot be void')
        if not isinstance(resource, base.ResourceBase):
            raise TypeError('"resource" argument must be a ResourceBase')

        self.core_resource = resource
        self.oem_property_name = oem_property_name
        self.refresh()

    def _parse_oem_attributes(self):
        """Parse the OEM extension attributes of a resource."""
        oem_json_body = (self.core_resource.json.get('Oem').
                         get(self.oem_property_name))
        for attr, field in _collect_oem_fields(self):
            # Hide the Field object behind the real value
            setattr(self, attr, field._load(oem_json_body, self))

        for attr, field in _collect_base_fields(self):
            # Hide the Field object behind the real value
            setattr(self, attr, field._load(self.core_resource.json, self))

    def refresh(self):
        """Refresh the attributes of the resource extension.

        Freshly parses the resource OEM attributes via
        ``_parse_oem_attributes()`` method.
        """
        self._parse_oem_attributes()
