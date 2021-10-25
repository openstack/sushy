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

# Values comes from the Redfish System json-schema:
# http://redfish.dmtf.org/schemas/v1/Resource.json and
# https://redfish.dmtf.org/schemas/v1/Settings.v1_3_3.json and
# https://redfish.dmtf.org/schemas/v1/Protocol.json

import enum

from sushy.resources.registry import constants as reg_cons
from sushy.resources.taskservice import constants as ts_cons


class Health(enum.Enum):
    """Health related constants."""
    OK = 'OK'
    """Normal."""

    WARNING = 'Warning'
    """A condition requires attention."""

    CRITICAL = 'Critical'
    """A critical condition requires immediate attention."""


# Backward compatibility
HEALTH_OK = Health.OK
HEALTH_WARNING = Health.WARNING
HEALTH_CRITICAL = Health.CRITICAL


class State(enum.Enum):
    """State related constants."""
    ENABLED = 'Enabled'
    """This function or resource is enabled."""

    DISABLED = 'Disabled'
    """This function or resource is disabled."""

    STANDBY_OFFLINE = 'StandbyOffline'
    """This function or resource is enabled but awaits an external action to
    activate it."""

    STANDBY_SPARE = 'StandbySpare'
    """This function or resource is part of a redundancy set and awaits a
    failover or other external action to activate it."""

    IN_TEST = 'InTest'
    """This function or resource is undergoing testing, or is in the process
    of capturing information for debugging."""

    STARTING = 'Starting'
    """This function or resource is starting."""

    ABSENT = 'Absent'
    """This function or resource is either not present or detected."""

    UNAVAILABLE_OFFLINE = 'UnavailableOffline'
    """This function or resource is present but cannot be used."""

    DEFERRING = 'Deferring'
    """The element does not process any commands but queues new requests."""

    QUIESCED = 'Quiesced'
    """The element is enabled but only processes a restricted set of
    commands."""

    UPDATING = 'Updating'
    """The element is updating and might be unavailable or degraded."""

    QUALIFIED = 'Qualified'
    """The element quality is within the acceptable range of operation."""


# Backward compatibility
STATE_ENABLED = State.ENABLED
STATE_DISABLED = State.DISABLED
STATE_ABSENT = State.ABSENT
STATE_STANDBYOFFLINE = State.STANDBY_OFFLINE
STATE_STANDBYSPARE = State.STANDBY_SPARE
STATE_INTEST = State.IN_TEST
STATE_STARTING = State.STARTING
STATE_UNAVAILABLEOFFLINE = State.UNAVAILABLE_OFFLINE
STATE_DEFERRING = State.DEFERRING
STATE_QUIESCED = State.QUIESCED
STATE_UPDATING = State.UPDATING


# Backward compatibility, the type moved to taskservice.constants
TASK_STATE_NEW = ts_cons.TaskState.NEW
TASK_STATE_STARTING = ts_cons.TaskState.STARTING
TASK_STATE_RUNNING = ts_cons.TaskState.RUNNING
TASK_STATE_SUSPENDED = ts_cons.TaskState.SUSPENDED
TASK_STATE_INTERRUPTED = ts_cons.TaskState.INTERRUPTED
TASK_STATE_PENDING = ts_cons.TaskState.PENDING
TASK_STATE_STOPPING = ts_cons.TaskState.STOPPING
TASK_STATE_COMPLETED = ts_cons.TaskState.COMPLETED
TASK_STATE_KILLED = ts_cons.TaskState.KILLED
TASK_STATE_EXCEPTION = ts_cons.TaskState.EXCEPTION
TASK_STATE_SERVICE = ts_cons.TaskState.SERVICE
TASK_STATE_CANCELLING = ts_cons.TaskState.CANCELLING
TASK_STATE_CANCELLED = ts_cons.TaskState.CANCELLED


# Backward compatibility, the type moved to registry.constants
PARAMTYPE_STRING = reg_cons.MessageParamType.STRING
PARAMTYPE_NUMBER = reg_cons.MessageParamType.NUMBER


# Backward compatibility (Severity is an alias of Health after 1.1.0)
Severity = Health
SEVERITY_OK = Severity.OK
SEVERITY_WARNING = Severity.WARNING
SEVERITY_CRITICAL = Severity.CRITICAL


class IndicatorLED(enum.Enum):
    """Indicator LED Constants"""

    LIT = 'Lit'
    """The Indicator LED is lit"""

    BLINKING = 'Blinking'
    """The Indicator LED is blinking"""

    OFF = 'Off'
    """The Indicator LED is off"""

    UNKNOWN = 'Unknown'
    """The state of the Indicator LED cannot be determine"""


# Backward compatibility
INDICATOR_LED_LIT = IndicatorLED.LIT
INDICATOR_LED_BLINKING = IndicatorLED.BLINKING
INDICATOR_LED_OFF = IndicatorLED.OFF
INDICATOR_LED_UNKNOWN = IndicatorLED.UNKNOWN


class PowerState(enum.Enum):
    """System PowerState constants"""

    ON = 'On'
    """The resource is powered on"""

    OFF = 'Off'
    """The resource is powered off, although some components may continue to
    have AUX power such as management controller"""

    POWERING_ON = 'PoweringOn'
    """A temporary state between Off and On. This temporary state can
    be very short"""

    POWERING_OFF = 'PoweringOff'
    """A temporary state between On and Off. The power off action can take
    time while the OS is in the shutdown process"""

    PAUSED = 'Paused'
    """The resource is paused."""


# Backward compatibility
POWER_STATE_ON = PowerState.ON
POWER_STATE_OFF = PowerState.OFF
POWER_STATE_POWERING_ON = PowerState.POWERING_ON
POWER_STATE_POWERING_OFF = PowerState.POWERING_OFF


class ResetType(enum.Enum):
    """Reset action constants"""
    ON = 'On'
    """Turn on the unit."""

    FORCE_OFF = 'ForceOff'
    """Turn off the unit immediately (non-graceful shutdown)."""

    GRACEFUL_SHUTDOWN = 'GracefulShutdown'
    """Shut down gracefully and power off."""

    GRACEFUL_RESTART = 'GracefulRestart'
    """Shut down gracefully and restart the system."""

    FORCE_RESTART = 'ForceRestart'
    """Shut down immediately and non-gracefully and restart the system."""

    NMI = 'Nmi'
    """Generate a diagnostic interrupt, which is usually an NMI on x86
    systems, to stop normal operations, complete diagnostic actions, and,
    typically, halt the system."""

    FORCE_ON = 'ForceOn'
    """Turn on the unit immediately."""

    PUSH_POWER_BUTTON = 'PushPowerButton'
    """Simulate the pressing of the physical power button on this unit."""

    POWER_CYCLE = 'PowerCycle'
    """Power cycle the unit.  Behaves like a full power removal, followed by
    a power restore to the resource."""

    SUSPEND = 'Suspend'
    """Write the state of the unit to disk before powering off.  This allows
    for the state to be restored when powered back on."""

    PAUSE = 'Pause'
    """Pause execution on the unit but do not remove power.  This is
    typically a feature of virtual machine hypervisors."""

    RESUME = 'Resume'
    """Resume execution on the paused unit.  This is typically a feature of
    virtual machine hypervisors."""


# Backward compatibility
RESET_TYPE_ON = ResetType.ON
RESET_TYPE_FORCE_OFF = ResetType.FORCE_OFF
RESET_TYPE_GRACEFUL_SHUTDOWN = ResetType.GRACEFUL_SHUTDOWN
RESET_TYPE_GRACEFUL_RESTART = ResetType.GRACEFUL_RESTART
RESET_TYPE_FORCE_RESTART = ResetType.FORCE_RESTART
RESET_TYPE_NMI = ResetType.NMI
RESET_TYPE_FORCE_ON = ResetType.FORCE_ON
RESET_TYPE_PUSH_POWER_BUTTON = ResetType.PUSH_POWER_BUTTON
RESET_TYPE_POWER_CYCLE = ResetType.POWER_CYCLE


class Protocol(enum.Enum):
    """Protocol type constants"""

    PCIe = 'PCIe'
    """PCI Express."""

    AHCI = 'AHCI'
    """Advanced Host Controller Interface (AHCI)."""

    UHCI = 'UHCI'
    """Universal Host Controller Interface (UHCI)."""

    SAS = 'SAS'
    """Serial Attached SCSI."""

    SATA = 'SATA'
    """Serial AT Attachment."""

    USB = 'USB'
    """Universal Serial Bus (USB)."""

    NVMe = 'NVMe'
    """Non-Volatile Memory Express (NVMe)."""

    FC = 'FC'
    """Fibre Channel."""

    iSCSI = 'iSCSI'
    """Internet SCSI."""

    FCoE = 'FCoE'
    """Fibre Channel over Ethernet (FCoE)."""

    FCP = 'FCP'
    """Fibre Channel Protocol for SCSI."""

    FICON = 'FICON'
    """FIbre CONnection (FICON)."""

    NVMe_OVER_FABRICS = 'NVMeOverFabrics'
    """NVMe over Fabrics."""

    SMB = 'SMB'
    """Server Message Block (SMB).  Also known as the Common Internet File
    System (CIFS)."""

    NFSv3 = 'NFSv3'
    """Network File System (NFS) version 3."""

    NFSv4 = 'NFSv4'
    """Network File System (NFS) version 4."""

    HTTP = 'HTTP'
    """Hypertext Transport Protocol (HTTP)."""

    HTTPS = 'HTTPS'
    """Hypertext Transfer Protocol Secure (HTTPS)."""

    FTP = 'FTP'
    """File Transfer Protocol (FTP)."""

    SFTP = 'SFTP'
    """SSH File Transfer Protocol (SFTP)."""

    iWARP = 'iWARP'
    """Internet Wide Area RDMA Protocol (iWARP)."""

    RoCE = 'RoCE'
    """RDMA over Converged Ethernet Protocol."""

    RoCEv2 = 'RoCEv2'
    """RDMA over Converged Ethernet Protocol Version 2."""

    I2C = 'I2C'
    """Inter-Integrated Circuit Bus."""

    TCP = 'TCP'
    """Transmission Control Protocol (TCP)."""

    UDP = 'UDP'
    """User Datagram Protocol (UDP)."""

    TFTP = 'TFTP'
    """Trivial File Transfer Protocol (TFTP)."""

    GEN_Z = 'GenZ'
    """GenZ."""

    MULTI_PROTOCOL = 'MultiProtocol'
    """Multiple Protocols."""

    INFINI_BAND = 'InfiniBand'
    """InfiniBand."""

    ETHERNET = 'Ethernet'
    """Ethernet."""

    NVLINK = 'NVLink'
    """NVLink."""

    OEM = 'OEM'
    """OEM-specific."""

    DISPLAY_PORT = 'DisplayPort'
    """DisplayPort."""

    HDMI = 'HDMI'
    """HDMI."""

    VGA = 'VGA'
    """VGA."""

    DVI = 'DVI'
    """DVI."""


# Backward compatibility

PROTOCOL_TYPE_AHCI = Protocol.AHCI
PROTOCOL_TYPE_FC = Protocol.FC
PROTOCOL_TYPE_FCP = Protocol.FCP
PROTOCOL_TYPE_FCoE = Protocol.FCoE
PROTOCOL_TYPE_FICON = Protocol.FICON
PROTOCOL_TYPE_FTP = Protocol.FTP
PROTOCOL_TYPE_HTTP = Protocol.HTTP
PROTOCOL_TYPE_HTTPS = Protocol.HTTPS
PROTOCOL_TYPE_I2C = Protocol.I2C
PROTOCOL_TYPE_NFSv3 = Protocol.NFSv3
PROTOCOL_TYPE_NFSv4 = Protocol.NFSv4
PROTOCOL_TYPE_NVMe = Protocol.NVMe
PROTOCOL_TYPE_NVMeOverFabrics = Protocol.NVMe_OVER_FABRICS
PROTOCOL_TYPE_OEM = Protocol.OEM
PROTOCOL_TYPE_PCIe = Protocol.PCIe
PROTOCOL_TYPE_RoCE = Protocol.RoCE
PROTOCOL_TYPE_RoCEv2 = Protocol.RoCEv2
PROTOCOL_TYPE_SAS = Protocol.SAS
PROTOCOL_TYPE_SATA = Protocol.SATA
PROTOCOL_TYPE_SFTP = Protocol.SFTP
PROTOCOL_TYPE_SMB = Protocol.SMB
PROTOCOL_TYPE_TFTP = Protocol.TFTP
PROTOCOL_TYPE_UHCI = Protocol.UHCI
PROTOCOL_TYPE_USB = Protocol.USB
PROTOCOL_TYPE_iSCSI = Protocol.iSCSI
PROTOCOL_TYPE_iWARP = Protocol.iWARP

# These values are not in the Protocol enum, using them is probably wrong!
PROTOCOL_TYPE_CIFS = Protocol.SMB
PROTOCOL_TYPE_NFS = Protocol.NFSv4
PROTOCOL_TYPE_SCP = Protocol.SFTP


class DurableNameFormat(enum.Enum):
    """Durable name format constants"""
    NAA = 'NAA'
    """The Name Address Authority (NAA) format."""

    iQN = 'iQN'
    """The iSCSI Qualified Name (iQN)."""

    FC_WWN = 'FC_WWN'
    """The Fibre Channel (FC) World Wide Name (WWN)."""

    UUID = 'UUID'
    """The Universally Unique Identifier (UUID)."""

    EUI = 'EUI'
    """The IEEE-defined 64-bit Extended Unique Identifier (EUI)."""

    NQN = 'NQN'
    """The NVMe Qualified Name (NQN)."""

    NSID = 'NSID'
    """The NVM Namespace Identifier (NSID)."""

    NGUID = 'NGUID'
    """The Namespace Globally Unique Identifier (NGUID)."""


# Backward compatibility
DURABLE_NAME_FORMAT_NAA = DurableNameFormat.NAA
DURABLE_NAME_FORMAT_iQN = DurableNameFormat.iQN
DURABLE_NAME_FORMAT_FC_WWN = DurableNameFormat.FC_WWN
DURABLE_NAME_FORMAT_UUID = DurableNameFormat.UUID
DURABLE_NAME_FORMAT_EUI = DurableNameFormat.EUI
DURABLE_NAME_FORMAT_NQN = DurableNameFormat.NQN
DURABLE_NAME_FORMAT_NSID = DurableNameFormat.NSID


class ApplyTime(enum.Enum):
    """Apply time constants"""

    IMMEDIATE = 'Immediate'
    """Apply immediately."""

    ON_RESET = 'OnReset'
    """Apply on a reset."""

    AT_MAINTENANCE_WINDOW_START = 'AtMaintenanceWindowStart'
    """Apply during a maintenance window as specified by an administrator."""

    IN_MAINTENANCE_WINDOW_ON_RESET = 'InMaintenanceWindowOnReset'
    """Apply after a reset but within maintenance window as specified by an
    administrator."""


# Backward compatibility
APPLY_TIME_IMMEDIATE = ApplyTime.IMMEDIATE
APPLY_TIME_ON_RESET = ApplyTime.ON_RESET
APPLY_TIME_MAINT_START = ApplyTime.AT_MAINTENANCE_WINDOW_START
APPLY_TIME_MAINT_RESET = ApplyTime.IN_MAINTENANCE_WINDOW_ON_RESET
