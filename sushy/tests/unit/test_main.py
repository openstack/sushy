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

import json
from unittest import mock

from sushy import auth
from sushy import connector
from sushy import exceptions
from sushy import main
from sushy.resources.chassis import chassis
from sushy.resources.compositionservice import compositionservice
from sushy.resources.fabric import fabric
from sushy.resources.manager import manager
from sushy.resources.registry import message_registry_file
from sushy.resources.sessionservice import session
from sushy.resources.sessionservice import sessionservice
from sushy.resources.system import system
from sushy.resources.updateservice import updateservice
from sushy.tests.unit import base


class MainTestCase(base.TestCase):

    @mock.patch.object(auth, 'SessionOrBasicAuth', autospec=True)
    @mock.patch.object(connector, 'Connector', autospec=True)
    @mock.patch.object(sessionservice, 'SessionService', autospec=True)
    def setUp(self, mock_session_service, mock_connector, mock_auth):
        super(MainTestCase, self).setUp()
        self.conn = mock.Mock()
        self.sess_serv = mock.Mock()
        self.sess_serv.create_session.return_value = (None, None)
        mock_session_service.return_value = self.sess_serv
        mock_connector.return_value = self.conn
        with open('sushy/tests/unit/json_samples/root.json') as f:
            self.json_doc = json.load(f)

        self.conn.get.return_value.json.return_value = self.json_doc
        self.root = main.Sushy('http://foo.bar:1234',
                               verify=True, auth=mock_auth)
        mock_connector.assert_called_once_with(
            'http://foo.bar:1234', verify=True)

    def test__parse_attributes(self):
        self.root._parse_attributes(self.json_doc)
        self.assertEqual('RootService', self.root.identity)
        self.assertEqual('Root Service', self.root.name)
        self.assertEqual('1.0.2', self.root.redfish_version)
        self.assertEqual('92384634-2938-2342-8820-489239905423',
                         self.root.uuid)
        self.assertEqual('Product', self.root.product)
        self.assertTrue(self.root.protocol_features_supported.excerpt_query)
        self.assertFalse(self.root.protocol_features_supported.expand_query)
        self.assertTrue(self.root.protocol_features_supported.filter_query)
        self.assertTrue(
            self.root.protocol_features_supported.only_member_query)
        self.assertFalse(self.root.protocol_features_supported.select_query)
        self.assertEqual('/redfish/v1/Systems', self.root._systems_path)
        self.assertEqual('/redfish/v1/Managers', self.root._managers_path)
        self.assertEqual('/redfish/v1/Chassis', self.root._chassis_path)
        self.assertEqual('/redfish/v1/Fabrics', self.root._fabrics_path)
        self.assertEqual('/redfish/v1/SessionService',
                         self.root._session_service_path)
        self.assertEqual('/redfish/v1/CompositionService',
                         self.root._composition_service_path)

    @mock.patch.object(connector, 'Connector', autospec=True)
    def test__init_throws_exception(self, mock_Connector):
        self.assertRaises(
            ValueError, main.Sushy, 'http://foo.bar:1234',
            'foo', 'bar', auth=mock.MagicMock())

    @mock.patch.object(connector, 'Connector', autospec=True)
    def test_custom_connector(self, mock_Sushy_Connector):
        connector_mock = mock.MagicMock()
        with open('sushy/tests/unit/json_samples/root.json') as f:
            connector_mock.get.return_value.json.return_value = (
                json.load(f))
        main.Sushy('http://foo.bar:1234', 'foo', 'bar',
                   connector=connector_mock)
        self.assertTrue(connector_mock.post.called)
        self.assertTrue(connector_mock.get.called)
        self.assertFalse(mock_Sushy_Connector.called)

    @mock.patch.object(system, 'SystemCollection', autospec=True)
    @mock.patch('sushy.Sushy.lazy_registries', autospec=True)
    def test_get_system_collection(
            self, mock_lazy_registries, mock_system_collection):
        self.root._standard_message_registries_path = None
        self.root.get_system_collection()
        mock_system_collection.assert_called_once_with(
            self.root._conn, '/redfish/v1/Systems',
            redfish_version=self.root.redfish_version,
            registries=mock_lazy_registries
        )

    @mock.patch.object(system, 'System', autospec=True)
    @mock.patch('sushy.Sushy.lazy_registries', autospec=True)
    def test_get_system(self, mock_lazy_registries, mock_system):
        self.root._standard_message_registries_path = None
        self.root.get_system('fake-system-id')
        mock_system.assert_called_once_with(
            self.root._conn, 'fake-system-id',
            redfish_version=self.root.redfish_version,
            registries=mock_lazy_registries)

    @mock.patch.object(system, 'SystemCollection', autospec=True)
    @mock.patch.object(system, 'System', autospec=True)
    @mock.patch('sushy.Sushy.lazy_registries', autospec=True)
    def test_get_system_default_ok(
            self, mock_lazy_registries, mock_system, mock_system_collection):
        self.root._standard_message_registries_path = None
        mock_system.path = 'fake-system-id'
        mock_members = mock_system_collection.return_value.get_members
        mock_members.return_value = [mock_system]
        self.root.get_system()
        mock_system_collection.assert_called_once_with(
            self.root._conn, '/redfish/v1/Systems',
            redfish_version=self.root.redfish_version,
            registries=mock_lazy_registries
        )
        mock_system.assert_called_once_with(
            self.root._conn, 'fake-system-id',
            redfish_version=self.root.redfish_version,
            registries=mock_lazy_registries)

    @mock.patch.object(system, 'SystemCollection', autospec=True)
    @mock.patch.object(system, 'System', autospec=True)
    @mock.patch('sushy.Sushy.lazy_registries', autospec=True)
    def test_get_system_default_failure(
            self, mock_lazy_registries, mock_system, mock_system_collection):
        self.root._standard_message_registries_path = None
        mock_members = mock_system_collection.return_value.get_members
        mock_members.return_value = []
        self.assertRaises(exceptions.UnknownDefaultError, self.root.get_system)
        mock_system_collection.assert_called_once_with(
            self.root._conn, '/redfish/v1/Systems',
            redfish_version=self.root.redfish_version,
            registries=mock_lazy_registries
        )

    @mock.patch.object(chassis, 'Chassis', autospec=True)
    def test_get_chassis(self, mock_chassis):
        self.root.get_chassis('fake-chassis-id')
        mock_chassis.assert_called_once_with(
            self.root._conn, 'fake-chassis-id',
            self.root.redfish_version, self.root.lazy_registries)

    @mock.patch.object(chassis, 'ChassisCollection', autospec=True)
    @mock.patch.object(chassis, 'Chassis', autospec=True)
    @mock.patch('sushy.Sushy.lazy_registries', autospec=True)
    def test_get_chassis_default_ok(
            self, mock_lazy_registries, mock_chassis, mock_chassis_collection):
        self.root._standard_message_registries_path = None
        mock_chassis.path = 'fake-chassis-id'
        mock_members = mock_chassis_collection.return_value.get_members
        mock_members.return_value = [mock_chassis]
        self.root.get_chassis()
        mock_chassis_collection.assert_called_once_with(
            self.root._conn, '/redfish/v1/Chassis',
            redfish_version=self.root.redfish_version,
            registries=mock_lazy_registries
        )
        mock_chassis.assert_called_once_with(
            self.root._conn, 'fake-chassis-id',
            redfish_version=self.root.redfish_version,
            registries=mock_lazy_registries
        )

    @mock.patch.object(chassis, 'ChassisCollection', autospec=True)
    @mock.patch.object(chassis, 'Chassis', autospec=True)
    @mock.patch('sushy.Sushy.lazy_registries', autospec=True)
    def test_get_chassis_default_failure(
            self, mock_lazy_registries, mock_chassis, mock_chassis_collection):
        self.root._standard_message_registries_path = None
        mock_members = mock_chassis_collection.return_value.get_members
        mock_members.return_value = []
        self.assertRaises(
            exceptions.UnknownDefaultError, self.root.get_chassis)
        mock_chassis_collection.assert_called_once_with(
            self.root._conn, '/redfish/v1/Chassis',
            redfish_version=self.root.redfish_version,
            registries=mock_lazy_registries
        )

    @mock.patch.object(chassis, 'ChassisCollection', autospec=True)
    def test_get_chassis_collection(self, chassis_collection_mock):
        self.root.get_chassis_collection()
        chassis_collection_mock.assert_called_once_with(
            self.root._conn, '/redfish/v1/Chassis',
            self.root.redfish_version, self.root.lazy_registries)

    @mock.patch.object(fabric, 'Fabric', autospec=True)
    def test_get_fabric(self, mock_fabric):
        self.root.get_fabric('fake-fabric-id')
        mock_fabric.assert_called_once_with(
            self.root._conn, 'fake-fabric-id',
            self.root.redfish_version, self.root.lazy_registries)

    @mock.patch.object(fabric, 'FabricCollection', autospec=True)
    def test_get_fabric_collection(self, fabric_collection_mock):
        self.root.get_fabric_collection()
        fabric_collection_mock.assert_called_once_with(
            self.root._conn, '/redfish/v1/Fabrics',
            self.root.redfish_version, self.root.lazy_registries)

    @mock.patch.object(manager, 'ManagerCollection', autospec=True)
    def test_get_manager_collection(self, ManagerCollection_mock):
        self.root.get_manager_collection()
        ManagerCollection_mock.assert_called_once_with(
            self.root._conn, '/redfish/v1/Managers',
            self.root.redfish_version, self.root.lazy_registries)

    @mock.patch.object(manager, 'Manager', autospec=True)
    def test_get_manager(self, Manager_mock):
        self.root.get_manager('fake-manager-id')
        Manager_mock.assert_called_once_with(
            self.root._conn, 'fake-manager-id',
            self.root.redfish_version, self.root.lazy_registries)

    @mock.patch.object(manager, 'ManagerCollection', autospec=True)
    @mock.patch.object(manager, 'Manager', autospec=True)
    @mock.patch('sushy.Sushy.lazy_registries', autospec=True)
    def test_get_manager_default_ok(
            self, mock_lazy_registries, mock_manager, mock_manager_collection):
        self.root._standard_message_registries_path = None
        mock_manager.path = 'fake-manager-id'
        mock_members = mock_manager_collection.return_value.get_members
        mock_members.return_value = [mock_manager]
        self.root.get_manager()
        mock_manager_collection.assert_called_once_with(
            self.root._conn, '/redfish/v1/Managers',
            redfish_version=self.root.redfish_version,
            registries=mock_lazy_registries
        )
        mock_manager.assert_called_once_with(
            self.root._conn, 'fake-manager-id',
            redfish_version=self.root.redfish_version,
            registries=mock_lazy_registries)

    @mock.patch.object(manager, 'ManagerCollection', autospec=True)
    @mock.patch.object(manager, 'Manager', autospec=True)
    @mock.patch('sushy.Sushy.lazy_registries', autospec=True)
    def test_get_manager_default_failure(
            self, mock_lazy_registries, mock_manager, mock_system_collection):
        self.root._standard_message_registries_path = None
        mock_members = mock_system_collection.return_value.get_members
        mock_members.return_value = []
        self.assertRaises(
            exceptions.UnknownDefaultError, self.root.get_manager)
        mock_system_collection.assert_called_once_with(
            self.root._conn, '/redfish/v1/Managers',
            redfish_version=self.root.redfish_version,
            registries=mock_lazy_registries
        )

    @mock.patch.object(sessionservice, 'SessionService', autospec=True)
    def test_get_sessionservice(self, mock_sess_serv):
        self.root.get_session_service()
        mock_sess_serv.assert_called_once_with(
            self.root._conn, '/redfish/v1/SessionService',
            self.root.redfish_version)

    @mock.patch.object(session, 'Session', autospec=True)
    def test_get_session(self, mock_sess):
        self.root.get_session('asdf')
        mock_sess.assert_called_once_with(
            self.root._conn, 'asdf',
            self.root.redfish_version, self.root.lazy_registries)

    @mock.patch.object(updateservice, 'UpdateService', autospec=True)
    def test_get_update_service(self, mock_upd_serv):
        self.root.get_update_service()
        mock_upd_serv.assert_called_once_with(
            self.root._conn, '/redfish/v1/UpdateService',
            self.root.redfish_version, self.root.lazy_registries)

    @mock.patch.object(message_registry_file,
                       'MessageRegistryFileCollection',
                       autospec=True)
    def test__get_registry_collection(
        self, MessageRegistryFileCollection_mock):
        self.root._get_registry_collection()
        MessageRegistryFileCollection_mock.assert_called_once_with(
            self.root._conn, '/redfish/v1/Registries',
            self.root.redfish_version)

    @mock.patch.object(
        compositionservice, 'CompositionService', autospec=True)
    def test_get_composition_service(self, mock_comp_ser):
        self.root.get_composition_service()
        mock_comp_ser.assert_called_once_with(
            self.root._conn, '/redfish/v1/CompositionService',
            self.root.redfish_version, self.root.lazy_registries)

    def test__get_standard_message_registry_collection(self):
        registries = self.root._get_standard_message_registry_collection()

        self.assertEqual(5, len(registries))
        self.assertIn('Base.1.3.0', {r.identity for r in registries})

    @mock.patch('sushy.Sushy._get_standard_message_registry_collection',
                autospec=True)
    @mock.patch('sushy.Sushy._get_registry_collection', autospec=True)
    def test__get_message_registries(self, mock_col, mock_st_col):
        mock_msg_reg1 = mock.Mock()
        mock_msg_reg1.registry_prefix = 'RegistryA'
        mock_msg_reg1.registry_version = '2.0.0'
        mock_msg_reg1.language = 'en'
        mock_st_col.return_value = [mock_msg_reg1]

        mock_msg_reg2 = mock.Mock()
        mock_msg_reg2.registry_prefix = 'RegistryB'
        mock_msg_reg2.registry_version = '1.0.0'
        mock_msg_reg_file = mock.Mock()
        mock_msg_reg_file.identity = 'Messages'
        mock_msg_reg_file.registry = 'RegistryB.1.0'
        mock_msg_reg_file.get_message_registry.return_value = mock_msg_reg2
        mock_col.return_value.get_members.return_value = [mock_msg_reg_file]

        registries = self.root.registries
        self.assertEqual({'RegistryA.2.0': mock_msg_reg1,
                          'RegistryB.1.0': mock_msg_reg2,
                          'Messages': mock_msg_reg2}, registries)

    @mock.patch('sushy.Sushy._get_standard_message_registry_collection',
                autospec=True)
    @mock.patch('sushy.Sushy._get_registry_collection', autospec=True)
    def test__get_message_registries_caching(self, mock_col, mock_st_col):
        mock_msg_reg1 = mock.Mock()
        mock_msg_reg1.registry_prefix = 'RegistryA'
        mock_msg_reg1.registry_version = '2.0.0'
        mock_msg_reg1.language = 'en'
        mock_st_col.return_value = [mock_msg_reg1]

        mock_msg_reg2 = mock.Mock()
        mock_msg_reg2.registry_prefix = 'RegistryB'
        mock_msg_reg2.registry_version = '1.0.0'
        mock_msg_reg_file = mock.Mock()
        mock_msg_reg_file.identity = 'Messages'
        mock_msg_reg_file.registry = 'RegistryB.1.0'
        mock_msg_reg_file.get_message_registry.return_value = mock_msg_reg2
        mock_col.return_value.get_members.return_value = [mock_msg_reg_file]

        registries = self.root.registries

        self.assertEqual(1, mock_col.call_count)
        self.assertEqual(1, mock_st_col.call_count)

        cached_registries = self.root.registries

        self.assertEqual(1, mock_col.call_count)
        self.assertEqual(1, mock_st_col.call_count)

        expected = {
            'RegistryA.2.0': mock_msg_reg1,
            'RegistryB.1.0': mock_msg_reg2,
            'Messages': mock_msg_reg2
        }

        self.assertEqual(expected, registries)
        self.assertEqual(cached_registries, registries)

    @mock.patch('sushy.Sushy._get_standard_message_registry_collection',
                autospec=True)
    @mock.patch('sushy.Sushy._get_registry_collection', autospec=True)
    def test_registries_provided_empty(self, mock_col, mock_st_col):
        mock_msg_reg1 = mock.Mock()
        mock_msg_reg1.registry_prefix = 'RegistryA'
        mock_msg_reg1.registry_version = '2.0.0'
        mock_msg_reg1.language = 'en'
        mock_st_col.return_value = [mock_msg_reg1]
        mock_col.return_value = None

        registries = self.root.registries
        self.assertEqual({'RegistryA.2.0': mock_msg_reg1}, registries)

    @mock.patch('sushy.Sushy.registries', autospec=True)
    def test_lazy_registries(self, mock_registries):
        registries = self.root.lazy_registries
        self.assertEqual(0, mock_registries.__getitem__.call_count)
        registries[1]
        self.assertEqual(1, mock_registries.__getitem__.call_count)

    def test_get_sessions_path(self):
        expected = '/redfish/v1/SessionService/Sessions'
        self.assertEqual(expected, self.root.get_sessions_path())


class BareMinimumMainTestCase(base.TestCase):

    def setUp(self):
        super(BareMinimumMainTestCase, self).setUp()
        self.conn = mock.MagicMock()
        with open('sushy/tests/unit/json_samples/'
                  'bare_minimum_root.json') as f:
            self.conn.get.return_value.json.return_value = json.load(f)
        self.root = main.Sushy('http://foo.bar:1234', verify=True,
                               auth=mock.MagicMock(), connector=self.conn)

    def test_get_system_collection_when_systems_attr_absent(self):
        self.assertRaisesRegex(
            exceptions.MissingAttributeError,
            'Systems/@odata.id', self.root.get_system_collection)

    def test_get_manager_collection_when_managers_attr_absent(self):
        self.assertRaisesRegex(
            exceptions.MissingAttributeError,
            'Managers/@odata.id', self.root.get_manager_collection)

    def test_get_chassis_collection_when_chassis_attr_absent(self):
        self.assertRaisesRegex(
            exceptions.MissingAttributeError,
            'Chassis/@odata.id', self.root.get_chassis_collection)

    def test_get_fabric_collection_when_fabrics_attr_absent(self):
        self.assertRaisesRegex(
            exceptions.MissingAttributeError,
            'Fabrics/@odata.id', self.root.get_fabric_collection)

    def test_get_session_service_when_sessionservice_attr_absent(self):
        self.assertRaisesRegex(
            exceptions.MissingAttributeError,
            'SessionService/@odata.id', self.root.get_session_service)

    def test_get_update_service_when_updateservice_attr_absent(self):
        self.assertRaisesRegex(
            exceptions.MissingAttributeError,
            'UpdateService/@odata.id', self.root.get_update_service)

    def test_get_composition_service_when_compositionservice_attr_absent(self):
        self.assertRaisesRegex(
            exceptions.MissingAttributeError,
            'CompositionService/@odata.id', self.root.get_composition_service)

    def test__get_registry_collection_when_registries_attr_absent(self):
        self.assertIsNone(self.root._get_registry_collection())

    def test_get_sessions_path_fail(self):
        self.assertRaisesRegex(
            exceptions.MissingAttributeError,
            'Links/Sessions/@data.id', self.root.get_sessions_path)
