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

# This is referred from Redfish standard schema.
# http://redfish.dmtf.org/schemas/v1/StorageController.v1_6_0.json

import logging

from sushy.resources import base
from sushy.resources import common
from sushy.resources import constants as res_cons
from sushy.resources import settings
from sushy.resources.system.storage import constants
from sushy.taskmonitor import TaskMonitor
from sushy import utils


LOG = logging.getLogger(__name__)


class StorageController(base.ResourceBase):
    """Storage controller"""

    identity = base.Field('Id', required=True)
    """The storage controller identity"""

    name = base.Field('Name', required=True)
    """The name of the storage controller"""

    status = common.StatusField('Status')
    """Describes the status and health of the resource and its children."""

    identifiers = common.IdentifiersListField('Identifiers', default=[])
    """The Durable names for the storage controller."""

    speed_gbps = base.Field('SpeedGbps')
    """The maximum speed of the storage controller's device interface."""

    controller_protocols = base.MappedListField(
        'SupportedControllerProtocols', res_cons.Protocol)
    """The protocols by which this storage controller can be communicated to"""

    device_protocols = base.MappedListField('SupportedDeviceProtocols',
                                            res_cons.Protocol)
    """The protocols that can be used to communicate with attached devices"""

    raid_types = base.MappedListField('SupportedRAIDTypes', constants.RAIDType)
    """The set of RAID types supported by the storage controller."""

    _settings = settings.SettingsField()
    """Future intended state for settings that can't be updated immediately."""

    @property
    @utils.cache_it
    def pending_settings(self):
        """Pending Storage Controller settings resource"""
        return StorageController(
            self._conn, self._settings.resource_uri,
            registries=None,
            redfish_version=self.redfish_version, root=self.root)

    @property
    def supported_apply_times(self):
        """List of supported BIOS update apply times

        :returns: List of supported update apply time names
        """
        return self._settings._supported_apply_times

    def update(self, payload, apply_time=None, maint_window_start_time=None,
               maint_window_duration=None):
        """Updates writable properties

        Supports updating properties that require reboot.

        :param payload: dictionary with properties to update
        :param apply_time: When to update the attributes. Optional.
            A :py:class:`sushy.ApplyTime` value.
        :param maint_window_start_time: The start time of a maintenance window,
            datetime. Required when updating during maintenance window and
            default maintenance window not set by the system.
        :param maint_window_duration: Duration of maintenance time since
            maintenance window start time in seconds. Required when updating
            during maintenance window and default maintenance window not
            set by the system.
        :returns: TaskMonitor if async task or None
        """
        payload = utils.process_apply_time_input(
            payload, apply_time, maint_window_start_time,
            maint_window_duration)
        # NOTE(vanou): To retrieve current ETag value of @Redfish.Settings
        # but not update cached pending_settings, because cached property is
        # only this one and re-cache this is not required
        self.refresh(force=False)
        r = self._settings.commit(self._conn, payload)
        utils.cache_clear(self, force_refresh=False,
                          only_these=['pending_settings'])
        if r.status_code == 202:
            return TaskMonitor.from_response(
                self._conn, r, self._settings.resource_uri,
                self.redfish_version, self.registries)


class ControllerCollection(base.ResourceCollectionBase):

    @property
    def _resource_type(self):
        return StorageController

    @property
    @utils.cache_it
    def summary(self):
        """Summary of storage controllers

        :returns: dictionary of controller id-s and their status in format

        .. code-block:: python

          {'RAID.Integrated.1-1': {'Health': sushy.Health.OK,
                                   'State': sushy.State.ENABLED}}
        """
        controllers = {}
        for controller in self.get_members():
            controllers[controller.identity] = {
                'Health': controller.status.health,
                'State': controller.status.state,
            }
        return controllers

    def __init__(self, connector, path, redfish_version=None, registries=None,
                 root=None):
        """A class representing a ControllerCollection

        :param connector: A Connector instance
        :param path: The canonical path to the Controller collection resource
        :param redfish_version: The version of Redfish. Used to construct
            the object according to schema of the given version.
        :param registries: Dict of Redfish Message Registry objects to be
            used in any resource that needs registries to parse messages
        :param root: Sushy root object. Empty for Sushy root itself.
        """
        super(ControllerCollection, self).__init__(
            connector, path, redfish_version=redfish_version,
            registries=registries,
            root=root)
