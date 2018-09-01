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
