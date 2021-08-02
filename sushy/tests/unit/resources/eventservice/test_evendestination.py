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

import json
from unittest import mock

from sushy.resources.eventservice import eventdestination
from sushy.tests.unit import base


class EventDestinationTestCase(base.TestCase):

    def setUp(self):
        super(EventDestinationTestCase, self).setUp()
        self.conn = mock.Mock()
        with open('sushy/tests/unit/json_samples/eventdestination1.json') as f:
            self.json_doc = json.load(f)

        self.conn.get.return_value.json.return_value = self.json_doc

        self.subscription = eventdestination.EventDestination(
            self.conn, '/redfish/v1/EventService',
            redfish_version='1.0.0')

    def test__parse_attributes(self):
        self.subscription._parse_attributes(self.json_doc)

        self.assertEqual(self.subscription.identity, '1')
        self.assertEqual(self.subscription.name, 'Event Subscription')
        self.assertEqual(self.subscription.context, 'SomeContext')
        self.assertEqual(self.subscription.destination,
                         'https://localhost/RedfishEvents/EventReceiver.php')
        self.assertEqual(self.subscription.protocol, 'Redfish')
        self.assertEqual(set(self.subscription.event_types),
                         set(["Alert", "StatusChange"]))
        self.assertEqual(self.subscription.http_headers, [])

    def test__delete(self):
        self.subscription.delete()
        self.subscription._conn.delete.assert_called_once_with(
            self.subscription._path)


class EventDestinationCollectionTestCase(base.TestCase):

    def setUp(self):
        super(EventDestinationCollectionTestCase, self).setUp()
        self.conn = mock.Mock()
        with open('sushy/tests/unit/json_samples/'
                  'eventdestination_collection.json', 'r') as f:
            self.conn.get.return_value.json.return_value = json.loads(f.read())
        self.eventdestination = eventdestination.EventDestinationCollection(
            self.conn, '/redfish/v1/EventService/Subscriptions',
            redfish_version='1.0.0')

    @mock.patch.object(eventdestination, 'EventDestination', autospec=True)
    def test_get_member(self, subscription_mock):
        self.eventdestination.get_member(
            '/redfish/v1/EventService/Subscriptions/1')
        subscription_mock.assert_called_once_with(
            self.eventdestination._conn,
            '/redfish/v1/EventService/Subscriptions/1',
            redfish_version=self.eventdestination.redfish_version,
            registries=None, root=self.eventdestination.root)

    @mock.patch.object(eventdestination, 'EventDestination', autospec=True)
    def test_get_members(self, subscription_mock):
        members = self.eventdestination.get_members()
        calls = [
            mock.call(self.eventdestination._conn,
                      '/redfish/v1/EventService/Subscriptions/%s' % member,
                      redfish_version=self.eventdestination.redfish_version,
                      registries=None,
                      root=self.eventdestination.root)
            for member in ('1', '2')
        ]
        subscription_mock.assert_has_calls(calls)
        self.assertIsInstance(members, list)
        self.assertEqual(2, len(members))

    def test__create_subscription_with_required_parameters(self):
        payload = {
            'Protocol': 'Redfish',
            'Destination': 'https://localhost/RedfishEvents/EventReceiver.php',
            'Context': 'IronicContext',
            'EventTypes': ["Alert"]
        }
        with open('sushy/tests/unit/json_samples/eventdestination2.json') as f:
            self.conn.get.return_value.json.return_value = json.load(f)
        self.conn.post.return_value.status_code = 201
        self.conn.post.return_value.headers.return_value = {
            'Location': '/redfish/v1/EventService/Subscriptions/2'
        }
        new_subscription = self.eventdestination.create(payload)
        self.eventdestination._conn.post.assert_called_once_with(
            '/redfish/v1/EventService/Subscriptions',
            data=payload,
        )
        self.assertIsNotNone(new_subscription)
        self.assertEqual(new_subscription.identity, '2')
        self.assertEqual(new_subscription.context, 'IronicContext')
        self.assertEqual(new_subscription.destination,
                         'https://localhost/RedfishEvents/EventReceiver.php')
        self.assertIn("Alert", new_subscription.event_types)

    def test__create_subscription_with_invalid_event_type(self):
        payload = {
            'Protocol': 'Redfish',
            'Destination': 'https://localhost/RedfishEvents/EventReceiver.php',
            'Context': 'IronicContext',
            'EventTypes': ["Other"]
        }
        self.conn.post.return_value.status_code = 400
        new_subscription = self.eventdestination.create(payload)
        self.eventdestination._conn.post.assert_called_once_with(
            '/redfish/v1/EventService/Subscriptions',
            data=payload,
        )
        self.assertIsNone(new_subscription)

    def test__create_subscription_with_empty_context(self):
        payload = {
            'Protocol': 'Redfish',
            'Destination': 'https://localhost/RedfishEvents/EventReceiver.php',
            'Context': '',
            'EventTypes': ["Alert"]
        }
        with open('sushy/tests/unit/json_samples/eventdestination3.json') as f:
            self.conn.get.return_value.json.return_value = json.load(f)
        self.conn.post.return_value.status_code = 201
        self.conn.post.return_value.headers.return_value = {
            'Location': '/redfish/v1/EventService/Subscriptions/3'
        }
        new_subscription = self.eventdestination.create(payload)
        self.eventdestination._conn.post.assert_called_once_with(
            '/redfish/v1/EventService/Subscriptions',
            data=payload,
        )
        self.assertIsNotNone(new_subscription)
        self.assertEqual(new_subscription.identity, '3')
        self.assertIsNone(new_subscription.context)
        self.assertEqual(new_subscription.destination,
                         'https://localhost/RedfishEvents/EventReceiver.php')
        self.assertIn("Alert", new_subscription.event_types)
