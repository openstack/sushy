# Copyright (c) 2020-2021 Dell Inc. or its subsidiaries.
#
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

import enum


class ExportTarget(enum.Enum):
    """Export system config action constants"""

    ALL = 'ALL'
    """Export entire system configuration"""

    BIOS = 'BIOS'
    """Export BIOS related configuration"""

    IDRAC = 'IDRAC'
    """Export iDRAC related configuration"""

    NIC = 'NIC'
    """Export NIC related configuration"""

    RAID = 'RAID'
    """Export RAID related configuration"""


# Backward compatibility
EXPORT_TARGET_ALL = ExportTarget.ALL
EXPORT_TARGET_BIOS = ExportTarget.BIOS
EXPORT_TARGET_IDRAC = ExportTarget.IDRAC
EXPORT_TARGET_NIC = ExportTarget.NIC
EXPORT_TARGET_RAID = ExportTarget.RAID


class ResetType(enum.Enum):
    """iDRAC Reset reset type constants"""

    GRACEFUL = 'Graceful'
    """Perform a graceful shutdown followed by a restart of the system"""

    FORCE = 'Force'
    """Perform an immediate (non-graceful) shutdown, followed by a restart"""


# Backward compatibility
RESET_IDRAC_GRACEFUL_RESTART = ResetType.GRACEFUL
RESET_IDRAC_FORCE_RESTART = ResetType.FORCE


class ShutdownType(enum.Enum):
    """ImportSystemConfiguration ShutdownType values"""

    GRACEFUL = 'Graceful'
    """Graceful shutdown for Import System Configuration

    Will wait for the host up to 5 minutes to shut down before timing out. The
    operating system can potentially deny or ignore the graceful shutdown
    request.
    """

    FORCED = 'Forced'
    """Forced shutdown for Import System Configuration

    The host server will be powered off immediately. Should be used when it is
    safe to power down the host.
    """

    NO_REBOOT = 'NoReboot'
    """No reboot for Import System Configuration

    No shutdown performed. Explicit reboot is necessary to apply changes.
    """


# Backward compatibility
IMPORT_SHUTDOWN_GRACEFUL = ShutdownType.GRACEFUL
IMPORT_SHUTDOWN_FORCED = ShutdownType.FORCED
IMPORT_SHUTDOWN_NO_REBOOT = ShutdownType.NO_REBOOT


class ExportUse(enum.Enum):
    """ExportUse in ExportSystemConfiguration"""

    DEFAULT = 'Default'
    """Default export type

    Leaves some attributes commented out and requires user to enable them
    before they can be applied during import.
    """

    CLONE = 'Clone'
    """Clone export type suitable for cloning a 'golden' configuration.

    Compared to Default export type, more attributes are enabled and
    storage settings adjusted to aid in cloning process.
    """

    REPLACE = 'Replace'
    """Replace export type suited for replacing complete configuration.

    Compared to Clone export type, most attributes are enabled and storage
    settings adjusted to aid in the replace process.
    """


# Backward compatibility
EXPORT_USE_DEFAULT = ExportUse.DEFAULT
EXPORT_USE_CLONE = ExportUse.CLONE
EXPORT_USE_REPLACE = ExportUse.REPLACE


class IncludeInExport(enum.Enum):
    """IncludeInExport in ExportSystemConfiguration"""

    DEFAULT = 'Default'
    """Default for what to include in export.

    Does not include read-only attributes, and depending on Export Use,
    passwords are marked as ****** (for Default) or are set to default password
    values (for Clone and Replace).
    """

    READ_ONLY = 'IncludeReadOnly'
    """Includes read-only attributes.

    In addition to values included by Default option, this also includes
    read-only attributes that cannot be changed via Import and are provided for
    informational purposes only.
    """

    PASSWORD_HASHES = 'IncludePasswordHashValues'  # noqa:S105
    """Include password hashes.

    When using Clone or Replace, include password hashes, instead of default
    password. Can be used to replicate passwords across systems.
    """

    READ_ONLY_PASSWORD_HASHES =\
        'IncludeReadOnly,IncludePasswordHashValues'  # noqa:S105
    """Includes both read-only attributes and password hashes.

    INCLUDE_EXPORT_READ_ONLY and INCLUDE_EXPORT_PASSWORD_HASHES combined
    """


# Backward compatibility
INCLUDE_EXPORT_DEFAULT = IncludeInExport.DEFAULT
INCLUDE_EXPORT_READ_ONLY = IncludeInExport.READ_ONLY
INCLUDE_EXPORT_PASSWORD_HASHES = IncludeInExport.PASSWORD_HASHES
INCLUDE_EXPORT_READ_ONLY_PASSWORD_HASHES =\
    IncludeInExport.READ_ONLY_PASSWORD_HASHES
