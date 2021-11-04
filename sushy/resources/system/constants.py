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

import enum

from sushy.resources import constants as res_cons

# Reset action constants

RESET_ON = res_cons.ResetType.ON
RESET_FORCE_OFF = res_cons.ResetType.FORCE_OFF
RESET_GRACEFUL_SHUTDOWN = res_cons.ResetType.GRACEFUL_SHUTDOWN
RESET_GRACEFUL_RESTART = res_cons.ResetType.GRACEFUL_RESTART
RESET_FORCE_RESTART = res_cons.ResetType.FORCE_RESTART
RESET_NMI = res_cons.ResetType.NMI
RESET_FORCE_ON = res_cons.ResetType.FORCE_ON
RESET_PUSH_POWER_BUTTON = res_cons.ResetType.PUSH_POWER_BUTTON

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


class BootSource(enum.Enum):
    """Boot source target constants"""

    NONE = 'None'
    """Boot from the normal boot device."""

    PXE = 'Pxe'
    """Boot from the Pre-Boot EXecution (PXE) environment."""

    FLOPPY = 'Floppy'
    """Boot from the floppy disk drive."""

    CD = 'Cd'
    """Boot from the CD or DVD."""

    USB = 'Usb'
    """Boot from a system BIOS-specified USB device."""

    HDD = 'Hdd'
    """Boot from a hard drive."""

    BIOS_SETUP = 'BiosSetup'
    """Boot to the BIOS setup utility."""

    UTILITIES = 'Utilities'
    """Boot to the manufacturer's utilities program or programs."""

    DIAGS = 'Diags'
    """Boot to the manufacturer's diagnostics program."""

    UEFI_SHELL = 'UefiShell'
    """Boot to the UEFI Shell."""

    UEFI_TARGET = 'UefiTarget'
    """Boot to the UEFI device specified in the UefiTargetBootSourceOverride
    property."""

    SD_CARD = 'SDCard'
    """Boot from an SD card."""

    UEFI_HTTP = 'UefiHttp'
    """Boot from a UEFI HTTP network location."""

    REMOTE_DRIVE = 'RemoteDrive'
    """Boot from a remote drive, such as an iSCSI target."""

    UEFI_BOOT_NEXT = 'UefiBootNext'
    """Boot to the UEFI device that the BootNext property specifies."""

    USB_CD = 'UsbCd'
    """Boot from a USB CD device as specified by the system BIOS.

    **This is NOT a standard value!**
    On SuperMicro X11 and X12 machines, virtual media is presented as an USB CD
    drive as opposed to a CD drive. Both are present in the list of boot
    devices, however only selecting UsbCd as the boot source results in a
    successful boot from vMedia. If CD is selected, boot fails even if vMedia
    is inserted."""


# Backward compatibility
BOOT_SOURCE_TARGET_NONE = BootSource.NONE
BOOT_SOURCE_TARGET_PXE = BootSource.PXE
BOOT_SOURCE_TARGET_FLOPPY = BootSource.FLOPPY
BOOT_SOURCE_TARGET_CD = BootSource.CD
BOOT_SOURCE_TARGET_USB = BootSource.USB
BOOT_SOURCE_TARGET_HDD = BootSource.HDD
BOOT_SOURCE_TARGET_BIOS_SETUP = BootSource.BIOS_SETUP
BOOT_SOURCE_TARGET_UTILITIES = BootSource.UTILITIES
BOOT_SOURCE_TARGET_DIAGS = BootSource.DIAGS
BOOT_SOURCE_TARGET_UEFI_SHELL = BootSource.UEFI_SHELL
BOOT_SOURCE_TARGET_UEFI_TARGET = BootSource.UEFI_TARGET
BOOT_SOURCE_TARGET_SD_CARD = BootSource.SD_CARD
BOOT_SOURCE_TARGET_UEFI_HTTP = BootSource.UEFI_HTTP
BOOT_SOURCE_TARGET_USB_CD = BootSource.USB_CD


class BootSourceOverrideMode(enum.Enum):
    """Boot source mode constants"""

    LEGACY = 'Legacy'
    """The system boots in non-UEFI boot mode to the boot source override
    target."""

    UEFI = 'UEFI'
    """The system boots in UEFI boot mode to the boot source override
    target."""


# Backward compatibility
BOOT_SOURCE_MODE_BIOS = BootSourceOverrideMode.LEGACY
BOOT_SOURCE_MODE_UEFI = BootSourceOverrideMode.UEFI


class BootSourceOverrideEnabled(enum.Enum):
    """Boot source enabled constants"""

    DISABLED = 'Disabled'
    """The system boots normally."""

    ONCE = 'Once'
    """On its next boot cycle, the system boots one time to the boot source
    override target.  Then, the BootSourceOverrideEnabled value is reset
    to `Disabled`."""

    CONTINUOUS = 'Continuous'
    """The system boots to the target specified in the
    BootSourceOverrideTarget property until this property is `Disabled`."""


# Backward compatibility
BOOT_SOURCE_ENABLED_DISABLED = BootSourceOverrideEnabled.DISABLED
BOOT_SOURCE_ENABLED_ONCE = BootSourceOverrideEnabled.ONCE
BOOT_SOURCE_ENABLED_CONTINUOUS = BootSourceOverrideEnabled.CONTINUOUS


class SystemType(enum.Enum):
    """System type constants"""

    PHYSICAL = 'Physical'
    """A computer system."""

    VIRTUAL = 'Virtual'
    """A virtual machine instance running on this system."""

    OS = 'OS'
    """An operating system instance."""

    PHYSICALLY_PARTITIONED = 'PhysicallyPartitioned'
    """A hardware-based partition of a computer system."""

    VIRTUALLY_PARTITIONED = 'VirtuallyPartitioned'
    """A virtual or software-based partition of a computer system."""

    COMPOSED = 'Composed'
    """A computer system constructed by binding resource blocks together."""

    DPU = 'DPU'
    """A computer system that performs the functions of a data processing
    unit, such as a SmartNIC."""


# Backward compatibility
SYSTEM_TYPE_PHYSICAL = SystemType.PHYSICAL
SYSTEM_TYPE_VIRTUAL = SystemType.VIRTUAL
SYSTEM_TYPE_OS = SystemType.OS
SYSTEM_TYPE_PHYSICALLY_PARTITIONED = SystemType.PHYSICALLY_PARTITIONED
SYSTEM_TYPE_VIRTUALLY_PARTITIONED = SystemType.VIRTUALLY_PARTITIONED
SYSTEM_TYPE_COMPOSED = SystemType.COMPOSED
SYSTEM_TYPE_DPU = SystemType.DPU


# Processor related constants
# Values comes from the Redfish Processor json-schema 1.3.0:
# http://redfish.dmtf.org/schemas/v1/Processor.v1_3_0.json

class ProcessorArchitecture(enum.Enum):
    """Processor Architecture constants"""

    X86 = 'x86'
    """x86 or x86-64."""

    IA_64 = 'IA-64'
    """Intel Itanium."""

    ARM = 'ARM'
    """ARM."""

    MIPS = 'MIPS'
    """MIPS."""

    POWER = 'Power'
    """Power."""

    OEM = 'OEM'
    """OEM-defined."""


# Backward compatibility
PROCESSOR_ARCH_x86 = ProcessorArchitecture.X86
PROCESSOR_ARCH_IA_64 = ProcessorArchitecture.IA_64
PROCESSOR_ARCH_ARM = ProcessorArchitecture.ARM
PROCESSOR_ARCH_MIPS = ProcessorArchitecture.MIPS
PROCESSOR_ARCH_OEM = ProcessorArchitecture.OEM


class ProcessorType(enum.Enum):
    """Processor type constants"""

    CPU = 'CPU'
    """A CPU."""

    GPU = 'GPU'
    """A GPU."""

    FPGA = 'FPGA'
    """An FPGA."""

    DSP = 'DSP'
    """A DSP."""

    ACCELERATOR = 'Accelerator'
    """An accelerator."""

    CORE = 'Core'
    """A core in a processor."""

    THREAD = 'Thread'
    """A thread in a processor."""

    OEM = 'OEM'
    """An OEM-defined processing unit."""


# Backward compatibility
PROCESSOR_TYPE_CPU = ProcessorType.CPU
PROCESSOR_TYPE_GPU = ProcessorType.GPU
PROCESSOR_TYPE_FPGA = ProcessorType.FPGA
PROCESSOR_TYPE_DSP = ProcessorType.DSP
PROCESSOR_TYPE_ACCELERATOR = ProcessorType.ACCELERATOR
PROCESSOR_TYPE_CORE = ProcessorType.CORE
PROCESSOR_TYPE_THREAD = ProcessorType.THREAD
PROCESSOR_TYPE_OEM = ProcessorType.OEM


class InstructionSet(enum.Enum):
    """Processor InstructionSet constants"""

    X86 = 'x86'
    """x86 32-bit."""

    X86_64 = 'x86-64'
    """x86 64-bit."""

    IA_64 = 'IA-64'
    """Intel IA-64."""

    ARM_A32 = 'ARM-A32'
    """ARM 32-bit."""

    ARM_A64 = 'ARM-A64'
    """ARM 64-bit."""

    MIPS32 = 'MIPS32'
    """MIPS 32-bit."""

    MIPS64 = 'MIPS64'
    """MIPS 64-bit."""

    POWER_ISA = 'PowerISA'
    """PowerISA-64 or PowerISA-32."""

    OEM = 'OEM'
    """OEM-defined."""


PROCESSOR_INSTRUCTIONSET_ARM_A32 = InstructionSet.ARM_A32
PROCESSOR_INSTRUCTIONSET_ARM_A64 = InstructionSet.ARM_A64
PROCESSOR_INSTRUCTIONSET_IA_64 = InstructionSet.IA_64
PROCESSOR_INSTRUCTIONSET_MIPS32 = InstructionSet.MIPS32
PROCESSOR_INSTRUCTIONSET_MIPS64 = InstructionSet.MIPS64
PROCESSOR_INSTRUCTIONSET_OEM = InstructionSet.OEM
PROCESSOR_INSTRUCTIONSET_x86 = InstructionSet.X86
PROCESSOR_INSTRUCTIONSET_x86_64 = InstructionSet.X86_64


# Secure boot constants from SecureBoot schema version 1.1.0
# https://redfish.dmtf.org/schemas/v1/SecureBoot.v1_1_0.json
# Some names were altered for clarity

class SecureBootCurrentBoot(enum.Enum):
    ENABLED = 'Enabled'
    """UEFI Secure Boot is currently enabled."""

    DISABLED = 'Disabled'
    """UEFI Secure Boot is currently disabled."""


# Backward compatibility
SECURE_BOOT_ENABLED = SecureBootCurrentBoot.ENABLED
SECURE_BOOT_DISABLED = SecureBootCurrentBoot.DISABLED


class SecureBootMode(enum.Enum):
    SETUP = 'SetupMode'
    """UEFI Secure Boot is currently in Setup Mode."""

    USER = 'UserMode'
    """UEFI Secure Boot is currently in User Mode."""

    AUDIT = 'AuditMode'
    """UEFI Secure Boot is currently in Audit Mode."""

    DEPLOYED = 'DeployedMode'
    """UEFI Secure Boot is currently in Deployed Mode."""


# Backward compatibility
SECURE_BOOT_MODE_SETUP = SecureBootMode.SETUP
SECURE_BOOT_MODE_USER = SecureBootMode.USER
SECURE_BOOT_MODE_AUDIT = SecureBootMode.AUDIT
SECURE_BOOT_MODE_DEPLOYED = SecureBootMode.DEPLOYED


class SecureBootResetKeysType(enum.Enum):
    RESET_ALL_KEYS_TO_DEFAULT = 'ResetAllKeysToDefault'
    """Reset the contents of all UEFI Secure Boot key databases, including
    the PK key database, to the default values."""

    DELETE_ALL_KEYS = 'DeleteAllKeys'
    """Delete the contents of all UEFI Secure Boot key databases, including
    the PK key database.  This puts the system in Setup Mode."""

    DELETE_PK = 'DeletePK'
    """Delete the contents of the PK UEFI Secure Boot database.  This puts
    the system in Setup Mode."""


# Internal constant based on
# https://redfish.dmtf.org/schemas/v1/SecureBootDatabase.v1_0_1.json
_SECURE_BOOT_DATABASE_RESET_KEYS = frozenset([
    SecureBootResetKeysType.RESET_ALL_KEYS_TO_DEFAULT,
    SecureBootResetKeysType.DELETE_ALL_KEYS,
])


# Backward compatibility
SECURE_BOOT_RESET_KEYS_TO_DEFAULT = \
    SecureBootResetKeysType.RESET_ALL_KEYS_TO_DEFAULT
SECURE_BOOT_RESET_KEYS_DELETE_ALL = SecureBootResetKeysType.DELETE_ALL_KEYS
SECURE_BOOT_RESET_KEYS_DELETE_PK = SecureBootResetKeysType.DELETE_PK


class SecureBootDatabaseId(enum.Enum):
    # This enumeration is hand-written based on the database schema
    # https://redfish.dmtf.org/schemas/v1/SecureBootDatabase.v1_0_1.json
    # and the UEFI specification.

    PLATFORM_KEY = "PK"
    KEY_EXCHANGE_KEYS = "KEK"
    ALLOWED_KEYS_DATABASE = "db"
    DENIED_KEYS_DATABASE = "dbx"
    RECOVERY_KEYS_DATABASE = "dbr"
    TIMESTAMP_DATABASE = "dbt"

    DEFAULT_PLATFORM_KEY = "PKDefault"
    DEFAULT_KEY_EXCHANGE_KEYS = "KEKDefault"
    DEFAULT_ALLOWED_KEYS_DATABASE = "dbDefault"
    DEFAULT_DENIED_KEYS_DATABASE = "dbxDefault"
    DEFAULT_RECOVERY_KEYS_DATABASE = "dbrDefault"
    DEFAULT_TIMESTAMP_DATABASE = "dbtDefault"


# Backward compatibility
SECURE_BOOT_PLATFORM_KEY = SecureBootDatabaseId.PLATFORM_KEY
SECURE_BOOT_KEY_EXCHANGE_KEYS = SecureBootDatabaseId.KEY_EXCHANGE_KEYS
SECURE_BOOT_ALLOWED_KEYS_DATABASE = SecureBootDatabaseId.ALLOWED_KEYS_DATABASE
SECURE_BOOT_DENIED_KEYS_DATABASE = SecureBootDatabaseId.DENIED_KEYS_DATABASE
SECURE_BOOT_RECOVERY_KEYS_DATABASE = \
    SecureBootDatabaseId.RECOVERY_KEYS_DATABASE
SECURE_BOOT_TIMESTAMP_DATABASE = SecureBootDatabaseId.TIMESTAMP_DATABASE

SECURE_BOOT_DEFAULT_PLATFORM_KEY = SecureBootDatabaseId.DEFAULT_PLATFORM_KEY
SECURE_BOOT_DEFAULT_KEY_EXCHANGE_KEYS = \
    SecureBootDatabaseId.DEFAULT_KEY_EXCHANGE_KEYS
SECURE_BOOT_DEFAULT_ALLOWED_KEYS_DATABASE = \
    SecureBootDatabaseId.DEFAULT_ALLOWED_KEYS_DATABASE
SECURE_BOOT_DEFAULT_DENIED_KEYS_DATABASE = \
    SecureBootDatabaseId.DEFAULT_DENIED_KEYS_DATABASE
SECURE_BOOT_DEFAULT_RECOVERY_KEYS_DATABASE = \
    SecureBootDatabaseId.DEFAULT_RECOVERY_KEYS_DATABASE
SECURE_BOOT_DEFAULT_TIMESTAMP_DATABASE = \
    SecureBootDatabaseId.DEFAULT_TIMESTAMP_DATABASE
