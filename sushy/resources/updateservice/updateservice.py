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
from sushy.resources.updateservice import mappings as up_maps
from sushy.resources.updateservice import softwareinventory
from sushy import utils

LOG = logging.getLogger(__name__)


class SimpleUpdateActionField(common.ActionField):

    image_uri = base.Field('ImageURI')
    """The URI of the software image to be installed"""

    targets = base.Field('Targets')
    """The array of URIs indicating where the update image is to be""" + \
        """applied"""

    transfer_protocol = base.MappedField(
        'TransferProtocol',
        up_maps.TRANSFER_PROTOCOL_TYPE_VALUE_MAP)
    """The network protocol used by the Update Service"""


class ActionsField(base.CompositeField):

    simple_update = SimpleUpdateActionField(
        '#UpdateService.SimpleUpdate')


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

    def __init__(self, connector, identity, redfish_version=None):
        """A class representing a UpdateService

        :param connector: A Connector instance
        :param identity: The identity of the UpdateService resource
        :param redfish_version: The version of RedFish. Used to construct
            the object according to schema of given version
        """
        super(UpdateService, self).__init__(
            connector,
            identity,
            redfish_version)

    def _get_simple_update_element(self):
        simple_update_action = self._actions.simple_update
        if not simple_update_action:
            raise exceptions.MissingAttributeError(
                action='#UpdateService.SimpleUpdate',
                resource=self._path)
        return simple_update_action

    def get_allowed_transfer_protocol_values(self):
        """Get the allowed values for transfer protocol.

        :returns: A set of allowed values.
        :raises: MissingAttributeError, if Actions/#UpdateService.SimpleUpdate
            attribute not present.
        """
        simple_update_action = self._get_simple_update_element()

        if not simple_update_action.transfer_protocol:
            LOG.warning(
                'Could not figure out the allowed values for the simple '
                'update action for UpdateService %s', self.identity)
            return set(up_maps.TRANSFER_PROTOCOL_TYPE_VALUE_MAP_REV)

        return set(up_maps.TRANSFER_PROTOCOL_TYPE_VALUE_MAP[v] for v in
                   simple_update_action.transfer_protocol if v in
                   up_maps.TRANSFER_PROTOCOL_TYPE_VALUE_MAP)

    def simple_update(self, image_uri, targets, transfer_protocol='HTTP'):
        """Simple Update is used to update software components"""
        transfer_protocol = transfer_protocol

        valid_transfer_protocols = self.get_allowed_transfer_protocol_values()
        if transfer_protocol not in valid_transfer_protocols:
            raise exceptions.InvalidParameterValueError(
                parameter='transfer_protocol', value=transfer_protocol,
                valid_values=valid_transfer_protocols)

        self._conn.post(data={
            'ImageURI': image_uri,
            'Targets': targets,
            'TransferProtocol': transfer_protocol})

    def _get_software_inventory_collection_path(self):
        """Helper function to find the SoftwareInventoryCollections path"""
        soft_inv_col = self.json.get('SoftwareInventory')
        if not soft_inv_col:
            raise exceptions.MissingAttributeError(
                attribute='SoftwareInventory', resource=self._path)
        return soft_inv_col.get('@odata.id')

    @property
    @utils.cache_it
    def software_inventory(self):
        """Property to reference SoftwareInventoryCollection instance"""
        return softwareinventory.SoftwareInventoryCollection(
            self._conn, self._get_software_inventory_collection_path,
            redfish_version=self.redfish_version)

    @property
    @utils.cache_it
    def firmware_inventory(self):
        """Property to reference SoftwareInventoryCollection instance"""
        return softwareinventory.SoftwareInventoryCollection(
            self._conn, self._get_software_inventory_collection_path,
            redfish_version=self.redfish_version)
