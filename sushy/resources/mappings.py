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

PROTOCOL_TYPE_VALUE_MAP = {
    'AHCI': res_cons.PROTOCOL_TYPE_AHCI,
    'FC': res_cons.PROTOCOL_TYPE_FC,
    'FCP': res_cons.PROTOCOL_TYPE_FCP,
    'FCoE': res_cons.PROTOCOL_TYPE_FCoE,
    'FICON': res_cons.PROTOCOL_TYPE_FICON,
    'FTP': res_cons.PROTOCOL_TYPE_FTP,
    'HTTP': res_cons.PROTOCOL_TYPE_HTTP,
    'HTTPS': res_cons.PROTOCOL_TYPE_HTTPS,
    'I2C': res_cons.PROTOCOL_TYPE_I2C,
    'NFSv3': res_cons.PROTOCOL_TYPE_NFSv3,
    'NFSv4': res_cons.PROTOCOL_TYPE_NFSv4,
    'NVMe': res_cons.PROTOCOL_TYPE_NVMe,
    'NVMeOverFabrics': res_cons.PROTOCOL_TYPE_NVMeOverFabrics,
    'OEM': res_cons.PROTOCOL_TYPE_OEM,
    'PCIe': res_cons.PROTOCOL_TYPE_PCIe,
    'RoCE': res_cons.PROTOCOL_TYPE_RoCE,
    'RoCEv2': res_cons.PROTOCOL_TYPE_RoCEv2,
    'SAS': res_cons.PROTOCOL_TYPE_SAS,
    'SATA': res_cons.PROTOCOL_TYPE_SATA,
    'SFTP': res_cons.PROTOCOL_TYPE_SFTP,
    'SMB': res_cons.PROTOCOL_TYPE_SMB,
    'UHCI': res_cons.PROTOCOL_TYPE_UHCI,
    'USB': res_cons.PROTOCOL_TYPE_USB,
    'iSCSI': res_cons.PROTOCOL_TYPE_iSCSI,
    'iWARP': res_cons.PROTOCOL_TYPE_iWARP,
}

DUR_NAME_FORMAT_VALUE_MAP = {
    'EUI': res_cons.DURABLE_NAME_FORMAT_EUI,
    'FC_WWN': res_cons.DURABLE_NAME_FORMAT_FC_WWN,
    'NAA': res_cons.DURABLE_NAME_FORMAT_NAA,
    'NQN': res_cons.DURABLE_NAME_FORMAT_NQN,
    'NSID': res_cons.DURABLE_NAME_FORMAT_NSID,
    'UUID': res_cons.DURABLE_NAME_FORMAT_UUID,
    'iQN': res_cons.DURABLE_NAME_FORMAT_iQN,
}

APPLY_TIME_VALUE_MAP = {
    'Immediate': res_cons.APPLY_TIME_IMMEDIATE,
    'OnReset': res_cons.APPLY_TIME_ON_RESET,
    'AtMaintenanceWindowStart':
        res_cons.APPLY_TIME_MAINT_START,
    'InMaintenanceWindowOnReset':
        res_cons.APPLY_TIME_MAINT_RESET,
}

APPLY_TIME_VALUE_MAP_REV = utils.revert_dictionary(APPLY_TIME_VALUE_MAP)
