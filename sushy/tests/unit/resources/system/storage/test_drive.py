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
from sushy.resources.system.storage import drive
from sushy.tests.unit import base


class DriveTestCase(base.TestCase):

    def setUp(self):
        super(DriveTestCase, self).setUp()
        self.conn = mock.Mock()
        with open('sushy/tests/unit/json_samples/drive.json') as f:
            self.json_doc = json.load(f)

        self.conn.get.return_value.json.return_value = self.json_doc

        self.stor_drive = drive.Drive(
            self.conn,
            '/redfish/v1/Systems/437XR1138/Storage/1/Drives/32ADF365C6C1B7BD',
            redfish_version='1.0.2')

    def test__parse_attributes(self):
        self.stor_drive._parse_attributes(self.json_doc)
        self.assertEqual('1.0.2', self.stor_drive.redfish_version)
        self.assertEqual('32ADF365C6C1B7BD', self.stor_drive.identity)
        self.assertEqual('Drive Sample', self.stor_drive.name)
        self.assertEqual(512, self.stor_drive.block_size_bytes)
        self.assertEqual(899527000000, self.stor_drive.capacity_bytes)
        identifiers = self.stor_drive.identifiers
        self.assertIsInstance(identifiers, list)
        self.assertEqual(1, len(identifiers))
        identifier = identifiers[0]
        self.assertEqual(sushy.DurableNameFormat.NAA,
                         identifier.durable_name_format)
        self.assertEqual('32ADF365C6C1B7BD', identifier.durable_name)
        self.assertEqual('Contoso', self.stor_drive.manufacturer)
        self.assertEqual('HDD', self.stor_drive.media_type)
        self.assertEqual('C123', self.stor_drive.model)
        self.assertEqual('C123-1111', self.stor_drive.part_number)
        self.assertEqual(sushy.Protocol.SAS, self.stor_drive.protocol)
        self.assertEqual('1234570', self.stor_drive.serial_number)
        self.assertEqual('100A', self.stor_drive.revision)
        self.assertEqual(sushy.State.ENABLED, self.stor_drive.status.state)
        self.assertEqual(sushy.Health.OK, self.stor_drive.status.health)

    def test_volumes(self):
        with open('sushy/tests/unit/json_samples/drive3.json') as f:
            drive_json = json.load(f)
        with open('sushy/tests/unit/json_samples/volume2.json') as f:
            volume2_json = json.load(f)
        with open('sushy/tests/unit/json_samples/volume3.json') as f:
            volume3_json = json.load(f)

        self.conn.get.return_value.json.side_effect = [drive_json,
                                                       volume2_json,
                                                       volume3_json]
        stor_drive = drive.Drive(
            self.conn,
            '/redfish/v1/Systems/437XR1138R2/Storage/1/Drives/'
            '3D58ECBC375FD9F2',
            redfish_version='1.0.2')

        volumes = stor_drive.volumes

        self.assertEqual(2, len(volumes))
        self.assertEqual('2', volumes[0].identity)
        self.assertEqual('3', volumes[1].identity)

    def test_set_indicator_led(self):
        self.conn.get.return_value.headers = {'ETag': 'a3b01b63f80a4913'}
        with mock.patch.object(
                self.stor_drive, 'invalidate',
                autospec=True) as invalidate_mock:
            self.stor_drive.set_indicator_led(sushy.IndicatorLED.BLINKING)
            self.stor_drive._conn.patch.assert_called_once_with(
                '/redfish/v1/Systems/437XR1138/Storage/1/Drives/'
                '32ADF365C6C1B7BD', data={'IndicatorLED': 'Blinking'},
                etag='a3b01b63f80a4913')

            invalidate_mock.assert_called_once_with()

    def test_set_indicator_led_invalid_state(self):
        self.assertRaises(exceptions.InvalidParameterValueError,
                          self.stor_drive.set_indicator_led,
                          'spooky-glowing')
