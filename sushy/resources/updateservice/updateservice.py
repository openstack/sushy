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

# This is referred from Redfish standard schema.
# https://redfish.dmtf.org/schemas/UpdateService.v1_2_2.json

import logging

from sushy import exceptions
from sushy.resources import base
from sushy.resources import common
from sushy.resources.updateservice import constants as up_cons
from sushy.resources.updateservice import softwareinventory
from sushy import taskmonitor
from sushy import utils

LOG = logging.getLogger(__name__)


class ActionsField(base.CompositeField):

    simple_update = common.ActionField('#UpdateService.SimpleUpdate')


class UpdateService(base.ResourceBase):

    identity = base.Field('Id', required=True)
    """The update service identity"""

    http_push_uri = base.Field('HttpPushUri')
    """The URI used to perform an HTTP or HTTPS push update to the Update
    Service"""

    http_push_uri_targets = base.Field('HttpPushUriTargets')
    """The array of URIs indicating the target for applying the""" + \
        """update image"""

    http_push_uri_targets_busy = base.Field('HttpPushUriTargetsBusy')
    """This represents if the HttpPushUriTargets property is reserved""" + \
        """by anyclient"""

    name = base.Field('Name', required=True)
    """The update service name"""

    service_enabled = base.Field('ServiceEnabled')
    """The status of whether this service is enabled"""

    status = common.StatusField('Status')
    """The status of the update service"""

    _actions = ActionsField('Actions', required=True)

    _firmware_inventory_path = base.Field(['FirmwareInventory', '@odata.id'])

    _software_inventory_path = base.Field(['SoftwareInventory', '@odata.id'])

    def __init__(self, connector, identity, redfish_version=None,
                 registries=None, root=None):
        """A class representing a UpdateService

        :param connector: A Connector instance
        :param identity: The identity of the UpdateService resource
        :param redfish_version: The version of RedFish. Used to construct
            the object according to schema of given version
        :param registries: Dict of Redfish Message Registry objects to be
            used in any resource that needs registries to parse messages
        :param root: Sushy root object. Empty for Sushy root itself.
        """
        super(UpdateService, self).__init__(
            connector, identity, redfish_version=redfish_version,
            registries=registries, root=root)

    def _get_simple_update_element(self):
        simple_update_action = self._actions.simple_update
        if not simple_update_action:
            raise exceptions.MissingAttributeError(
                action='#UpdateService.SimpleUpdate',
                resource=self._path)
        return simple_update_action

    def _get_legacy_transfer_protocols(self):
        """Get the backward-compatible values for transfer protocol.

        :returns: A set of allowed values.
        """
        LOG.warning(
            'Could not figure out the allowed values for the simple '
            'update action for UpdateService %s', self.identity)
        return {x.value for x in up_cons.UpdateTransferProtocolType}

    def get_allowed_transfer_protocols(self):
        """Get the allowed values for transfer protocol.

        :returns: A set of allowed values.
        :raises: MissingAttributeError, if Actions/#UpdateService.SimpleUpdate
            attribute not present.
        """
        simple_update_action = self._get_simple_update_element()

        if not getattr(simple_update_action, 'transfer_protocol', None):
            LOG.debug(
                'Server does not constrain allowed transfer protocols for '
                'simple update action of UpdateService %s', self.identity)
            return set(up_cons.UpdateTransferProtocolType)

        return {simple_update_action.transfer_protocol}

    def simple_update(self, image_uri, targets=None,
                      transfer_protocol=up_cons.UPDATE_PROTOCOL_HTTP):
        """Simple Update is used to update software components.

        :returns: A task monitor.
        """
        valid_transfer_protocols = self.get_allowed_transfer_protocols()

        if transfer_protocol in valid_transfer_protocols:
            transfer_protocol = up_cons.UpdateTransferProtocolType(
                transfer_protocol).value

        else:
            legacy_transfer_protocols = self._get_legacy_transfer_protocols()

            if transfer_protocol not in legacy_transfer_protocols:
                raise exceptions.InvalidParameterValueError(
                    parameter='transfer_protocol', value=transfer_protocol,
                    valid_values=valid_transfer_protocols)

            LOG.warning(
                'Legacy transfer protocol constant %s is being used. '
                'Consider migrating to any of: %s', transfer_protocol,
                ', '.join(x.value for x in up_cons.UpdateTransferProtocolType))

        target_uri = self._get_simple_update_element().target_uri

        LOG.debug(
            'Updating software component %s via '
            '%s ...', image_uri, target_uri)

        data = {'ImageURI': image_uri, 'TransferProtocol': transfer_protocol}
        if targets:
            data['Targets'] = targets
        rsp = self._conn.post(target_uri, data=data)

        return taskmonitor.TaskMonitor.from_response(
            self._conn, rsp, target_uri,
            redfish_version=self.redfish_version, registries=self.registries)

    def get_task_monitor(self, task_monitor):
        """Used to retrieve a TaskMonitor.

        Deprecated: Use sushy.Sushy.get_task_monitor
        :returns: A task monitor.
        """
        return taskmonitor.TaskMonitor(
            self._conn,
            task_monitor,
            redfish_version=self.redfish_version,
            registries=self.registries,
            root=self.root)

    @property
    @utils.cache_it
    def software_inventory(self):
        """Property to reference SoftwareInventory collection instance"""
        if not self._software_inventory_path:
            raise exceptions.MissingAttributeError(
                attribute='SoftwareInventory/@odata.id',
                resource=self._software_inventory_path)

        return softwareinventory.SoftwareInventoryCollection(
            self._conn,
            self._software_inventory_path,
            redfish_version=self.redfish_version,
            registries=self.registries, root=self.root)

    @property
    @utils.cache_it
    def firmware_inventory(self):
        """Property to reference FirmwareInventory collection instance"""
        if not self._firmware_inventory_path:
            raise exceptions.MissingAttributeError(
                attribute='FirmwareInventory/@odata.id',
                resource=self._firmware_inventory_path)

        return softwareinventory.SoftwareInventoryCollection(
            self._conn,
            self._firmware_inventory_path,
            redfish_version=self.redfish_version,
            registries=self.registries, root=self.root)
