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

# Values comes from the Redfish System json-schema 1.0.0:
# http://redfish.dmtf.org/schemas/v1/ComputerSystem.v1_0_0.json#/definitions/ComputerSystem  # noqa

# Reset action constants

RESET_ON = 'on'
RESET_FORCE_OFF = 'force off'
RESET_GRACEFUL_SHUTDOWN = 'graceful shutdown'
RESET_GRACEFUL_RESTART = 'graceful restart'
RESET_FORCE_RESTART = 'force restart'
RESET_NMI = 'nmi'
RESET_FORCE_ON = 'force on'
RESET_PUSH_POWER_BUTTON = 'push power button'

# System' PowerState constants

SYSTEM_POWER_STATE_ON = 'on'
"""The system is powered on"""

SYSTEM_POWER_STATE_OFF = 'off'
"""The system is powered off, although some components may continue to
   have AUX power such as management controller"""

SYSTEM_POWER_STATE_POWERING_ON = 'powering on'
"""A temporary state between Off and On. This temporary state can
   be very short"""

SYSTEM_POWER_STATE_POWERING_OFF = 'powering off'
"""A temporary state between On and Off. The power off action can take
   time while the OS is in the shutdown process"""

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
# Values comes from the Redfish Processor json-schema 1.0.0:
# http://redfish.dmtf.org/schemas/v1/Processor.v1_0_0.json

# Processor Architecture constants

PROCESSOR_ARCH_x86 = 'x86 or x86-64'
PROCESSOR_ARCH_IA_64 = 'Intel Itanium'
PROCESSOR_ARCH_ARM = 'ARM'
PROCESSOR_ARCH_MIPS = 'MIPS'
PROCESSOR_ARCH_OEM = 'OEM-defined'
