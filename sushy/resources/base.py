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
import enum
import io
import json
import logging
import zipfile

import pkg_resources

from sushy import exceptions
from sushy.resources import constants
from sushy.resources import oem
from sushy import utils


LOG = logging.getLogger(__name__)


class Field(object):
    """Definition for fields fetched from JSON."""

    def __init__(self, path, required=False, default=None,
                 adapter=lambda x: x):
        """Create a field definition.

        :param path: JSON field to fetch the value from. Either a string,
            or a list of strings in case of a nested field.
        :param required: whether this field is required. Missing required,
            but not defaulted, fields result in MissingAttributeError.
        :param default: the default value to use when the field is missing.
        :param adapter: a function to call to transform and/or validate
            the received value. UnicodeError, ValueError or TypeError from
            this call are reraised as MalformedAttributeError.
        """
        if not callable(adapter):
            raise TypeError("Adapter must be callable")

        if not isinstance(path, list):
            path = [path]

        elif not path:
            raise ValueError('Path cannot be empty')

        self._path = path
        self._required = required
        self._default = default
        self._adapter = adapter

    def _get_item(self, dct, key_or_callable, **context):
        if not callable(key_or_callable):
            return dct[key_or_callable]

        for candidate_key in dct:
            if key_or_callable(
                    candidate_key, value=dct[candidate_key], **context):
                return dct[candidate_key]

        raise KeyError(key_or_callable)

    def _load(self, body, resource, nested_in=None):
        """Load this field from a JSON object.

        :param body: parsed JSON body.
        :param resource: ResourceBase instance for which the field is loaded.
        :param nested_in: parent resource path (for error reporting only),
            must be a list of strings or None.
        :raises: MissingAttributeError if a required field is missing
            and not defaulted.
        :raises: MalformedAttributeError on invalid field value or type.
        :returns: loaded and verified value
        """
        name = self._path[-1]
        for path_item in self._path[:-1]:
            body = body.get(path_item, {})

        try:
            item = self._get_item(body, name)

        except KeyError:
            if self._required:
                path = (nested_in or []) + self._path

                if self._default is None:
                    raise exceptions.MissingAttributeError(
                        attribute='/'.join(path),
                        resource=resource.path)

                logging.warning(
                    'Applying default "%s" on required, but missing '
                    'attribute "%s"' % (self._default, path))

            # Do not run the adapter on the default value
            return self._default

        # NOTE(etingof): this is just to account for schema violation
        if item is None:
            return

        try:
            return self._adapter(item)

        except (UnicodeError, ValueError, TypeError) as exc:
            path = (nested_in or []) + self._path
            raise exceptions.MalformedAttributeError(
                attribute='/'.join(path),
                resource=resource.path,
                error=exc)


def _collect_fields(resource):
    """Collect fields from the JSON.

    :param resource: ResourceBase or CompositeField instance.
    :returns: generator of tuples (key, field)
    """
    for attr in dir(resource.__class__):
        field = getattr(resource.__class__, attr)
        if isinstance(field, Field):
            yield (attr, field)


class CompositeField(collections.abc.Mapping, Field, metaclass=abc.ABCMeta):
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
    # https://docs.python.org/3/library/collections.abc.html#collections.abc.Mapping

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

    def __getitem__(self, key):
        return getattr(self, key)


class LinksField(CompositeField):
    """Reference to linked resources."""
    oem_vendors = Field('Oem', adapter=list)


class DictionaryField(Field):
    """Base class for fields consisting of dictionary of several sub-fields."""

    def __init__(self, *args, **kwargs):
        super(DictionaryField, self).__init__(*args, **kwargs)
        self._subfields = dict(_collect_fields(self))

    def _load(self, body, resource, nested_in=None):
        """Load the dictionary.

        :param body: parent JSON body.
        :param resource: parent resource.
        :param nested_in: parent resource name (for error reporting only).
        :returns: a new dictionary object containing subfields.
        """
        nested_in = (nested_in or []) + self._path
        values = super(DictionaryField, self)._load(body, resource)
        if values is None:
            return None

        instances = {}
        for key, value in values.items():
            instance_value = copy.copy(self)
            for attr, field in self._subfields.items():
                # Hide the Field object behind the real value
                setattr(instance_value, attr, field._load(value,
                                                          resource,
                                                          nested_in))
            instances[key] = instance_value

        return instances

    def __getitem__(self, key):
        return getattr(self, key)


class MappedField(Field):
    """Field taking real value from a mapping."""

    def __init__(self, field, mapping, required=False, default=None):
        """Create a mapped field definition.

        :param field: JSON field to fetch the value from. This can be either
            a string or a list of string. In the latter case, the value will
            be fetched from a nested object.
        :param mapping: a mapping to take values from, a dictionary or
            an enumeration.
        :param required: whether this field is required. Missing required,
            but not defaulted, fields result in MissingAttributeError.
        :param default: the default value to use when the field is missing.
            This value is not matched against the mapping.
        """
        if isinstance(mapping, type) and issubclass(mapping, enum.Enum):
            def adapter(value):
                try:
                    return mapping(value)
                except ValueError:
                    return None

        elif isinstance(mapping, collections.abc.Mapping):
            adapter = mapping.get
        else:
            raise TypeError("The mapping argument must be a mapping or "
                            "an enumeration")

        super(MappedField, self).__init__(
            field, required=required, default=default, adapter=adapter)


class MappedListField(Field):
    """Field taking a list of values with a mapping for the values

    Given JSON {'field':['xxx', 'yyy']}, a sushy resource definition and
    mapping {'xxx':'a', 'yyy':'b'}, the sushy object to come out will be like
    resource.field = ['a', 'b']
    """

    def __init__(self, field, mapping, required=False, default=None):
        """Create a mapped list field definition.

        :param field: JSON field to fetch the list of values from.
        :param mapping: a mapping for the list elements.
        :param required: whether this field is required. Missing required,
            but not defaulted, fields result in MissingAttributeError.
        :param default: the default value to use when the field is missing.
        """
        if isinstance(mapping, type) and issubclass(mapping, enum.Enum):
            def adapter(value):
                try:
                    return mapping(value)
                except ValueError:
                    return None

        elif isinstance(mapping, collections.abc.Mapping):
            adapter = mapping.get
        else:
            raise TypeError("The mapping argument must be a mapping or "
                            "an enumeration")

        self._mapping_adapter = adapter
        super(MappedListField, self).__init__(
            field, required=required, default=default,
            adapter=lambda x: x)

    def _load(self, body, resource, nested_in=None):
        """Load the mapped list.

        :param body: parent JSON body.
        :param resource: parent resource.
        :param nested_in: parent resource name (for error reporting only).
        :returns: a new list object containing the mapped values.
        """
        nested_in = (nested_in or []) + self._path
        values = super(MappedListField, self)._load(body, resource)

        if values is None:
            return

        instances = [self._mapping_adapter(value) for value in values
                     if self._mapping_adapter(value) is not None]

        return instances


class MessageListField(ListField):
    """List of messages with details of settings update status"""

    message_id = Field('MessageId')
    """The key for this message which can be used
    to look up the message in a message registry
    """

    message = Field('Message')
    """Human readable message, if provided"""

    severity = MappedField('Severity', constants.Severity)
    """Severity of the error"""

    resolution = Field('Resolution')
    """Used to provide suggestions on how to resolve
    the situation that caused the error
    """

    _related_properties = Field('RelatedProperties')
    """List of properties described by the message"""

    message_args = Field('MessageArgs')
    """List of message substitution arguments for the message
    referenced by `message_id` from the message registry
    """


class FieldData(object):
    """Contains data to be used when constructing Fields"""

    def __init__(self, status_code, headers, json_doc):
        """Initializes the FieldData instance"""
        self._status_code = status_code
        self._headers = headers
        self._json_doc = json_doc

    @property
    def status_code(self):
        """The status code"""
        return self._status_code

    @property
    def headers(self):
        """The headers"""
        return self._headers

    @property
    def json_doc(self):
        """The parsed JSON body"""
        return self._json_doc


class AbstractDataReader(object, metaclass=abc.ABCMeta):

    def set_connection(self, connector, path):
        """Sets mandatory connection parameters

        :param connector: A Connector instance
        :param path: path of the resource
        """
        self._conn = connector
        self._path = path

    @abc.abstractmethod
    def get_data(self):
        """Based on data source get data and parse to JSON"""


class JsonDataReader(AbstractDataReader):
    """Gets the data from HTTP response given by path"""

    def get_data(self):
        """Gets JSON file from URI directly"""
        data = self._conn.get(path=self._path)

        json_data = data.json() if data.content else {}

        return FieldData(data.status_code, data.headers, json_data)


class JsonPublicFileReader(AbstractDataReader):
    """Loads the data from the Internet"""

    def get_data(self):
        """Get JSON file from full URI"""
        data = self._conn.get(self._path)

        return FieldData(data.status_code, data.headers, data.json())


class JsonArchiveReader(AbstractDataReader):
    """Gets the data from JSON file in archive"""

    def __init__(self, archive_file):
        """Initializes the reader

        :param archive_file: file name of JSON file in archive
        """
        self._archive_file = archive_file

    def get_data(self):
        """Gets JSON file from archive. Currently supporting ZIP only"""

        data = self._conn.get(path=self._path)
        if data.headers.get('content-type') == 'application/zip':
            try:
                archive = zipfile.ZipFile(io.BytesIO(data.content))
                json_data = json.loads(archive.read(self._archive_file)
                                       .decode(encoding='utf-8'))
                return FieldData(data.status_code, data.headers, json_data)
            except (zipfile.BadZipfile, ValueError) as e:
                raise exceptions.ArchiveParsingError(
                    path=self._path, error=e)
        else:
            LOG.error('Support for %(type)s not implemented',
                      {'type': data.headers['content-type']})

            return FieldData(data.status_code, data.headers, None)


class JsonPackagedFileReader(AbstractDataReader):
    """Gets the data from packaged file given by path"""

    def __init__(self, resource_package_name):
        """Initializes the reader

        :param resource_package: Python package/module name
        """
        self._resource_package_name = resource_package_name

    def get_data(self):
        """Gets JSON file from packaged file denoted by path"""

        with pkg_resources.resource_stream(self._resource_package_name,
                                           self._path) as resource:
            json_data = json.loads(resource.read().decode(encoding='utf-8'))
            return FieldData(None, None, json_data)


def get_reader(connector, path, reader=None):
    """Create and configure the reader.

    :param connector: A Connector instance
    :param path: sub-URI path to the resource.
    :param reader: Reader to use to fetch JSON data.
    :returns: the reader
    """
    if reader is None:
        reader = JsonDataReader()
    reader.set_connection(connector, path)

    return reader


class ResourceBase(object, metaclass=abc.ABCMeta):

    redfish_version = None
    """The Redfish version"""

    _oem_vendors = Field('Oem', adapter=list)
    """The list of OEM extension names for this resource."""

    links = LinksField('Links')

    _log_resource_body = True
    """Whether to log the whole resource body in debug mode."""

    def __init__(self,
                 connector,
                 path='',
                 redfish_version=None,
                 registries=None,
                 reader=None,
                 json_doc=None,
                 root=None):
        """A class representing the base of any Redfish resource

        Invokes the ``refresh()`` method of resource for the first
        time from here (constructor).
        :param connector: A Connector instance
        :param path: sub-URI path to the resource.
        :param redfish_version: The version of Redfish. Used to construct
            the object according to schema of the given version.
        :param registries: Dict of Redfish Message Registry objects to be
            used in any resource that needs registries to parse messages
        :param reader: Reader to use to fetch JSON data.
        :param json_doc: parsed JSON document in form of Python types.
        :param root: Sushy root object. Empty for Sushy root itself.
        """
        self._conn = connector
        self._path = path
        self._json = None
        self.redfish_version = redfish_version
        self._registries = registries
        # Note(deray): Indicates if the resource holds stale data or not.
        # Starting off with True and eventually gets set to False when
        # attribute values are fetched.
        self._is_stale = True

        self._reader = get_reader(connector, path, reader)
        self._root = root
        self.refresh(json_doc=json_doc)

    def _get_value(self, val):
        """Iterate through the input to get values for all attributes

        :param val: Either a value or a resource
        :returns: Attribute value, which may be a dictionary
        """
        if isinstance(val, dict):
            subfields = {}
            for key, s_val in val.items():
                subfields[key] = self._get_value(s_val)
            return subfields

        elif isinstance(val, list):
            return [self._get_value(val[i]) for i in range(len(val))]

        elif (isinstance(val, DictionaryField)
              or isinstance(val, CompositeField)
              or isinstance(val, ListField)):
            subfields = {}
            for attr, field in val._subfields.items():
                subfields[attr] = self._get_value(val.__getitem__(attr))
            return subfields

        return val

    def _get_registry(self, identity, language='en', description='registry'):
        """Get a registry with the given identity.

        :param identity: The registry identity.
        :param language: RFC 5646 language code for Message Registries.
            Indicates language of registry to be used. Defaults to 'en'.
        :param description: Human-readable description to use in logging.
        :returns: the corresponding registry object or None.
        """
        registries = self._registries
        if not registries:
            LOG.info('No %s is available', description)
            return None

        for key, registry in registries.items():
            if (registry
                    and identity in (key, registry.identity)):
                # NOTE(iurygregory): some registries may have "en-US"
                # as their language, in this case we can check if the
                # registry language starts with the requested language.
                registry_language = registry.language.lower().split('-', 1)[0]
                if (language != registry.language
                        and language.lower() != registry_language):
                    LOG.debug('Found %(descr)s but its language %(reg_lang)s '
                              'does not match the requested %(lang)s',
                              {'descr': description,
                               'lang': language,
                               'reg_lang': registry.language})
                    continue

                return registry

        avail = ', '.join(f'{reg.identity} ({reg.language})'
                          for reg in registries.values())
        LOG.info('%(descr)s %(registry)s not available for language %(lang)s; '
                 'available are: %(avail)s',
                 {'descr': description,
                  'registry': self._attribute_registry,
                  'lang': language,
                  'avail': avail})
        return None

    def _parse_attributes(self, json_doc):
        """Parse the attributes of a resource.

        Parsed JSON fields are set to `self` as declared in the class.

        :param json_doc: parsed JSON document in form of Python types
        :returns: dictionary of attribute/values after parsing
        """
        settings = {}
        for attr, field in _collect_fields(self):
            # Hide the Field object behind the real value
            setattr(self, attr, field._load(json_doc, self))

            # Get the attribute/value pairs that have been parsed
            settings[attr] = self._get_value(getattr(self, attr))

        return settings

    def _get_etag(self):
        """Returns the ETag of the HTTP request if any was specified.

        :returns ETag or None
        """
        return self._get_headers().get('ETag')

    def _get_headers(self):
        """Returns the HTTP headers of the request for the resource.

        :returns: dict of HTTP headers
        """
        return self._reader.get_data()._headers

    def _allow_patch(self):
        """Returns if the resource supports the PATCH HTTP method.

        If the resource supports the PATCH HTTP method for updates,
        it will return it in the Allow HTTP header.
        :returns: Boolean flag if PATCH is supported or not
        """
        allow_header = self._get_headers().get('Allow', '')
        methods = set([h.strip().upper() for h in allow_header.split(',')])
        return "PATCH" in methods

    def refresh(self, force=True, json_doc=None):
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
        :param json_doc: parsed JSON document in form of Python types.
        :raises: ResourceNotFoundError
        :raises: ConnectionError
        :raises: HTTPError
        """
        # Note(deray): Don't re-fetch / invalidate the sub-resources if the
        # resource is "_not_ stale" (i.e. fresh) OR _not_ forced.
        if not self._is_stale and not force:
            return

        if json_doc:
            self._json = json_doc
        else:
            self._json = self._reader.get_data().json_doc

        attributes = self._parse_attributes(self._json)
        LOG.debug('Received representation of %(type)s %(path)s: %(json)s',
                  {'type': self.__class__.__name__,
                   'path': self._path,
                   'json': (attributes if self._log_resource_body
                            else '<stripped>')})
        self._do_refresh(force)

        # Mark it fresh
        self._is_stale = False

    def _do_refresh(self, force):
        """Primitive method to be overridden by refresh related activities.

        Derived classes are supposed to override this method with the
        resource specific refresh operations to be performed. This is a
        primitive method in the paradigm of Template design pattern.

        As for the base implementation of this method the approach taken is:
        On refresh, all sub-resources are marked as stale. That means
        invalidate (or undefine) the exposed attributes for nested resources
        for fresh evaluation in subsequent calls to those exposed attributes.
        In other words greedy-refresh is not done for them, unless forced by
        ``force`` argument.

        :param force: should force refresh the resource and its sub-resources,
            if set to True.
        :raises: ResourceNotFoundError
        :raises: ConnectionError
        :raises: HTTPError
        """
        utils.cache_clear(self, force_refresh=force)

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
    def oem_vendors(self):
        return list(
            set((self._oem_vendors or []) + (self.links.oem_vendors or []))
        )

    @property
    def json(self):
        return self._json

    @property
    def path(self):
        return self._path

    def clone_resource(self, new_resource, path=''):
        """Instantiate given resource using existing BMC connection context"""
        return new_resource(
            self._conn, path or self.path,
            redfish_version=self.redfish_version,
            reader=self._reader,
            root=self.root)

    @property
    def resource_name(self):
        return utils.camelcase_to_underscore_joined(self.__class__.__name__)

    def get_oem_extension(self, vendor):
        """Get the OEM extension instance for this resource by OEM vendor

        :param vendor: the OEM vendor string which is the vendor-specific
            extensibility identifier. Examples are 'Contoso', 'Hpe'.
            Possible value can be got from ``oem_vendors`` attribute.
        :returns: the Redfish resource OEM extension instance.
        :raises: OEMExtensionNotFoundError
        """
        return oem.get_resource_extension_by_vendor(
            self.resource_name, vendor, self)

    @property
    def registries(self):
        return self._registries

    @property
    def root(self):
        return self._root


class ResourceLinksBase(ResourceBase, metaclass=abc.ABCMeta):

    def __init__(self, connector, path, redfish_version=None, registries=None,
                 root=None):
        """A class representing the base of any Redfish resource collection

        It gets inherited from ``ResourceBase`` and invokes the base class
        constructor.
        :param connector: A Connector instance
        :param path: sub-URI path to the resource collection.
        :param redfish_version: The version of Redfish. Used to construct
            the object according to schema of the given version.
        :param registries: Dict of Redfish Message Registry objects to be
            used in any resource that needs registries to parse messages.
        :param root: Sushy root object. Empty for Sushy root itself.
        """
        super().__init__(connector, path, redfish_version, registries,
                         root=root)
        LOG.debug('Received %(count)d member(s) for %(type)s %(path)s',
                  {'count': len(self.members_identities),
                   'type': self.__class__.__name__, 'path': self._path})

    @property
    @abc.abstractmethod
    def members_identities(self):
        """A sequence with members identities"""

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
        return self._resource_type(
            self._conn, identity, redfish_version=self.redfish_version,
            registries=self.registries,
            root=self.root)

    @utils.cache_it
    def get_members(self):
        """Return a list of ``_resource_type`` objects present in collection

        :returns: A list of ``_resource_type`` objects
        """
        return [self.get_member(id_) for id_ in self.members_identities]


class ResourceCollectionBase(ResourceLinksBase):

    name = Field('Name')
    """The name of the collection"""

    members_identities = Field('Members', default=[],
                               adapter=utils.get_members_identities)
    """A tuple with the members identities"""


class MutableResourceCollectionBase(ResourceCollectionBase):

    def _create_member(self, values):
        """Create a new member of this collection.

        :param values: Fields to set on creation.
        :return: Created resource or None if it was not returned by the server.
        """
        response = self._conn.post(self._path, data=values)
        self.invalidate(force_refresh=True)

        location = response.headers.get('Location')
        if location is None:
            return None

        return self._resource_type(
            self._conn, location,
            redfish_version=self.redfish_version,
            registries=self.registries,
            root=self.root)

    def delete_member(self, identity):
        """Delete the given member of the collection."""
        self._conn.delete(identity)
        self.invalidate(force_refresh=True)
