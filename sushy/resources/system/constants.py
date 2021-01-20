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

# Values come from the Redfish System json-schema 1.0.0:
# http://redfish.dmtf.org/schemas/v1/ComputerSystem.v1_0_0.json#/definitions/ComputerSystem  # noqa

from sushy.resources import constants as res_cons

# Reset action constants

RESET_ON = res_cons.RESET_TYPE_ON
RESET_FORCE_OFF = res_cons.RESET_TYPE_FORCE_OFF
RESET_GRACEFUL_SHUTDOWN = res_cons.RESET_TYPE_GRACEFUL_SHUTDOWN
RESET_GRACEFUL_RESTART = res_cons.RESET_TYPE_GRACEFUL_RESTART
RESET_FORCE_RESTART = res_cons.RESET_TYPE_FORCE_RESTART
RESET_NMI = res_cons.RESET_TYPE_NMI
RESET_FORCE_ON = res_cons.RESET_TYPE_FORCE_ON
RESET_PUSH_POWER_BUTTON = res_cons.RESET_TYPE_PUSH_POWER_BUTTON

# System' PowerState constants

SYSTEM_POWER_STATE_ON = res_cons.POWER_STATE_ON
"""The system is powered on"""

SYSTEM_POWER_STATE_OFF = res_cons.POWER_STATE_OFF
"""The system is powered off, although some components may continue to
   have AUX power such as management controller"""

SYSTEM_POWER_STATE_POWERING_ON = res_cons.POWER_STATE_POWERING_ON
"""A temporary state between Off and On. This temporary state can
   be very short"""

SYSTEM_POWER_STATE_POWERING_OFF = res_cons.POWER_STATE_POWERING_OFF
"""A temporary state between On and Off. The power off action can take
   time while the OS is in the shutdown process"""

# Indicator LED Constants

SYSTEM_INDICATOR_LED_LIT = res_cons.INDICATOR_LED_LIT
"""The Indicator LED is lit

Deprecated: Use `sushy.resources.constants.INDICATOR_LED_LIT`.
"""

SYSTEM_INDICATOR_LED_BLINKING = res_cons.INDICATOR_LED_BLINKING
"""The Indicator LED is blinking

Deprecated: Use `sushy.resources.constants.INDICATOR_LED_BLINKING`.
"""

SYSTEM_INDICATOR_LED_OFF = res_cons.INDICATOR_LED_OFF
"""The Indicator LED is off

Deprecated: Use `sushy.resources.constants.INDICATOR_LED_OFF`.
"""

SYSTEM_INDICATOR_LED_UNKNOWN = res_cons.INDICATOR_LED_UNKNOWN
"""The state of the Indicator LED cannot be determine

Deprecated: Use `sushy.resources.constants.INDICATOR_LED_UNKNOWN`.
"""

# Boot source target constants

BOOT_SOURCE_TARGET_NONE = 'none'
"""Boot from the normal boot device"""

BOOT_SOURCE_TARGET_PXE = 'pxe'
"""Boot from the Pre-Boot EXecution (PXE) environment"""

BOOT_SOURCE_TARGET_FLOPPY = 'floppy'
"""Boot from the floppy disk drive"""

BOOT_SOURCE_TARGET_CD = 'cd'
"""Boot from the CD/DVD disc"""

BOOT_SOURCE_TARGET_USB = 'usb'
"""Boot from a USB device as specified by the system BIOS"""

BOOT_SOURCE_TARGET_HDD = 'hdd'
"""Boot from a hard drive"""

BOOT_SOURCE_TARGET_BIOS_SETUP = 'bios setup'
"""Boot to the BIOS Setup Utility"""

BOOT_SOURCE_TARGET_UTILITIES = 'utilities'
"""Boot the manufacturer's Utilities program(s)"""

BOOT_SOURCE_TARGET_DIAGS = 'diags'
"""Boot the manufacturer's Diagnostics program"""

BOOT_SOURCE_TARGET_SD_CARD = 'sd card'
"""Boot from an SD Card"""

BOOT_SOURCE_TARGET_UEFI_TARGET = 'uefi target'
"""Boot to the UEFI Device specified in the
   UefiTargetBootSourceOverride property"""

BOOT_SOURCE_TARGET_UEFI_SHELL = 'uefi shell'
"""Boot to the UEFI Shell"""

BOOT_SOURCE_TARGET_UEFI_HTTP = 'uefi http'
"""Boot from a UEFI HTTP network location"""

# Boot source mode constants

BOOT_SOURCE_MODE_BIOS = 'bios'
BOOT_SOURCE_MODE_UEFI = 'uefi'

# Boot source enabled constants

BOOT_SOURCE_ENABLED_ONCE = 'once'
BOOT_SOURCE_ENABLED_CONTINUOUS = 'continuous'
BOOT_SOURCE_ENABLED_DISABLED = 'disabled'

# Processor related constants
# Values comes from the Redfish Processor json-schema 1.3.0:
# http://redfish.dmtf.org/schemas/v1/Processor.v1_3_0.json

# Processor Architecture constants

PROCESSOR_ARCH_x86 = 'x86 or x86-64'
PROCESSOR_ARCH_IA_64 = 'Intel Itanium'
PROCESSOR_ARCH_ARM = 'ARM'
PROCESSOR_ARCH_MIPS = 'MIPS'
PROCESSOR_ARCH_OEM = 'OEM-defined'

# Processor type constants

PROCESSOR_TYPE_ACCELERATOR = 'An Accelerator'
PROCESSOR_TYPE_CPU = 'A Central Processing Unit'
PROCESSOR_TYPE_CORE = 'A Core in a Processor'
PROCESSOR_TYPE_DSP = 'A Digital Signal Processor'
PROCESSOR_TYPE_FPGA = 'A Field Programmable Gate Array'
PROCESSOR_TYPE_GPU = 'A Graphics Processing Unit'
PROCESSOR_TYPE_OEM = 'An OEM-defined Processing Unit'
PROCESSOR_TYPE_THREAD = 'A Thread in a Processor'

# Processor InstructionSet constants

PROCESSOR_INSTRUCTIONSET_ARM_A32 = 'ARM 32-bit'
PROCESSOR_INSTRUCTIONSET_ARM_A64 = 'ARM 64-bit'
PROCESSOR_INSTRUCTIONSET_IA_64 = 'Intel IA-64'
PROCESSOR_INSTRUCTIONSET_MIPS32 = 'MIPS 32-bit'
PROCESSOR_INSTRUCTIONSET_MIPS64 = 'MIPS 64-bit'
PROCESSOR_INSTRUCTIONSET_OEM = 'OEM-defined'
PROCESSOR_INSTRUCTIONSET_x86 = 'x86 32-bit'
PROCESSOR_INSTRUCTIONSET_x86_64 = 'x86 64-bit'

# System type constants

SYSTEM_TYPE_PHYSICAL = "Physical"
"""A physical computer system"""
SYSTEM_TYPE_VIRTUAL = "Virtual"
"""A virtual machine instance"""
SYSTEM_TYPE_OS = "OS"
"""An operating system instance"""
SYSTEM_TYPE_PHYSICALLY_PARTITIONED = "PhysicallyPartitioned"
"""A hardware-based partition of a computer system"""
SYSTEM_TYPE_VIRTUALLY_PARTITIONED = "VirtuallyPartitioned"
"""A virtual or software-based partition of a computer system"""
SYSTEM_TYPE_COMPOSED = "Composed"
"""A computer system created by binding resource blocks together"""

# Secure boot constants

SECURE_BOOT_ENABLED = "Enabled"
"""UEFI secure boot is enabled."""

SECURE_BOOT_DISABLED = "Disabled"
"""UEFI secure boot is disabled."""

SECURE_BOOT_MODE_SETUP = "SetupMode"
SECURE_BOOT_MODE_USER = "UserMode"
SECURE_BOOT_MODE_AUDIT = "AuditMode"
SECURE_BOOT_MODE_DEPLOYED = "DeployedMode"

SECURE_BOOT_RESET_KEYS_TO_DEFAULT = "ResetAllKeysToDefault"
SECURE_BOOT_RESET_KEYS_DELETE_ALL = "DeleteAllKeys"
SECURE_BOOT_RESET_KEYS_DELETE_PK = "DeletePK"
