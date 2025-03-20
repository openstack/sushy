# Copyright (c) 2022 SAP SE or its subsidiaries.
#
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

from sushy.resources import base


class DellAttributes(base.ResourceBase):
    identity = base.Field('Id', required=True)
    """The DellAttributes resource identity string"""

    name = base.Field('Name')
    """The name of the resource"""

    description = base.Field('Description')
    """Human-readable description of the DellAttributes resource"""

    _attribute_registry = base.Field('AttributeRegistry')
    """The Resource ID of the AttributeRegistry for this resource"""

    attributes = base.Field('Attributes')
    """Vendor-specific key-value dict of effective DellAttributes

    They cannot be updated directly.
    To update use :py:func:`~set_attribute` or :py:func:`~set_attributes`
    """

    def set_attribute(self, key, value):
        """Update an attribute

        Attribute update is not immediate but requires system restart.
        Committed attributes can be checked at :py:attr:`~pending_attributes`
        property

        :param key: Attribute name
        :param value: Attribute value
        """
        self.set_attributes({key: value})

    def set_attributes(self, value):
        """Update many attributes at once

        Attribute update is not immediate but requires system restart.
        Committed attributes can be checked at :py:attr:`~pending_attributes`
        property

        :param value: Key-value pairs for attribute name and value
        :param apply_time: When to update the attributes. Optional.
            An :py:class:`sushy.ApplyTime` value.
        """
        payload = {'Attributes': value}
        result = self._conn.patch(self.path, data=payload)
        if result.status_code in (200, 202):
            for k, v in value.items():
                self.attributes[k] = v

    def get_attribute_registry(self, language='en'):
        """Get the Attribute Registry associated with this resource

        :param language: RFC 5646 language code for Message Registries.
            Indicates language of registry to be used. Defaults to 'en'.
        :returns: the DellAttributes Attribute Registry
        """
        return self._get_registry(self._attribute_registry,
                                  language=language,
                                  description='Dell attribute registry')
