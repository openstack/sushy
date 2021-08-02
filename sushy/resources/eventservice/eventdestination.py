# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied.
# See the License for the specific language governing permissions and
# limitations under the License.


# Redfish standard schema.
# https://redfish.dmtf.org/schemas/v1/EventDestination.v1_0_0.json

import logging

from sushy.resources import base

LOG = logging.getLogger(__name__)


class EventDestination(base.ResourceBase):

    identity = base.Field('Id', required=True)
    """The EventDestination resource identity"""

    name = base.Field('Name', required=True)
    """The EventDestination resource name"""

    context = base.Field('Context')
    """A client-supplied string that is stored with the event destination
    subscription"""

    description = base.Field('Description')
    """The description of the EventDestination resource"""

    destination = base.Field('Destination')
    """The URI of the destination Event Service"""

    event_types = base.Field('EventTypes', adapter=list)
    """The types of events that shall be sent to the destination"""

    protocol = base.Field('Protocol')
    """Contain the protocol type that the event will use for sending
    the event to the destination.  A value of Redfish shall be used
    to indicate that the event type shall adhere to that defined in
    the Redfish specification"""

    http_headers = base.Field('HttpHeaders', adapter=list)
    """This is for setting HTTP headers, such as authorization information.
    This object will be null on a GET."""

    def __init__(self, connector, identity, redfish_version=None,
                 registries=None, root=None):
        """A class representing an EventDestination

        :param connector: A Connector instance
        :param identity: The identity of the EventDestination resource
        :param redfish_version: The version of RedFish. Used to construct
            the object according to schema of given version.
        :param registries: Dict of registries to be used in any resource
            that needs registries to parse messages.
        :param root: Sushy root object. Empty for Sushy root itself.
        """
        super(EventDestination, self).__init__(
            connector, identity, redfish_version=redfish_version,
            registries=registries, root=root)

    def delete(self):
        """Delete an EventDestination

        :raises: ConnectionError
        :raises: HTTPError
        """
        self._conn.delete(self._path)


class EventDestinationCollection(base.ResourceCollectionBase):

    name = base.Field('Name')
    """The EventDestination collection name"""

    description = base.Field('Description')
    """The EventDestination collection description"""

    @property
    def _resource_type(self):
        return EventDestination

    def __init__(self, connector, identity, redfish_version=None,
                 registries=None, root=None):
        """A class representing a EventDestinationCollection

        :param connector: A Connector instance
        :param identity: The identity of the EventDestination resource
        :param redfish_version: The version of RedFish. Used to construct
            the object according to schema of given version.
        :param registries: Dict of registries to be used in any resource
            that needs registries to parse messages.
        :param root: Sushy root object. Empty for Sushy root itself.
        """
        super(EventDestinationCollection, self).__init__(
            connector, identity, redfish_version=redfish_version,
            registries=registries, root=root)

    def _create(self, payload):
        r = self._conn.post(self._path, data=payload)
        location = r.headers.get('Location')
        return r, location

    def create(self, payload):
        """Create a Subscription

        :param payload: The payload representing the subscription.

        :raises: ConnectionError
        :raises: HTTPError
        :returns: The new subscription
        """
        r, location = self._create(payload)
        if r.status_code == 201:
            if location:
                self.refresh()
                return self.get_member(location)
