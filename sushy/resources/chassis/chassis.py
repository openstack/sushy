# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

# This is referred from Redfish standard schema.
# http://redfish.dmtf.org/schemas/v1/Chassis.v1_8_0.json

import logging

from sushy import exceptions
from sushy.resources import base
from sushy.resources.chassis import mappings as cha_maps
from sushy.resources.chassis.power import power
from sushy.resources.chassis.thermal import thermal
from sushy.resources import common
from sushy.resources.manager import manager
from sushy.resources import mappings as res_maps
from sushy import utils


LOG = logging.getLogger(__name__)


class ActionsField(base.CompositeField):
    reset = common.ResetActionField('#Chassis.Reset')


class PhysicalSecurity(base.CompositeField):
    intrusion_sensor = base.MappedField('IntrusionSensor',
                                        cha_maps.CHASSIS_INTRUSION_SENSOR_MAP)
    """IntrusionSensor
    This indicates the known state of the physical security sensor, such as if
    it is hardware intrusion detected.
    """

    intrusion_sensor_number = base.Field('IntrusionSensorNumber')
    """A numerical identifier to represent the physical security sensor"""

    intrusion_sensor_re_arm = (
        base.MappedField('IntrusionSensorReArm',
                         cha_maps.CHASSIS_INTRUSION_SENSOR_RE_ARM_MAP))
    """This indicates how the Normal state to be restored"""


class Chassis(base.ResourceBase):
    """Chassis resource

    The Chassis represents the physical components of a system. This
    resource represents the sheet-metal confined spaces and logical zones
    such as racks, enclosures, chassis and all other containers.
    """

    chassis_type = base.MappedField('ChassisType',
                                    cha_maps.CHASSIS_TYPE_VALUE_MAP,
                                    required=True)
    """The type of physical form factor of the chassis"""

    identity = base.Field('Id', required=True)
    """Identifier for the chassis"""

    name = base.Field('Name', required=True)
    """The chassis name"""

    asset_tag = base.Field('AssetTag')
    """The user assigned asset tag of this chassis"""

    depth_mm = base.Field('DepthMm')
    """Depth in millimeters
    The depth of the chassis. The value of this property shall represent
    the depth (length) of the chassis (in millimeters) as specified by the
    manufacturer.
    """

    description = base.Field('Description')
    """The chassis description"""

    height_mm = base.Field('HeightMm')
    """Height in millimeters
    The height of the chassis. The value of this property shall represent
    the height of the chassis (in millimeters) as specified by the
    manufacturer.
    """

    indicator_led = base.MappedField('IndicatorLED',
                                     res_maps.INDICATOR_LED_VALUE_MAP)
    """The state of the indicator LED, used to identify the chassis"""

    manufacturer = base.Field('Manufacturer')
    """The manufacturer of this chassis"""

    model = base.Field('Model')
    """The model number of the chassis"""

    part_number = base.Field('PartNumber')
    """The part number of the chassis"""

    physical_security = PhysicalSecurity('PhysicalSecurity')
    """PhysicalSecurity
    This value of this property shall contain the sensor state of the physical
    security.
    """

    power_state = base.MappedField('PowerState',
                                   res_maps.POWER_STATE_VALUE_MAP)
    """The current power state of the chassis"""

    serial_number = base.Field('SerialNumber')
    """The serial number of the chassis"""

    sku = base.Field('SKU')
    """Stock-keeping unit number (SKU)
    The value of this property shall be the stock-keeping unit number for
    this chassis.
    """

    status = common.StatusField('Status')
    """Status and Health
    This property describes the status and health of the chassis and its
    children.
    """

    uuid = base.Field('UUID')
    """The Universal Unique Identifier (UUID) for this Chassis."""

    weight_kg = base.Field('WeightKg')
    """Weight in kilograms
    The value of this property shall represent the published mass (commonly
    referred to as weight) of the chassis (in kilograms).
    """

    width_mm = base.Field('WidthMm')
    """Width in millimeters
    The value of this property shall represent the width of the chassis
    (in millimeters) as specified by the manufacturer.
    """

    _actions = ActionsField('Actions')

    def __init__(self, connector, identity, redfish_version=None,
                 registries=None):
        """A class representing a Chassis

        :param connector: A Connector instance
        :param identity: The identity of the Chassis resource
        :param redfish_version: The version of RedFish. Used to construct
            the object according to schema of the given version.
        :param registries: Dict of Redfish Message Registry objects to be
            used in any resource that needs registries to parse messages
        """
        super(Chassis, self).__init__(
            connector, identity, redfish_version, registries)

    def _get_reset_action_element(self):
        reset_action = self._actions.reset

        if not reset_action:
            raise exceptions.MissingActionError(action='#Chassis.Reset',
                                                resource=self._path)
        return reset_action

    def get_allowed_reset_chassis_values(self):
        """Get the allowed values for resetting the chassis.

        :returns: A set of allowed values.
        :raises: MissingAttributeError, if Actions/#Chassis.Reset attribute
            not present.
        """
        reset_action = self._get_reset_action_element()

        if not reset_action.allowed_values:
            LOG.warning('Could not figure out the allowed values for the '
                        'reset chassis action for Chassis %s', self.identity)
            return set(res_maps.RESET_TYPE_VALUE_MAP_REV)

        return set([res_maps.RESET_TYPE_VALUE_MAP[v] for v in
                    set(res_maps.RESET_TYPE_VALUE_MAP).
                    intersection(reset_action.allowed_values)])

    def reset_chassis(self, value):
        """Reset the chassis.

        :param value: The target value.
        :raises: InvalidParameterValueError, if the target value is not
            allowed.
        """
        valid_resets = self.get_allowed_reset_chassis_values()
        if value not in valid_resets:
            raise exceptions.InvalidParameterValueError(
                parameter='value', value=value, valid_values=valid_resets)

        value = res_maps.RESET_TYPE_VALUE_MAP_REV[value]
        target_uri = self._get_reset_action_element().target_uri

        LOG.debug('Resetting the Chassis %s ...', self.identity)
        self._conn.post(target_uri, data={'ResetType': value})
        LOG.info('The Chassis %s is being reset', self.identity)

    def set_indicator_led(self, state):
        """Set IndicatorLED to the given state.

        :param state: Desired LED state, lit (INDICATOR_LED_LIT), blinking
            (INDICATOR_LED_BLINKING), off (INDICATOR_LED_OFF)
        :raises: InvalidParameterValueError, if any information passed is
            invalid.
        """
        if state not in res_maps.INDICATOR_LED_VALUE_MAP_REV:
            raise exceptions.InvalidParameterValueError(
                parameter='state', value=state,
                valid_values=list(res_maps.INDICATOR_LED_VALUE_MAP_REV))

        data = {
            'IndicatorLED': res_maps.INDICATOR_LED_VALUE_MAP_REV[state]
        }

        self._conn.patch(self.path, data=data)
        self.invalidate()

    @property
    @utils.cache_it
    def managers(self):
        """A list of managers for this chassis.

        Returns a list of `Manager` objects representing the managers
        that manage this chassis.

        :raises: MissingAttributeError if '@odata.id' field is missing.
        :returns: A list of `Manager` instances
        """
        paths = utils.get_sub_resource_path_by(
            self, ["Links", "ManagedBy"], is_collection=True)

        return [manager.Manager(self._conn, path,
                                self.redfish_version, self.registries)
                for path in paths]

    @property
    @utils.cache_it
    def systems(self):
        """A list of systems residing in this chassis.

        Returns a list of `System` objects representing systems being
        mounted in this chassis/cabinet.

        :raises: MissingAttributeError if '@odata.id' field is missing.
        :returns: A list of `System` instances
        """
        paths = utils.get_sub_resource_path_by(
            self, ["Links", "ComputerSystems"], is_collection=True)

        from sushy.resources.system import system
        return [system.System(self._conn, path,
                              self.redfish_version, self.registries)
                for path in paths]

    @property
    @utils.cache_it
    def power(self):
        """Property to reference `Power` instance

        It is set once when the first time it is queried. On refresh,
        this property is marked as stale (greedy-refresh not done).
        Here the actual refresh of the sub-resource happens, if stale.
        """
        return power.Power(
            self._conn,
            utils.get_sub_resource_path_by(self, 'Power'),
            self.redfish_version, self.registries)

    @property
    @utils.cache_it
    def thermal(self):
        """Property to reference `Thermal` instance

        It is set once when the first time it is queried. On refresh,
        this property is marked as stale (greedy-refresh not done).
        Here the actual refresh of the sub-resource happens, if stale.
        """
        return thermal.Thermal(
            self._conn,
            utils.get_sub_resource_path_by(self, 'Thermal'),
            self.redfish_version, self.registries)


class ChassisCollection(base.ResourceCollectionBase):

    @property
    def _resource_type(self):
        return Chassis

    def __init__(self, connector, path, redfish_version=None, registries=None):
        """A class representing a ChassisCollection

        :param connector: A Connector instance
        :param path: The canonical path to the Chassis collection resource
        :param redfish_version: The version of RedFish. Used to construct
            the object according to schema of the given version.
        :param registries: Dict of Redfish Message Registry objects to be
            used in any resource that needs registries to parse messages
        """
        super(ChassisCollection, self).__init__(
            connector, path, redfish_version, registries)
