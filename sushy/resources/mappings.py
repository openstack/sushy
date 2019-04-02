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

from sushy.resources import constants as res_cons
from sushy import utils


STATE_VALUE_MAP = {
    'Enabled': res_cons.STATE_ENABLED,
    'Disabled': res_cons.STATE_DISABLED,
    'Absent': res_cons.STATE_ABSENT,
}

STATE_VALUE_MAP_REV = (
    utils.revert_dictionary(STATE_VALUE_MAP))

HEALTH_VALUE_MAP = {
    'OK': res_cons.HEALTH_OK,
    'Warning': res_cons.HEALTH_WARNING,
    'Critical': res_cons.HEALTH_CRITICAL
}

HEALTH_VALUE_MAP_REV = (
    utils.revert_dictionary(HEALTH_VALUE_MAP))

PARAMTYPE_VALUE_MAP = {
    'string': res_cons.PARAMTYPE_STRING,
    'number': res_cons.PARAMTYPE_NUMBER
}

SEVERITY_VALUE_MAP = {
    'OK': res_cons.SEVERITY_OK,
    'Warning': res_cons.SEVERITY_WARNING,
    'Critical': res_cons.SEVERITY_CRITICAL
}

INDICATOR_LED_VALUE_MAP = {
    'Lit': res_cons.INDICATOR_LED_LIT,
    'Blinking': res_cons.INDICATOR_LED_BLINKING,
    'Off': res_cons.INDICATOR_LED_OFF,
    'Unknown': res_cons.INDICATOR_LED_UNKNOWN,
}

INDICATOR_LED_VALUE_MAP_REV = utils.revert_dictionary(INDICATOR_LED_VALUE_MAP)

POWER_STATE_VALUE_MAP = {
    'On': res_cons.POWER_STATE_ON,
    'Off': res_cons.POWER_STATE_OFF,
    'PoweringOn': res_cons.POWER_STATE_POWERING_ON,
    'PoweringOff': res_cons.POWER_STATE_POWERING_OFF,
}

POWER_STATE_MAP_REV = utils.revert_dictionary(POWER_STATE_VALUE_MAP)

RESET_TYPE_VALUE_MAP = {
    'On': res_cons.RESET_TYPE_ON,
    'ForceOff': res_cons.RESET_TYPE_FORCE_OFF,
    'GracefulShutdown': res_cons.RESET_TYPE_GRACEFUL_SHUTDOWN,
    'GracefulRestart': res_cons.RESET_TYPE_GRACEFUL_RESTART,
    'ForceRestart': res_cons.RESET_TYPE_FORCE_RESTART,
    'Nmi': res_cons.RESET_TYPE_NMI,
    'ForceOn': res_cons.RESET_TYPE_FORCE_ON,
    'PushPowerButton': res_cons.RESET_TYPE_PUSH_POWER_BUTTON,
    'PowerCycle': res_cons.RESET_TYPE_POWER_CYCLE,
}

RESET_TYPE_VALUE_MAP_REV = utils.revert_dictionary(RESET_TYPE_VALUE_MAP)
