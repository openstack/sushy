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

import collections
import functools
import logging
import threading

from sushy import exceptions

LOG = logging.getLogger(__name__)

CACHE_ATTR_NAMES_VAR_NAME = '_cache_attr_names'


def revert_dictionary(dictionary):
    """Given a dictionary revert it's mapping

    :param dictionary: A dictionary to be reverted
    :returns: A dictionary with the keys and values reverted

    """
    return {v: k for k, v in dictionary.items()}


def get_members_identities(members):
    """Extract and return a tuple of members identities

    :param members: A list of members in JSON format
    :returns: A tuple containing the members paths

    """
    members_list = []
    for member in members:
        path = member.get('@odata.id')
        if not path:
            LOG.warning('Could not find the \'@odata.id\' attribute for '
                        'member %s', member)
            continue
        members_list.append(path.rstrip('/'))

    return tuple(members_list)


def int_or_none(x):
    """Given a value x it cast as int or None

    :param x: The value to transform and return
    :returns: Either None or x cast to an int

    """
    if x is None:
        return None
    return int(x)


def bool_or_none(x):
    """Given a value x this method returns either a bool or None

    :param x: The value to transform and return
    :returns: Either None or x cast to a bool

    """
    if x is None:
        return None
    return bool(x)


def get_sub_resource_path_by(resource, subresource_name, is_collection=False):
    """Helper function to find the subresource path

    :param resource: ResourceBase instance on which the name
        gets queried upon.
    :param subresource_name: name of the resource field to
        fetch the '@odata.id' from.
    :param is_collection: if `True`, expect a list of resources to
        fetch the '@odata.id' from.
    :returns: Resource path (if `is_collection` is `False`) or
        a list of resource paths (if `is_collection` is `True`).
    """
    if not subresource_name:
        raise ValueError('"subresource_name" cannot be empty')

    if not isinstance(subresource_name, list):
        subresource_name = [subresource_name]

    body = resource.json
    for path_item in subresource_name:
        body = body.get(path_item, {})

    if not body:
        raise exceptions.MissingAttributeError(
            attribute='/'.join(subresource_name), resource=resource.path)

    elements = []

    try:
        if is_collection:
            for element in body:
                elements.append(element['@odata.id'])
            return elements

        return body['@odata.id']

    except (TypeError, KeyError):
        attribute = '/'.join(subresource_name)
        if is_collection:
            attribute += '[%s]' % len(elements)
        attribute += '/@odata.id'
        raise exceptions.MissingAttributeError(
            attribute=attribute, resource=resource.path)


def max_safe(iterable, default=0):
    """Helper wrapper over builtin max() function.

    This function is just a wrapper over builtin max() w/o ``key`` argument.
    The ``default`` argument specifies an object to return if the provided
    ``iterable`` is empty. Also it filters out the None type values.

    :param iterable: an iterable
    :param default: 0 by default
    """

    try:
        return max(x for x in iterable if x is not None)
    except ValueError:
        # TypeError is not caught here as that should be thrown.
        return default


def setdefaultattr(obj, name, default):
    """Python's ``dict.setdefault`` applied on Python objects.

    If name is an attribute with obj, return its value. If not, set name
    attribute with a value of default and return default.

    :param obj: a python object
    :param name: name of attribute
    :param default: default value to be set
    """

    try:
        return getattr(obj, name)
    except AttributeError:
        setattr(obj, name, default)
    return default


def cache_it(res_accessor_method):
    """Utility decorator to cache the return value of the decorated method.

    This decorator is to be used with any Sushy resource class method.
    This will internally create an attribute on the resource namely
    ``_cache_<decorated_method_name>``. This is referred to as the "caching
    attribute". This attribute will eventually hold the resultant value from
    the method invocation (when method gets first time called) and for every
    subsequent calls to that method this cached value will get returned. It
    expects the decorated method to contain its own logic of evaluation.

    This also assigns a variable named ``_cache_attr_names`` on the resource.
    This variable maintains a collection of all the existing
    "caching attribute" names.

    To invalidate or clear the cache use :py:func:`~cache_clear`.
    Usage:

    .. code-block:: python

      class SomeResource(base.ResourceBase):
        ...
        @cache_it
        def get_summary(self):
          # do some calculation and return the result
          # and this result will be cached.
          return result
        ...
        def _do_refresh(self, force):
          cache_clear(self, force)

    If the returned value is a Sushy resource instance or a sequence whose
    element is of type Sushy resource it handles the case of calling the
    ``refresh()`` method of that resource. This is done to avoid unnecessary
    recreation of a new resource instance which got already created at the
    first place in contrast to fresh retrieval of the resource json data.
    Again, the ``force`` argument is deliberately set to False to do only the
    "light refresh" of the resource (only the fresh retrieval of resource)
    instead of doing the complete exhaustive "cascading refresh" (resource
    with all its nested subresources recursively).

    .. code-block:: python

      class SomeResource(base.ResourceBase):
        ...
        @property
        @cache_it
        def nested_resource(self):
          return NestedResource(
            self._conn, "Path/to/NestedResource",
            redfish_version=self.redfish_version)
        ...
        def _do_refresh(self, force):
          # selective attribute clearing
          cache_clear(self, force, only_these=['nested_resource'])

    Do note that this is not thread safe. So guard your code to protect it
    from any kind of concurrency issues while using this decorator.

    :param res_accessor_method: the resource accessor decorated method.

    """
    cache_attr_name = '_cache_' + res_accessor_method.__name__

    @functools.wraps(res_accessor_method)
    def func_wrapper(res_selfie):

        cache_attr_val = getattr(res_selfie, cache_attr_name, None)
        if cache_attr_val is None:

            cache_attr_val = res_accessor_method(res_selfie)
            setattr(res_selfie, cache_attr_name, cache_attr_val)

            # Note(deray): Each resource instance maintains a collection of
            # all the cache attribute names in a private attribute.
            cache_attr_names = setdefaultattr(
                res_selfie, CACHE_ATTR_NAMES_VAR_NAME, set())
            cache_attr_names.add(cache_attr_name)

        from sushy.resources import base

        if isinstance(cache_attr_val, base.ResourceBase):
            cache_attr_val.refresh(force=False)
        elif isinstance(cache_attr_val, collections.abc.Sequence):
            for elem in cache_attr_val:
                if isinstance(elem, base.ResourceBase):
                    elem.refresh(force=False)

        return cache_attr_val

    return func_wrapper


def cache_clear(res_selfie, force_refresh, only_these=None):
    """Clear some or all cached values of the resource.

    If the cache variable refers to a resource instance then the
    ``invalidate()`` method is called on that. Otherwise it is set to None.
    Should there be a need to force refresh the resource and its sub-resources,
    "cascading refresh", ``force_refresh`` is to be set to True.

    This is the complimentary method of ``cache_it`` decorator.

    :param res_selfie: the resource instance.
    :param force_refresh: force_refresh argument of ``invalidate()`` method.
    :param only_these: expects a sequence of specific method names
        for which the cached value/s need to be cleared only. When None, all
        the cached values are cleared.
    """
    cache_attr_names = setdefaultattr(
        res_selfie, CACHE_ATTR_NAMES_VAR_NAME, set())
    if only_these is not None:
        if not isinstance(only_these, collections.abc.Sequence):
            raise TypeError("'only_these' must be a sequence.")

        cache_attr_names = cache_attr_names.intersection(
            '_cache_' + attr for attr in only_these)

    for cache_attr_name in cache_attr_names:
        cache_attr_val = getattr(res_selfie, cache_attr_name)

        from sushy.resources import base

        if isinstance(cache_attr_val, base.ResourceBase):
            cache_attr_val.invalidate(force_refresh)
        elif isinstance(cache_attr_val, collections.abc.Sequence):
            for elem in cache_attr_val:
                if isinstance(elem, base.ResourceBase):
                    elem.invalidate(force_refresh)
                else:
                    setattr(res_selfie, cache_attr_name, None)
                    break
        else:
            setattr(res_selfie, cache_attr_name, None)


def camelcase_to_underscore_joined(camelcase_str):
    """Convert camelCase string to underscore_joined string

    :param camelcase_str: The camelCase string
    :returns: the equivalent underscore_joined string
    """
    if not camelcase_str:
        raise ValueError('"camelcase_str" cannot be empty')

    r = camelcase_str[0].lower()
    for i, letter in enumerate(camelcase_str[1:], 1):
        if letter.isupper():
            try:
                if (camelcase_str[i - 1].islower()
                        or camelcase_str[i + 1].islower()):
                    r += '_'
            except IndexError:
                pass

        r += letter.lower()

    return r


def synchronized(wrapped):
    """Simple synchronization decorator.

    Decorating a method like so:

    .. code-block:: python

      @synchronized
      def foo(self, *args):
        ...

    ensures that only one thread will execute the foo method at a time.
    """
    lock = threading.RLock()

    @functools.wraps(wrapped)
    def wrapper(*args, **kwargs):
        with lock:
            return wrapped(*args, **kwargs)

    return wrapper


_REMOVE = frozenset(['password', 'x-auth-token'])


def sanitize(item):
    """Remove passwords from the item."""
    if isinstance(item, dict):
        return {key: ('***' if key.lower() in _REMOVE else sanitize(value))
                for key, value in item.items()}
    else:
        return item
