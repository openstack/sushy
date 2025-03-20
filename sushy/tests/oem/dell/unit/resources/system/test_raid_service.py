# Copyright (c) 2021 Dell Inc. or its subsidiaries.
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

import json
from unittest import mock

from oslotest.base import BaseTestCase
from sushy import exceptions
from sushy import taskmonitor

from sushy.oem.dell.resources.system import raid_service


class DellRaidService(BaseTestCase):

    def setUp(self):
        super().setUp()
        self.conn = mock.Mock()
        with open('sushy/tests/oem/dell/unit/json_samples/'
                  'raid_service.json') as f:
            mock_response = self.conn.get.return_value
            mock_response.json.return_value = json.load(f)
            mock_response.status_code = 200

        self.mock_response = mock.Mock()
        self.mock_response.status_code = 202
        self.mock_response.headers = {
            'Location': '/redfish/v1/Managers/iDRAC.Embedded.1/Oem/Dell/Jobs/'
                        'JID_999888777666'
        }

        self.root = mock.Mock()

        self.raid_service = raid_service.DellRaidService(
            self.conn,
            '/redfish/v1/Systems/System.Embedded.1/Oem/Dell/'
            'DellRaidService', root=self.root
        )

    @mock.patch.object(raid_service.DellRaidService,
                       '_get_task_monitor_from_dell_job', autospec=True)
    def test_convert_to_raid(self, mock_get_task_mon):
        mock_task_mon = mock.Mock()
        mock_get_task_mon.return_value = mock_task_mon
        fqdds = ["Disk.Bay.0:Enclosure.Internal.0-1:RAID.Integrated.1-1",
                 "Disk.Bay.1:Enclosure.Internal.0-1:RAID.Integrated.1-1"]

        task_mon = self.raid_service.convert_to_raid(fqdds)

        self.conn.post.assert_called_once_with(
            '/redfish/v1/Systems/System.Embedded.1/Oem/Dell/DellRaidService/'
            'Actions/DellRaidService.ConvertToRAID',
            data={'PDArray': fqdds})
        self.assertEqual(mock_task_mon, task_mon)

    @mock.patch.object(raid_service.DellRaidService,
                       '_get_task_monitor_from_dell_job', autospec=True)
    def test_convert_to_nonraid(self, mock_get_task_mon):
        mock_task_mon = mock.Mock()
        mock_get_task_mon.return_value = mock_task_mon
        fqdds = ["Disk.Bay.0:Enclosure.Internal.0-1:RAID.Integrated.1-1",
                 "Disk.Bay.1:Enclosure.Internal.0-1:RAID.Integrated.1-1"]

        task_mon = self.raid_service.convert_to_nonraid(fqdds)

        self.conn.post.assert_called_once_with(
            '/redfish/v1/Systems/System.Embedded.1/Oem/Dell/DellRaidService/'
            'Actions/DellRaidService.ConvertToNonRAID',
            data={'PDArray': fqdds})
        self.assertEqual(mock_task_mon, task_mon)

    @mock.patch.object(raid_service.DellRaidService,
                       '_get_task_monitor_from_dell_job', autospec=True)
    def test_clear_foreign_config(self, mock_get_task_mon):
        mock_task_mon = mock.Mock()
        mock_get_task_mon.return_value = mock_task_mon

        result = self.raid_service.clear_foreign_config('RAID.Integrated.1-1')

        self.conn.post.assert_called_once_with(
            '/redfish/v1/Systems/System.Embedded.1/Oem/Dell/DellRaidService/'
            'Actions/DellRaidService.ClearForeignConfig',
            data={'TargetFQDD': 'RAID.Integrated.1-1'})
        self.assertEqual(mock_task_mon, result)

    def test_clear_foreign_config_no_config(self):
        mock_response = mock.Mock()
        mock_response.status_code = 400
        mock_response.json.return_value = {
            "error": {
                "@Message.ExtendedInfo": [
                    {
                        "Message": "No foreign configurations detected.",
                        "MessageArgs": [],
                        "MessageArgs@odata.count": 0,
                        "MessageId": "IDRAC.2.5.STOR018",
                        "RelatedProperties": [],
                        "RelatedProperties@odata.count": 0,
                        "Resolution": "If the only foreign drives present are "
                                      "in a secured locked state, run a "
                                      "secure erase operation on the drives "
                                      "to securely erase data or unlock these "
                                      "drives and retry the operation. "
                                      "Otherwise the operation was not "
                                      "successful because there are no "
                                      "foreign drives.",
                        "Severity": "Warning"
                    }
                ],
                "code": "Base.1.8.GeneralError",
                "message": "A general error has occurred. See ExtendedInfo "
                           "for more information"
            }
        }
        no_config_error = exceptions.BadRequestError(
            'POST', '/redfish/v1/Dell/Systems/System.Embedded.1/'
            'DellRaidService/Actions/DellRaidService.ClearForeignConfig',
            mock_response)
        self.conn.post.side_effect = no_config_error

        result = self.raid_service.clear_foreign_config('RAID.Integrated.1-1')

        self.assertIsNone(result)

    def test_clear_foreign_config_bad_request(self):
        mock_response = mock.Mock()
        mock_response.status_code = 400
        mock_response.json.return_value = {
            "error": {
                "@Message.ExtendedInfo": [
                    {
                        "Message": "Controller not found.",
                        "MessageArgs": [],
                        "MessageArgs@odata.count": 0,
                        "MessageId": "IDRAC.2.4.STOR030",
                        "RelatedProperties": [],
                        "RelatedProperties@odata.count": 0,
                        "Resolution": "Provide a valid controller FQDD (Fully "
                                      "Qualified Device Descriptor) and retry "
                                      "the operation.",
                        "Severity": "Warning"
                    }
                ],
                "code": "Base.1.7.GeneralError",
                "message": "A general error has occurred. See ExtendedInfo "
                           "for more information"
            }
        }
        no_config_error = exceptions.BadRequestError(
            'POST', '/redfish/v1/Dell/Systems/System.Embedded.1/'
            'DellRaidService/Actions/DellRaidService.ClearForeignConfig',
            mock_response)
        self.conn.post.side_effect = no_config_error

        self.assertRaises(exceptions.BadRequestError,
                          self.raid_service.clear_foreign_config,
                          'RAID.Integrated.999')

    def test__get_task_monitor_from_dell_job(self):
        mock_task1 = mock.Mock(identity='JID_111222333444',
                               path='/TaskService/Task/JID_111222333444')
        mock_task2 = mock.Mock(identity='JID_999888777666',
                               path='/TaskService/Task/JID_999888777666')
        mock_tasks = mock.Mock()
        mock_tasks.get_members.return_value = [mock_task1, mock_task2]
        self.root.get_task_service.return_value.tasks = mock_tasks

        task_mon = self.raid_service._get_task_monitor_from_dell_job(
            self.mock_response)

        self.assertIsInstance(task_mon, taskmonitor.TaskMonitor)
        self.assertEqual('/TaskService/Task/JID_999888777666',
                         task_mon.task_monitor_uri)

    def test__get_task_monitor_from_dell_job_location_missing(self):
        mock_response = mock.Mock()
        mock_response.status_code = 202
        mock_response.headers = {
            'Connection': 'Keep-Alive'
        }

        self.assertRaisesRegex(
            exceptions.ExtensionError,
            'does not include Location',
            self.raid_service._get_task_monitor_from_dell_job, mock_response)

    def test__get_task_monitor_from_dell_job_task_not_found(self):
        mock_task1 = mock.Mock(identity='JID_000000000000',
                               path='/TaskService/Task/JID_000000000000')
        mock_tasks = mock.Mock()
        mock_tasks.get_members.return_value = [mock_task1]
        self.root.get_task_service.return_value.tasks = mock_tasks

        self.assertRaisesRegex(
            exceptions.ExtensionError,
            'not find task by id',
            self.raid_service._get_task_monitor_from_dell_job,
            self.mock_response)
