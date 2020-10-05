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

from http import client as http_client
import json
from unittest import mock


import sushy
from sushy import exceptions
from sushy.resources.manager import virtual_media
from sushy.tests.unit import base


class VirtualMediaTestCase(base.TestCase):

    def setUp(self):
        super(VirtualMediaTestCase, self).setUp()
        self.conn = mock.Mock()
        with open('sushy/tests/unit/json_samples/'
                  'virtual_media.json') as f:
            self.json_doc = json.load(f)

        self.conn.get.return_value.json.return_value = self.json_doc

        self.sys_virtual_media = virtual_media.VirtualMedia(
            self.conn, '/redfish/v1/Managers/BMC/VirtualMedia/Floppy1',
            redfish_version='1.0.2')

    def test__parse_attributes(self):
        self.sys_virtual_media._parse_attributes(self.json_doc)
        self.assertEqual('Virtual Removable Media',
                         self.sys_virtual_media.name)
        self.assertEqual('Floppy1', self.sys_virtual_media.identity)
        self.assertEqual('https://www.dmtf.org/freeImages/Sardine.img',
                         self.sys_virtual_media.image)
        self.assertEqual('Sardine2.1.43.35.6a',
                         self.sys_virtual_media.image_name)
        self.assertEqual(sushy.CONNECTED_VIA_URI,
                         self.sys_virtual_media.connected_via)
        self.assertEqual([sushy.VIRTUAL_MEDIA_FLOPPY,
                          sushy.VIRTUAL_MEDIA_USBSTICK],
                         self.sys_virtual_media.media_types)
        self.assertEqual(True, self.sys_virtual_media.inserted)
        self.assertEqual(False, self.sys_virtual_media.write_protected)

    def test__parse_attributes_return(self):
        attributes = self.sys_virtual_media._parse_attributes(self.json_doc)

        # Test that various types are returned correctly
        self.assertEqual('https://www.dmtf.org/freeImages/Sardine.img',
                         attributes.get('image'))
        self.assertEqual(sushy.CONNECTED_VIA_URI,
                         attributes.get('connected_via'))
        self.assertEqual([sushy.VIRTUAL_MEDIA_FLOPPY,
                          sushy.VIRTUAL_MEDIA_USBSTICK],
                         attributes.get('media_types'))

    def test_insert_media_none(self):
        self.sys_virtual_media._actions.insert_media = None
        self.assertRaisesRegex(
            exceptions.MissingActionError, 'action #VirtualMedia.InsertMedia',
            self.sys_virtual_media.insert_media,
            "https://www.dmtf.org/freeImages/Sardine.img", True, False)

    def test_insert_media(self):
        self.assertFalse(self.sys_virtual_media._is_stale)
        self.sys_virtual_media.insert_media(
            "https://www.dmtf.org/freeImages/Sardine.img", True, False)
        self.sys_virtual_media._conn.post.assert_called_once_with(
            ("/redfish/v1/Managers/BMC/VirtualMedia/Floppy1/Actions"
             "/VirtualMedia.InsertMedia"),
            data={"Image": "https://www.dmtf.org/freeImages/Sardine.img",
                  "Inserted": True, "WriteProtected": False}
        )
        self.assertTrue(self.sys_virtual_media._is_stale)

    def test_eject_media_none(self):
        self.sys_virtual_media._actions.eject_media = None
        self.assertRaisesRegex(
            exceptions.MissingActionError, 'action #VirtualMedia.EjectMedia',
            self.sys_virtual_media.eject_media)

    def test_eject_media(self):
        self.assertFalse(self.sys_virtual_media._is_stale)
        self.sys_virtual_media.eject_media()
        self.sys_virtual_media._conn.post.assert_called_once_with(
            ("/redfish/v1/Managers/BMC/VirtualMedia/Floppy1/Actions"
             "/VirtualMedia.EjectMedia"))
        self.assertTrue(self.sys_virtual_media._is_stale)

    def test_eject_media_pass_empty_dict_415(self):
        target_uri = ("/redfish/v1/Managers/BMC/VirtualMedia/Floppy1/Actions"
                      "/VirtualMedia.EjectMedia")
        self.conn.post.side_effect = [exceptions.HTTPError(
            method='POST', url=target_uri, response=mock.MagicMock(
                status_code=http_client.UNSUPPORTED_MEDIA_TYPE)), '200']
        self.sys_virtual_media.eject_media()
        post_calls = [
            mock.call(target_uri),
            mock.call(target_uri, data={})]
        self.sys_virtual_media._conn.post.assert_has_calls(post_calls)
        self.assertTrue(self.sys_virtual_media._is_stale)

    def test_eject_media_pass_empty_dict_400(self):
        target_uri = ("/redfish/v1/Managers/BMC/VirtualMedia/Floppy1/Actions"
                      "/VirtualMedia.EjectMedia")
        self.conn.post.side_effect = [exceptions.HTTPError(
            method='POST', url=target_uri, response=mock.MagicMock(
                status_code=http_client.BAD_REQUEST)), '200']
        self.sys_virtual_media.eject_media()
        post_calls = [
            mock.call(target_uri),
            mock.call(target_uri, data={})]
        self.sys_virtual_media._conn.post.assert_has_calls(post_calls)
        self.assertTrue(self.sys_virtual_media._is_stale)
