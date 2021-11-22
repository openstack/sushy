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
# https://redfish.dmtf.org/schemas/v1/EventService.v1_0_8.json

import logging

from sushy import exceptions
from sushy.resources import base
from sushy.resources import common
from sushy.resources.eventservice import constants
from sushy.resources.eventservice import eventdestination

LOG = logging.getLogger(__name__)


class ActionsField(base.CompositeField):

    submit_test_event = common.ActionField(
        '#EventService.SubmitTestEvent')


class EventService(base.ResourceBase):

    identity = base.Field('Id', required=True)
    """The EventService resource identity"""

    name = base.Field('Name', required=True)
    """The EventService resource name"""

    delivery_retry_attempts = base.Field('DeliveryRetryAttempts')
    """Number of attempts an event posting is retried before the subscription
    is terminated. This retry is at the service level, meaning the HTTP POST
    to the Event Destination was returned by the HTTP operation as unsuccessful
    (4xx or 5xx return code) or an HTTP timeout occurred this many times before
    the Event Destination subscription is terminated
    """

    delivery_retry_interval = base.Field('DeliveryRetryIntervalSeconds')
    """Number of seconds between retry attempts for sending any given Event"""

    event_types_for_subscription = base.Field('EventTypesForSubscription',
                                              adapter=list)
    """Types of Events that can be subscribed to"""

    service_enabled = base.Field('ServiceEnabled', adapter=bool)
    """Indicates whether the EventService is enabled"""

    status = common.StatusField('Status')
    """The status of the EventService"""

    _actions = ActionsField('Actions', required=True)

    def __init__(self, connector, identity, redfish_version=None,
                 registries=None, root=None):
        """A class representing a EventService

        :param connector: A Connector instance
        :param identity: The identity of the EventService resource
        :param redfish_version: The version of Redfish. Used to construct
            the object according to schema of given version
        :param registries: Dict of registries to be used in any resource
            that needs registries to parse messages.
        :param root: Sushy root object. Empty for Sushy root itself.
        """
        super(EventService, self).__init__(
            connector, identity, redfish_version=redfish_version,
            registries=registries, root=root)

    def _get_submit_test_event(self):
        submit_test_event_action = self._actions.submit_test_event
        if not submit_test_event_action:
            raise exceptions.MissingActionError(
                action='#EventService.SubmitTestEvent',
                resource=self._path)
        return submit_test_event_action

    def submit_test_event(self, event_id, event_timestamp, event_type,
                          message, message_args, message_id, origin,
                          severity):
        """Submit Test Event is used to to send a test event to the BMC

        :param event_id: ID of event to be added.
        :param event_timestamp: time stamp of event to be added.
        :param event_type: type of event to be added.
        :param message: human readable message of event to be added.
        :param message_args: array of message arguments of the event to
            be added.
        :param message_id: message ID of event to be added.
        :param origin: string of the URL within the OriginOfCondition
            property of the event to be added
        :param severity: the Severity of event to be added.
        :param target: The  link to invoke action.
        :raises: MissingActionError if the EvenService does not have the
             action.
        """

        target_uri = self._get_submit_test_event().target_uri

        data = {
            'EventId': event_id,
            'EventTimestamp': event_timestamp,
            'EventType': event_type,
            'Message': message,
            'MessageArgs': message_args,
            'MessageId': message_id,
            'OriginOfCondition': origin,
            'Severity': severity
        }

        self._conn.post(target_uri, data=data)

    def get_event_types_for_subscription(self):
        """Get the Types of Events that can be subscribed to

        :returns: A set with the types of Events that can be subscribed to.
        """
        if not self.event_types_for_subscription:
            LOG.warning('Could not figure out the Event types supported by '
                        'the EventService %s', self.identity)
            return set(constants.EventType)

        return {v for v in constants.EventType
                if v.value in self.event_types_for_subscription}

    def _get_subscriptions_collection_path(self):
        """Helper function to find the EventDestinationCollections path"""
        subscriptions = self.json.get('Subscriptions')
        if not subscriptions:
            raise exceptions.MissingAttributeError(
                attribute='Subscriptions', resource=self._path)
        return subscriptions.get('@odata.id')

    @property
    def subscriptions(self):
        """Reference to a collection of Event Destination resources"""
        return eventdestination.EventDestinationCollection(
            self._conn, self._get_subscriptions_collection_path(),
            redfish_version=self.redfish_version, registries=self.registries,
            root=self.root)
