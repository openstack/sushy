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

import sushy
from sushy import exceptions
from sushy.resources import constants as res_cons
from sushy.resources.eventservice import eventservice
from sushy.tests.unit import base


class EventServiceTestCase(base.TestCase):

    def setUp(self):
        super(EventServiceTestCase, self).setUp()
        self.conn = mock.Mock()
        with open('sushy/tests/unit/json_samples/eventservice.json') as f:
            self.json_doc = json.load(f)

        self.conn.get.return_value.json.return_value = self.json_doc

        self.eventservice = eventservice.EventService(
            self.conn, '/redfish/v1/EventService',
            redfish_version='1.0.8')

    def test__parse_attributes(self):
        self.eventservice._parse_attributes(self.json_doc)

        self.assertEqual(self.eventservice.identity, 'EventService')
        self.assertEqual(self.eventservice.name, 'Event Service')
        self.assertEqual(self.eventservice.delivery_retry_attempts, 3)
        self.assertEqual(self.eventservice.delivery_retry_interval, 30)
        self.assertEqual(self.eventservice.service_enabled, True)
        self.assertEqual(self.eventservice.status.health, res_cons.Health.OK)
        self.assertEqual(self.eventservice.status.health_rollup,
                         res_cons.Health.OK)
        self.assertEqual(self.eventservice.status.state,
                         res_cons.State.ENABLED)
        self.assertEqual(self.eventservice.subscriptions._path,
                         '/redfish/v1/EventService/Subscriptions/')

    def test__get_event_types_for_subscription(self):
        expected = set([sushy.EventType.STATUS_CHANGE,
                        sushy.EventType.RESOURCE_ADDED,
                        sushy.EventType.RESOURCE_REMOVED,
                        sushy.EventType.RESOURCE_UPDATED,
                        sushy.EventType.ALERT])

        values = self.eventservice.get_event_types_for_subscription()
        self.assertEqual(expected, values)
        self.assertIsInstance(values, set)

    def test__no_event_types_for_subscription(self):
        expected = set([sushy.EventType.STATUS_CHANGE,
                        sushy.EventType.RESOURCE_ADDED,
                        sushy.EventType.RESOURCE_REMOVED,
                        sushy.EventType.RESOURCE_UPDATED,
                        sushy.EventType.ALERT,
                        sushy.EventType.METRIC_REPORT,
                        sushy.EventType.OTHER])
        self.eventservice.event_types_for_subscription = []

        values = self.eventservice.get_event_types_for_subscription()
        self.assertEqual(expected, values)
        self.assertIsInstance(values, set)

    def test__eventservice_missing_action(self):
        self.eventservice._actions.submit_test_event = None
        self.assertRaisesRegex(
            exceptions.MissingActionError, '#EventService.SubmitTestEvent',
            self.eventservice.submit_test_event, mock.ANY, mock.ANY, mock.ANY,
            mock.ANY, mock.ANY, mock.ANY, mock.ANY, mock.ANY)

    def test__missing_submit_test_event_target(self):
        evt_json = self.eventservice.json
        evt_json['Actions']['#EventService.SubmitTestEvent'].pop('target')
        self.assertRaisesRegex(
            exceptions.MissingAttributeError,
            'attribute Actions/#EventService.SubmitTestEvent/target',
            self.eventservice._parse_attributes, self.json_doc)

    def test__submit_test_event(self):
        self.assertIsNotNone(self.eventservice._actions.submit_test_event)
        payload = {
            "EventId": "myEventId",
            "EventTimestamp": "2016-10-11T09:42:59Z",
            "EventType": "StatusChange",
            "Message": "This is a test message",
            "MessageArgs": ["arg0", "arg1"],
            "MessageId": "iLOEvents.0.9.ResourceStatusChanged",
            "OriginOfCondition": "/rest/v1/Chassis/1/FooBar",
            "Severity": "OK"
        }
        self.eventservice.submit_test_event(
            payload["EventId"], payload["EventTimestamp"],
            payload["EventType"], payload["Message"],
            payload["MessageArgs"], payload["MessageId"],
            payload["OriginOfCondition"], payload["Severity"])
        self.eventservice._conn.post.assert_called_once_with(
            '/redfish/v1/EventService/Actions/EventService.SubmitTestEvent/',
            data=payload)
