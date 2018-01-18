# Copyright 2017 Red Hat, Inc.
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

import abc
import collections
import copy
import logging

import six

from sushy import exceptions
from sushy import utils


LOG = logging.getLogger(__name__)


class Field(object):
    """Definition for fields fetched from JSON."""

    def __init__(self, path, required=False, default=None,
                 adapter=lambda x: x):
        """Create a field definition.

        :param path: JSON field to fetch the value from. Either a string,
            or a list of strings in case of a nested field.
        :param required: whether this field is required. Missing required
            fields result in MissingAttributeError.
        :param default: the default value to use when the field is missing.
            Only has effect when the field is not required.
        :param adapter: a function to call to transform and/or validate
            the received value. UnicodeError, ValueError or TypeError from
            this call are reraised as MalformedAttributeError.
        """
        if not callable(adapter):
            raise TypeError("Adapter must be callable")

        if isinstance(path, six.string_types):
            path = [path]
        elif not path:
            raise ValueError('Path cannot be empty')

        self._path = path
        self._required = required
        self._default = default
        self._adapter = adapter

    def _load(self, body, resource, nested_in=None):
        """Load this field from a JSON object.

        :param body: parsed JSON body.
        :param resource: ResourceBase instance for which the field is loaded.
        :param nested_in: parent resource path (for error reporting only),
            must be a list of strings or None.
        :raises: MissingAttributeError if a required field is missing.
        :raises: MalformedAttributeError on invalid field value or type.
        :returns: loaded and verified value
        """
        name = self._path[-1]
        for path_item in self._path[:-1]:
            body = body.get(path_item, {})

        if name not in body:
            if self._required:
                path = (nested_in or []) + self._path
                raise exceptions.MissingAttributeError(
                    attribute='/'.join(path),
                    resource=resource.path)
            else:
                # Do not run the adapter on the default value
                return self._default

        try:
            value = self._adapter(body[name])
        except (UnicodeError, ValueError, TypeError) as exc:
            path = (nested_in or []) + self._path
            raise exceptions.MalformedAttributeError(
                attribute='/'.join(path),
                resource=resource.path,
                error=exc)

        return value


def _collect_fields(resource):
    """Collect fields from the JSON.

    :param resource: ResourceBase or CompositeField instance.
    :returns: generator of tuples (key, field)
    """
    for attr in dir(resource.__class__):
        field = getattr(resource.__class__, attr)
        if isinstance(field, Field):
            yield (attr, field)


@six.add_metaclass(abc.ABCMeta)
class CompositeField(collections.Mapping, Field):
    """Base class for fields consisting of several sub-fields."""

    def __init__(self, *args, **kwargs):
        super(CompositeField, self).__init__(*args, **kwargs)
        self._subfields = dict(_collect_fields(self))

    def _load(self, body, resource, nested_in=None):
        """Load the composite field.

        :param body: parent JSON body.
        :param resource: parent resource.
        :param nested_in: parent resource name (for error reporting only).
        :returns: a new object with sub-fields attached to it.
        """
        nested_in = (nested_in or []) + self._path
        value = super(CompositeField, self)._load(body, resource)
        if value is None:
            return None

        # We need a new instance, as this method is called a singleton instance
        # that is attached to a class (not instance) of a resource or another
        # CompositeField. We don't want to end up modifying this instance.
        instance = copy.copy(self)
        for attr, field in self._subfields.items():
            # Hide the Field object behind the real value
            setattr(instance, attr, field._load(value, resource, nested_in))

        return instance

    # Satisfy the mapping interface, see
    # https://docs.python.org/2/library/collections.html#collections.Mapping.

    def __getitem__(self, key):
        if key in self._subfields:
            return getattr(self, key)
        else:
            raise KeyError(key)

    def __len__(self):
        return len(self._subfields)

    def __iter__(self):
        return iter(self._subfields)


class ListField(Field):
    """Base class for fields consisting of a list of several sub-fields."""

    def __init__(self, *args, **kwargs):
        super(ListField, self).__init__(*args, **kwargs)
        self._subfields = dict(_collect_fields(self))

    def _load(self, body, resource, nested_in=None):
        """Load the field list.

        :param body: parent JSON body.
        :param resource: parent resource.
        :param nested_in: parent resource name (for error reporting only).
        :returns: a new list object containing subfields.
        """
        nested_in = (nested_in or []) + self._path
        values = super(ListField, self)._load(body, resource)
        if values is None:
            return None

        # Initialize the list that will contain each field instance
        instances = []
        for value in values:
            instance = copy.copy(self)
            for attr, field in self._subfields.items():
                # Hide the Field object behind the real value
                setattr(instance, attr, field._load(value,
                                                    resource,
                                                    nested_in))
            instances.append(instance)

        return instances


class MappedField(Field):
    """Field taking real value from a mapping."""

    def __init__(self, field, mapping, required=False, default=None):
        """Create a mapped field definition.

        :param field: JSON field to fetch the value from. This can be either
            a string or a list of string. In the latter case, the value will
            be fetched from a nested object.
        :param mapping: a mapping to take values from.
        :param required: whether this field is required. Missing required
            fields result in MissingAttributeError.
        :param default: the default value to use when the field is missing.
            Only has effect when the field is not required. This value is not
            matched against the mapping.
        """
        if not isinstance(mapping, collections.Mapping):
            raise TypeError("The mapping argument must be a mapping")

        super(MappedField, self).__init__(
            field, required=required, default=default,
            adapter=mapping.get)


@six.add_metaclass(abc.ABCMeta)
class ResourceBase(object):

    redfish_version = None
    """The Redfish version"""

    def __init__(self, connector, path='', redfish_version=None):
        """A class representing the base of any Redfish resource

        Invokes the ``refresh()`` method of resource for the first
        time from here (constructor).
        :param connector: A Connector instance
        :param path: sub-URI path to the resource.
        :param redfish_version: The version of RedFish. Used to construct
            the object according to schema of the given version.
        """
        self._conn = connector
        self._path = path
        self._json = None
        self.redfish_version = redfish_version
        # Note(deray): Indicates if the resource holds stale data or not.
        # Starting off with True and eventually gets set to False when
        # attribute values are fetched.
        self._is_stale = True

        self.refresh()

    def _parse_attributes(self):
        """Parse the attributes of a resource."""
        for attr, field in _collect_fields(self):
            # Hide the Field object behind the real value
            setattr(self, attr, field._load(self.json, self))

    def refresh(self, force=True):
        """Refresh the resource

        Freshly retrieves/fetches the resource attributes and invokes
        ``_parse_attributes()`` method on successful retrieval.
        It is recommended not to override this method in concrete ResourceBase
        classes. Resource classes can place their refresh specific operations
        in ``_do_refresh()`` method, if needed. This method represents the
        template method in the paradigm of Template design pattern.

        :param force: if set to False, will only refresh if the resource is
            marked as stale, otherwise neither it nor its subresources will
            be refreshed.
        :raises: ResourceNotFoundError
        :raises: ConnectionError
        :raises: HTTPError
        """
        # Note(deray): Don't re-fetch / invalidate the sub-resources if the
        # resource is "_not_ stale" (i.e. fresh) OR _not_ forced.
        if not self._is_stale and not force:
            return

        self._json = self._conn.get(path=self._path).json()
        LOG.debug('Received representation of %(type)s %(path)s: %(json)s',
                  {'type': self.__class__.__name__,
                   'path': self._path, 'json': self._json})
        self._parse_attributes()
        self._do_refresh(force)

        # Mark it fresh
        self._is_stale = False

    def _do_refresh(self, force):
        """Primitive method to be overridden by refresh related activities.

        Derived classes are supposed to override this method with the
        resource specific refresh operations to be performed. This is a
        primitive method in the paradigm of Template design pattern.

        :param force: should force refresh the resource and its sub-resources,
            if set to True.
        :raises: ResourceNotFoundError
        :raises: ConnectionError
        :raises: HTTPError
        """

    def invalidate(self, force_refresh=False):
        """Mark the resource as stale, prompting refresh() before getting used.

        If ``force_refresh`` is set to True, then it invokes ``refresh()``
        on the resource.

        :param force_refresh: will invoke refresh on the resource,
            if set to True.
        :raises: ResourceNotFoundError
        :raises: ConnectionError
        :raises: HTTPError
        """
        self._is_stale = True
        if force_refresh:
            self.refresh()

    @property
    def json(self):
        return self._json

    @property
    def path(self):
        return self._path


@six.add_metaclass(abc.ABCMeta)
class ResourceCollectionBase(ResourceBase):

    name = Field('Name')
    """The name of the collection"""

    members_identities = Field('Members', default=[],
                               adapter=utils.get_members_identities)
    """A tuple with the members identities"""

    def __init__(self, connector, path, redfish_version=None):
        """A class representing the base of any Redfish resource collection

        It gets inherited ``ResourceBase`` and invokes the base class
        constructor.
        :param connector: A Connector instance
        :param path: sub-URI path to the resource collection.
        :param redfish_version: The version of RedFish. Used to construct
            the object according to schema of the given version.
        """
        super(ResourceCollectionBase, self).__init__(connector, path,
                                                     redfish_version)
        LOG.debug('Received %(count)d member(s) for %(type)s %(path)s',
                  {'count': len(self.members_identities),
                   'type': self.__class__.__name__, 'path': self._path})

    @property
    @abc.abstractmethod
    def _resource_type(self):
        """The resource class that the collection contains.

        Override this property to specify the resource class that the
        collection contains.
        """

    def get_member(self, identity):
        """Given the identity return a ``_resource_type`` object

        :param identity: The identity of the ``_resource_type``
        :returns: The ``_resource_type`` object
        :raises: ResourceNotFoundError
        """
        return self._resource_type(self._conn, identity,
                                   redfish_version=self.redfish_version)

    def get_members(self):
        """Return a list of ``_resource_type`` objects present in collection

        :returns: A list of ``_resource_type`` objects
        """
        return [self.get_member(id_) for id_ in self.members_identities]
