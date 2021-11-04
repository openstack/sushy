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

import json
from unittest import mock


import sushy
from sushy import exceptions
from sushy.resources import constants as res_cons
from sushy.resources.system import processor
from sushy.tests.unit import base


class ProcessorTestCase(base.TestCase):

    def setUp(self):
        super(ProcessorTestCase, self).setUp()
        self.conn = mock.Mock()
        with open('sushy/tests/unit/json_samples/processor.json') as f:
            self.json_doc = json.load(f)

        self.conn.get.return_value.json.return_value = self.json_doc

        self.sys_processor = processor.Processor(
            self.conn, '/redfish/v1/Systems/437XR1138R2/Processors/CPU1',
            redfish_version='1.0.2')

    def test__parse_attributes(self):
        self.sys_processor._parse_attributes(self.json_doc)
        self.assertEqual('1.0.2', self.sys_processor.redfish_version)
        self.assertEqual('CPU1', self.sys_processor.identity)
        self.assertEqual('CPU 1', self.sys_processor.socket)
        self.assertEqual(
            sushy.ProcessorType.CPU,
            self.sys_processor.processor_type)
        self.assertEqual(sushy.ProcessorArchitecture.X86,
                         self.sys_processor.processor_architecture)
        self.assertEqual(sushy.InstructionSet.X86_64,
                         self.sys_processor.instruction_set)
        self.assertEqual('Intel(R) Corporation',
                         self.sys_processor.manufacturer)
        self.assertEqual('Multi-Core Intel(R) Xeon(R) processor 7xxx Series',
                         self.sys_processor.model)
        self.assertEqual('0x42',
                         self.sys_processor.processor_id.effective_family)
        self.assertEqual('0x61',
                         self.sys_processor.processor_id.effective_model)
        self.assertEqual('0x34AC34DC8901274A',
                         self.sys_processor.processor_id.
                         identification_registers)
        self.assertEqual('0x429943',
                         self.sys_processor.processor_id.microcode_info)
        self.assertEqual('0x1',
                         self.sys_processor.processor_id.step)
        self.assertEqual('GenuineIntel',
                         self.sys_processor.processor_id.vendor_id)

        self.assertEqual(3700, self.sys_processor.max_speed_mhz)
        self.assertEqual(8, self.sys_processor.total_cores)
        self.assertEqual(16, self.sys_processor.total_threads)
        self.assertEqual(res_cons.State.ENABLED,
                         self.sys_processor.status.state)
        self.assertEqual(res_cons.Health.OK, self.sys_processor.status.health)
        self.assertEqual(res_cons.Health.OK,
                         self.sys_processor.status.health_rollup)

    def test_sub_processors(self):
        self.conn.get.return_value.json.reset_mock()
        with open('sushy/tests/unit/json_samples/'
                  'subprocessor_collection.json') as f:
            subproc_col = json.load(f)
        with open('sushy/tests/unit/json_samples/subprocessor.json') as f:
            subproc1 = json.load(f)

        self.conn.get.return_value.json.side_effect = [subproc_col, subproc1]

        sub_processors = self.sys_processor.sub_processors
        self.assertIsInstance(sub_processors,
                              processor.ProcessorCollection)
        self.assertEqual((0, None), sub_processors.summary)
        self.assertEqual('Core1', sub_processors.get_members()[0].identity)

    def test_sub_processors_missing(self):
        self.sys_processor.json.pop('SubProcessors')
        with self.assertRaisesRegex(
                exceptions.MissingAttributeError, 'attribute SubProcessors'):
            self.sys_processor.sub_processors


class ProcessorCollectionTestCase(base.TestCase):

    def setUp(self):
        super(ProcessorCollectionTestCase, self).setUp()
        self.conn = mock.Mock()
        with open('sushy/tests/unit/json_samples/'
                  'processor_collection.json') as f:
            self.json_doc = json.load(f)

        self.conn.get.return_value.json.return_value = self.json_doc

        self.sys_processor_col = processor.ProcessorCollection(
            self.conn, '/redfish/v1/Systems/437XR1138R2/Processors',
            redfish_version='1.0.2')

    def test__parse_attributes(self):
        self.sys_processor_col._parse_attributes(self.json_doc)
        self.assertEqual('1.0.2', self.sys_processor_col.redfish_version)
        self.assertEqual('Processors Collection', self.sys_processor_col.name)
        self.assertEqual(('/redfish/v1/Systems/437XR1138R2/Processors/CPU1',
                          '/redfish/v1/Systems/437XR1138R2/Processors/CPU2'),
                         self.sys_processor_col.members_identities)

    @mock.patch.object(processor, 'Processor', autospec=True)
    def test_get_member(self, mock_processor):
        self.sys_processor_col.get_member(
            '/redfish/v1/Systems/437XR1138R2/Processors/CPU1')
        mock_processor.assert_called_once_with(
            self.sys_processor_col._conn,
            '/redfish/v1/Systems/437XR1138R2/Processors/CPU1',
            redfish_version=self.sys_processor_col.redfish_version,
            registries=None, root=self.sys_processor_col.root)

    @mock.patch.object(processor, 'Processor', autospec=True)
    def test_get_members(self, mock_processor):
        members = self.sys_processor_col.get_members()
        calls = [
            mock.call(self.sys_processor_col._conn,
                      '/redfish/v1/Systems/437XR1138R2/Processors/CPU1',
                      redfish_version=self.sys_processor_col.redfish_version,
                      registries=None, root=self.sys_processor_col.root),
            mock.call(self.sys_processor_col._conn,
                      '/redfish/v1/Systems/437XR1138R2/Processors/CPU2',
                      redfish_version=self.sys_processor_col.redfish_version,
                      registries=None, root=self.sys_processor_col.root)
        ]
        mock_processor.assert_has_calls(calls)
        self.assertIsInstance(members, list)
        self.assertEqual(2, len(members))

    def _setUp_processor_summary(self):
        self.conn.get.return_value.json.reset_mock()
        successive_return_values = []
        file_names = ['sushy/tests/unit/json_samples/processor.json',
                      'sushy/tests/unit/json_samples/processor2.json']
        for file_name in file_names:
            with open(file_name) as f:
                successive_return_values.append(json.load(f))

        self.conn.get.return_value.json.side_effect = successive_return_values

    def test_summary(self):
        # | GIVEN |
        self._setUp_processor_summary()
        # | WHEN |
        actual_summary = self.sys_processor_col.summary
        # | THEN |
        self.assertEqual((16, sushy.ProcessorArchitecture.X86),
                         actual_summary)
        self.assertEqual(16, actual_summary.count)
        self.assertEqual(sushy.ProcessorArchitecture.X86,
                         actual_summary.architecture)

        # reset mock
        self.conn.get.return_value.json.reset_mock()

        # | WHEN & THEN |
        # tests for same object on invoking subsequently
        self.assertIs(actual_summary,
                      self.sys_processor_col.summary)
        self.conn.get.return_value.json.assert_not_called()

    def test_summary_on_refresh(self):
        # | GIVEN |
        self._setUp_processor_summary()
        # | WHEN & THEN |
        self.assertEqual((16, sushy.ProcessorArchitecture.X86),
                         self.sys_processor_col.summary)

        self.conn.get.return_value.json.side_effect = None
        # On refreshing the sys_processor_col instance...
        with open('sushy/tests/unit/json_samples/'
                  'processor_collection.json') as f:
            self.conn.get.return_value.json.return_value = json.load(f)
        self.sys_processor_col.invalidate()
        self.sys_processor_col.refresh(force=False)

        # | GIVEN |
        self._setUp_processor_summary()
        # | WHEN & THEN |
        self.assertEqual((16, sushy.ProcessorArchitecture.X86),
                         self.sys_processor_col.summary)
