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

import datetime
import json
from unittest import mock

import sushy
from sushy import exceptions
from sushy.resources import base as resource_base
from sushy.resources.system import system
from sushy.tests.unit import base
from sushy import utils


class UtilsTestCase(base.TestCase):

    def test_revert_dictionary(self):
        source = {'key0': 'value0', 'key1': 'value1'}
        expected = {'value0': 'key0', 'value1': 'key1'}
        self.assertEqual(expected, utils.revert_dictionary(source))

    @mock.patch.object(utils.LOG, 'warning', autospec=True)
    def test_get_members_identities(self, log_mock):
        members = [{"@odata.id": "/redfish/v1/Systems/FOO"},
                   {"other_key": "/redfish/v1/Systems/FUN"},
                   {"@odata.id": "/redfish/v1/Systems/BAR/"}]
        expected = ('/redfish/v1/Systems/FOO', '/redfish/v1/Systems/BAR')
        self.assertEqual(expected, utils.get_members_identities(members))
        self.assertEqual(1, log_mock.call_count)

    def test_int_or_none(self):
        self.assertEqual(1, utils.int_or_none('1'))
        self.assertIsNone(utils.int_or_none(None))

    def test_bool_or_none_none(self):
        self.assertIsNone(utils.bool_or_none(None))

    def test_bool_or_none_bool(self):
        self.assertEqual(True, utils.bool_or_none(True))

    def setUp(self):
        super(UtilsTestCase, self).setUp()
        self.conn = mock.MagicMock()
        with open('sushy/tests/unit/json_samples/system.json') as f:
            system_json = json.load(f)
        self.conn.get.return_value.json.return_value = system_json

        self.sys_inst = system.System(self.conn,
                                      '/redfish/v1/Systems/437XR1138R2',
                                      redfish_version='1.0.2')

    def test_get_sub_resource_path_by(self):
        subresource_path = 'EthernetInterfaces'
        expected_result = '/redfish/v1/Systems/437XR1138R2/EthernetInterfaces'
        value = utils.get_sub_resource_path_by(self.sys_inst,
                                               subresource_path)
        self.assertEqual(expected_result, value)

    def test_get_sub_resource_path_by_list(self):
        subresource_path = ['EthernetInterfaces']
        expected_result = '/redfish/v1/Systems/437XR1138R2/EthernetInterfaces'
        value = utils.get_sub_resource_path_by(self.sys_inst,
                                               subresource_path)
        self.assertEqual(expected_result, value)

    def test_get_sub_resource_path_by_collection(self):
        subresource_path = ["Links", "ManagedBy"]
        expected_result = ['/redfish/v1/Managers/BMC']
        value = utils.get_sub_resource_path_by(self.sys_inst,
                                               subresource_path,
                                               is_collection=True)
        self.assertEqual(expected_result, value)

    def test_get_sub_resource_path_by_fails(self):
        subresource_path = ['Links', 'Chassis']
        expected_result = 'attribute Links/Chassis/@odata.id is missing'
        self.assertRaisesRegex(
            exceptions.MissingAttributeError,
            expected_result,
            utils.get_sub_resource_path_by,
            self.sys_inst, subresource_path)

    def test_get_sub_resource_path_by_fails_with_empty_path(self):
        self.assertRaisesRegex(
            ValueError,
            '"subresource_name" cannot be empty',
            utils.get_sub_resource_path_by,
            self.sys_inst, [])

    def test_get_sub_resource_path_by_fails_with_empty_string(self):
        self.assertRaisesRegex(
            ValueError,
            '"subresource_name" cannot be empty',
            utils.get_sub_resource_path_by,
            self.sys_inst, '')

    def test_max_safe(self):
        self.assertEqual(10, utils.max_safe([1, 3, 2, 8, 5, 10, 6]))
        self.assertEqual(821, utils.max_safe([15, 300, 270, None, 821, None]))
        self.assertEqual(0, utils.max_safe([]))
        self.assertIsNone(utils.max_safe([], default=None))

    def test_camelcase_to_underscore_joined(self):
        input_vs_expected = [
            ('GarbageCollection', 'garbage_collection'),
            ('DD', 'dd'),
            ('rr', 'rr'),
            ('AABbbC', 'aa_bbb_c'),
            ('AABbbCCCDd', 'aa_bbb_ccc_dd'),
            ('Manager', 'manager'),
            ('EthernetInterfaceCollection', 'ethernet_interface_collection'),
            (' ', ' '),
        ]
        for inp, exp in input_vs_expected:
            self.assertEqual(exp, utils.camelcase_to_underscore_joined(inp))

    def test_camelcase_to_underscore_joined_fails_with_empty_string(self):
        self.assertRaisesRegex(
            ValueError,
            '"camelcase_str" cannot be empty',
            utils.camelcase_to_underscore_joined, '')


class NestedResource(resource_base.ResourceBase):

    def _parse_attributes(self, json_doc):
        pass


class BaseResource(resource_base.ResourceBase):

    def _parse_attributes(self, json_doc):
        pass

    def _do_some_crunch_work_to_get_a(self):
        return 'a'

    @utils.cache_it
    def get_a(self):
        return self._do_some_crunch_work_to_get_a()

    def _do_some_crunch_work_to_get_b(self):
        return 'b'

    @utils.cache_it
    def get_b(self):
        return self._do_some_crunch_work_to_get_b()

    @property
    @utils.cache_it
    def nested_resource(self):
        return NestedResource(
            self._conn, "path/to/nested_resource",
            redfish_version=self.redfish_version)

    @property
    @utils.cache_it
    def few_nested_resources(self):
        return [NestedResource(self._conn, "/nested_res1",
                               redfish_version=self.redfish_version),
                NestedResource(self._conn, "/nested_res2",
                               redfish_version=self.redfish_version)]


class CacheTestCase(base.TestCase):

    def setUp(self):
        super(CacheTestCase, self).setUp()
        self.conn = mock.Mock()
        self.res = BaseResource(connector=self.conn, path='/Foo',
                                redfish_version='1.0.2')

    def test_cache_nested_resource_retrieval(self):
        nested_res = self.res.nested_resource
        few_nested_res = self.res.few_nested_resources

        self.assertIsInstance(nested_res, NestedResource)
        self.assertIs(nested_res, self.res.nested_resource)
        self.assertIsInstance(few_nested_res, list)
        for n_res in few_nested_res:
            self.assertIsInstance(n_res, NestedResource)
        self.assertIs(few_nested_res, self.res.few_nested_resources)

        self.res.invalidate()
        self.res.refresh(force=False)

        self.assertIsNotNone(self.res._cache_nested_resource)
        self.assertTrue(self.res._cache_nested_resource._is_stale)
        self.assertIsNotNone(self.res._cache_few_nested_resources)
        for n_res in self.res._cache_few_nested_resources:
            self.assertTrue(n_res._is_stale)

        self.assertIsInstance(self.res.nested_resource, NestedResource)
        self.assertFalse(self.res._cache_nested_resource._is_stale)
        self.assertIsInstance(self.res.few_nested_resources, list)
        for n_res in self.res._cache_few_nested_resources:
            self.assertFalse(n_res._is_stale)

    def test_cache_non_resource_retrieval(self):
        with mock.patch.object(
                self.res, '_do_some_crunch_work_to_get_a',
                wraps=self.res._do_some_crunch_work_to_get_a,
                autospec=True) as do_work_to_get_a_spy:
            result = self.res.get_a()
            self.assertTrue(do_work_to_get_a_spy.called)

            do_work_to_get_a_spy.reset_mock()
            # verify subsequent invocation
            self.assertEqual(result, self.res.get_a())
            self.assertFalse(do_work_to_get_a_spy.called)

    def test_cache_clear_only_selected_attr(self):
        self.res.nested_resource
        self.res.get_a()
        self.res.get_b()

        utils.cache_clear(self.res, False, only_these=['get_a'])

        # cache cleared (set to None)
        self.assertIsNone(self.res._cache_get_a)
        # cache retained
        self.assertEqual('b', self.res._cache_get_b)
        self.assertFalse(self.res._cache_nested_resource._is_stale)

    def test_cache_clear_failure(self):
        self.assertRaises(
            TypeError, utils.cache_clear, self.res, False, only_these=10)

    def test_sanitize(self):
        orig = {'UserName': 'admin', 'Password': 'pwd',
                'nested': {'answer': 42, 'password': 'secret'}}
        expected = {'UserName': 'admin', 'Password': '***',
                    'nested': {'answer': 42, 'password': '***'}}
        self.assertEqual(expected, utils.sanitize(orig))


class ProcessApplyTimeTestCase(base.TestCase):

    def test_process_apply_time_input(self):
        payload = utils.process_apply_time_input(
            {'test': 'value'},
            sushy.ApplyTime.ON_RESET, None, None)
        self.assertEqual(
            {'@Redfish.SettingsApplyTime': {
                '@odata.type': '#Settings.v1_0_0.PreferredApplyTime',
                'ApplyTime': 'OnReset'},
                'test': 'value'}, payload)

    def test_process_apply_time_input_maintenance_window(self):
        payload = utils.process_apply_time_input(
            {'test': 'value'},
            sushy.ApplyTime.AT_MAINTENANCE_WINDOW_START,
            datetime.datetime(2020, 9, 1, 4, 30, 0),
            600)
        self.assertEqual(
            {'@Redfish.SettingsApplyTime': {
                '@odata.type': '#Settings.v1_0_0.PreferredApplyTime',
                'ApplyTime': 'AtMaintenanceWindowStart',
                'MaintenanceWindowDurationInSeconds': 600,
                'MaintenanceWindowStartTime': '2020-09-01T04:30:00'},
             'test': 'value'}, payload)

    def test_process_apply_time_missing(self):
        self.assertRaises(
            ValueError, utils.process_apply_time_input,
            {'test': 'value'}, None, datetime.datetime(2020, 9, 1, 4, 30, 0),
            600)

    def test_process_apply_time_maint_window_start_time_missing(self):
        self.assertRaises(
            ValueError, utils.process_apply_time_input, {'test': 'value'},
            sushy.ApplyTime.AT_MAINTENANCE_WINDOW_START, None, 600)

    def test_process_apply_time_maint_window_duration_missing(self):
        self.assertRaises(
            ValueError, utils.process_apply_time_input, {'test': 'value'},
            sushy.ApplyTime.AT_MAINTENANCE_WINDOW_START,
            datetime.datetime.now(), None)
