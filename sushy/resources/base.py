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
import logging

import six

from sushy import utils


LOG = logging.getLogger(__name__)


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
        self.refresh()

    def refresh(self):
        """Refresh the resource

        Freshly retrieves/fetches the resource attributes and invokes
        ``_parse_attributes()`` method on successful retrieval.
        :raises: ResourceNotFoundError
        :raises: ConnectionError
        :raises: HTTPError
        """
        self._json = self._conn.get(path=self._path).json()
        LOG.debug('Received representation of %(type)s %(path)s: %(json)s',
                  {'type': self.__class__.__name__,
                   'path': self._path, 'json': self._json})
        self._parse_attributes()

    @property
    def json(self):
        return self._json

    @property
    def path(self):
        return self._path

    @abc.abstractmethod
    def _parse_attributes(self):
        """Parse the attributes of a resource

        This method should be overwritten and is responsible for parsing
        all the attributes of a resource.
        """


@six.add_metaclass(abc.ABCMeta)
class ResourceCollectionBase(ResourceBase):

    name = None
    """The name of the collection"""

    members_identities = None
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

    @property
    @abc.abstractmethod
    def _resource_type(self):
        """The resource class that the collection contains.

        Override this property to specify the resource class that the
        collection contains.
        """

    def _parse_attributes(self):
        self.name = self.json.get('Name')
        self.members_identities = (
            utils.get_members_identities(self.json.get('Members', [])))
        LOG.debug('Received %(count)d member(s) for %(type)s %(path)s',
                  {'count': len(self.members_identities),
                   'type': self.__class__.__name__, 'path': self._path})

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
