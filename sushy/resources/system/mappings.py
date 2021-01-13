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

from sushy.resources.system import constants as sys_cons
from sushy import utils


RESET_SYSTEM_VALUE_MAP = {
    'On': sys_cons.RESET_ON,
    'ForceOff': sys_cons.RESET_FORCE_OFF,
    'GracefulShutdown': sys_cons.RESET_GRACEFUL_SHUTDOWN,
    'GracefulRestart': sys_cons.RESET_GRACEFUL_RESTART,
    'ForceRestart': sys_cons.RESET_FORCE_RESTART,
    'Nmi': sys_cons.RESET_NMI,
    'ForceOn': sys_cons.RESET_FORCE_ON,
    'PushPowerButton': sys_cons.RESET_PUSH_POWER_BUTTON,
}

RESET_SYSTEM_VALUE_MAP_REV = utils.revert_dictionary(RESET_SYSTEM_VALUE_MAP)

BOOT_SOURCE_TARGET_MAP = {
    'None': sys_cons.BOOT_SOURCE_TARGET_NONE,
    'Pxe': sys_cons.BOOT_SOURCE_TARGET_PXE,
    'Floppy': sys_cons.BOOT_SOURCE_TARGET_FLOPPY,
    'Cd': sys_cons.BOOT_SOURCE_TARGET_CD,
    'Usb': sys_cons.BOOT_SOURCE_TARGET_USB,
    'Hdd': sys_cons.BOOT_SOURCE_TARGET_HDD,
    'BiosSetup': sys_cons.BOOT_SOURCE_TARGET_BIOS_SETUP,
    'Utilities': sys_cons.BOOT_SOURCE_TARGET_UTILITIES,
    'Diags': sys_cons.BOOT_SOURCE_TARGET_DIAGS,
    'SDCard': sys_cons.BOOT_SOURCE_TARGET_SD_CARD,
    'UefiTarget': sys_cons.BOOT_SOURCE_TARGET_UEFI_TARGET,
    'UefiShell': sys_cons.BOOT_SOURCE_TARGET_UEFI_SHELL,
    'UefiHttp': sys_cons.BOOT_SOURCE_TARGET_UEFI_HTTP,
}

BOOT_SOURCE_TARGET_MAP_REV = utils.revert_dictionary(BOOT_SOURCE_TARGET_MAP)

BOOT_SOURCE_MODE_MAP = {
    'Legacy': sys_cons.BOOT_SOURCE_MODE_BIOS,
    'UEFI': sys_cons.BOOT_SOURCE_MODE_UEFI,
}

BOOT_SOURCE_MODE_MAP_REV = utils.revert_dictionary(BOOT_SOURCE_MODE_MAP)

BOOT_SOURCE_ENABLED_MAP = {
    'Once': sys_cons.BOOT_SOURCE_ENABLED_ONCE,
    'Continuous': sys_cons.BOOT_SOURCE_ENABLED_CONTINUOUS,
    'Disabled': sys_cons.BOOT_SOURCE_ENABLED_DISABLED,
}

BOOT_SOURCE_ENABLED_MAP_REV = utils.revert_dictionary(BOOT_SOURCE_ENABLED_MAP)

PROCESSOR_ARCH_VALUE_MAP = {
    'x86': sys_cons.PROCESSOR_ARCH_x86,
    'IA-64': sys_cons.PROCESSOR_ARCH_IA_64,
    'ARM': sys_cons.PROCESSOR_ARCH_ARM,
    'MIPS': sys_cons.PROCESSOR_ARCH_MIPS,
    'OEM': sys_cons.PROCESSOR_ARCH_OEM,
}

PROCESSOR_ARCH_VALUE_MAP_REV = (
    utils.revert_dictionary(PROCESSOR_ARCH_VALUE_MAP))

PROCESSOR_TYPE_VALUE_MAP = {
    'Accelerator': sys_cons.PROCESSOR_TYPE_ACCELERATOR,
    'CPU': sys_cons.PROCESSOR_TYPE_CPU,
    'Core': sys_cons.PROCESSOR_TYPE_CORE,
    'DSP': sys_cons.PROCESSOR_TYPE_DSP,
    'FPGA': sys_cons.PROCESSOR_TYPE_FPGA,
    'GPU': sys_cons.PROCESSOR_TYPE_GPU,
    'OEM': sys_cons.PROCESSOR_TYPE_OEM,
    'Thread': sys_cons.PROCESSOR_TYPE_THREAD
}

PROCESSOR_TYPE_VALUE_MAP_REV = (
    utils.revert_dictionary(PROCESSOR_TYPE_VALUE_MAP))

PROCESSOR_INSTRUCTIONSET_VALUE_MAP = {
    'ARM-A32': sys_cons.PROCESSOR_INSTRUCTIONSET_ARM_A32,
    'ARM-A64': sys_cons.PROCESSOR_INSTRUCTIONSET_ARM_A64,
    'IA-64': sys_cons.PROCESSOR_INSTRUCTIONSET_IA_64,
    'MIPS32': sys_cons.PROCESSOR_INSTRUCTIONSET_MIPS32,
    'MIPS64': sys_cons.PROCESSOR_INSTRUCTIONSET_MIPS64,
    'OEM': sys_cons.PROCESSOR_INSTRUCTIONSET_OEM,
    'x86': sys_cons.PROCESSOR_INSTRUCTIONSET_x86,
    'x86-64': sys_cons.PROCESSOR_INSTRUCTIONSET_x86_64
}

PROCESSOR_INSTRUCTIONSET_VALUE_MAP_REV = (
    utils.revert_dictionary(PROCESSOR_INSTRUCTIONSET_VALUE_MAP))

SYSTEM_TYPE_VALUE_MAP = {
    'Physical': sys_cons.SYSTEM_TYPE_PHYSICAL,
    'Virtual': sys_cons.SYSTEM_TYPE_VIRTUAL,
    'OS': sys_cons.SYSTEM_TYPE_OS,
    'PhysicallyPartitioned': sys_cons.SYSTEM_TYPE_PHYSICALLY_PARTITIONED,
    'VirtuallyPartitioned': sys_cons.SYSTEM_TYPE_VIRTUALLY_PARTITIONED,
    'Composed': sys_cons.SYSTEM_TYPE_COMPOSED
}

SYSTEM_TYPE_VALUE_MAP_REV = (
    utils.revert_dictionary(SYSTEM_TYPE_VALUE_MAP))

SECURE_BOOT_STATE = {
    'Enabled': sys_cons.SECURE_BOOT_ENABLED,
    'Disabled': sys_cons.SECURE_BOOT_DISABLED,
}

SECURE_BOOT_STATE_REV = utils.revert_dictionary(SECURE_BOOT_STATE)

SECURE_BOOT_MODE = {
    'SetupMode': sys_cons.SECURE_BOOT_MODE_SETUP,
    'UserMode': sys_cons.SECURE_BOOT_MODE_USER,
    'AuditMode': sys_cons.SECURE_BOOT_MODE_AUDIT,
    'DeployedMode': sys_cons.SECURE_BOOT_MODE_DEPLOYED,
}

SECURE_BOOT_MODE_REV = utils.revert_dictionary(SECURE_BOOT_MODE)

SECURE_BOOT_RESET_KEYS = {
    'ResetAllKeysToDefault': sys_cons.SECURE_BOOT_RESET_KEYS_TO_DEFAULT,
    'DeleteAllKeys': sys_cons.SECURE_BOOT_RESET_KEYS_DELETE_ALL,
    'DeletePK': sys_cons.SECURE_BOOT_RESET_KEYS_DELETE_PK,
}

SECURE_BOOT_RESET_KEYS_REV = utils.revert_dictionary(SECURE_BOOT_RESET_KEYS)
