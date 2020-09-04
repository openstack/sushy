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
# http://redfish.dmtf.org/schemas/v1/Resource.json or
# https://redfish.dmtf.org/schemas/v1/MessageRegistry.v1_1_1.json

# Health related constants.
HEALTH_OK = 'ok'
HEALTH_WARNING = 'warning'
HEALTH_CRITICAL = 'critical'

# State related constants.
STATE_ENABLED = 'enabled'
STATE_DISABLED = 'disabled'
STATE_STANDBYOFFLINE = 'standby offline'
STATE_STANDBYSPARE = 'standby spare'
STATE_INTEST = 'in test'
STATE_STARTING = 'starting'
STATE_ABSENT = 'absent'
STATE_UNAVAILABLEOFFLINE = 'unavailable offline'
STATE_DEFERRING = 'deferring'
STATE_QUIESCED = 'quiesced'
STATE_UPDATING = 'updating'

# Task state related constants
TASK_STATE_NEW = 'new'
TASK_STATE_STARTING = 'starting'
TASK_STATE_RUNNING = 'running'
TASK_STATE_SUSPENDED = 'suspended'
TASK_STATE_INTERRUPTED = 'interrupted'
TASK_STATE_PENDING = 'pending'
TASK_STATE_STOPPING = 'stopping'
TASK_STATE_COMPLETED = 'completed'
TASK_STATE_KILLED = 'killed'
TASK_STATE_EXCEPTION = 'exception'
TASK_STATE_SERVICE = 'service'
TASK_STATE_CANCELLING = 'cancelling'
TASK_STATE_CANCELLED = 'cancelled'

# Message Registry message parameter type related constants.
PARAMTYPE_STRING = 'string'
PARAMTYPE_NUMBER = 'number'

# Severity related constants
SEVERITY_OK = 'ok'
SEVERITY_WARNING = 'warning'
SEVERITY_CRITICAL = 'critical'

# Indicator LED Constants

INDICATOR_LED_LIT = 'indicator led lit'
"""The Indicator LED is lit"""

INDICATOR_LED_BLINKING = 'indicator led blinking'
"""The Indicator LED is blinking"""

INDICATOR_LED_OFF = 'indicator led off'
"""The Indicator LED is off"""

INDICATOR_LED_UNKNOWN = 'indicator led unknown'
"""The state of the Indicator LED cannot be determine"""

# System' PowerState constants

POWER_STATE_ON = 'on'
"""The resource is powered on"""

POWER_STATE_OFF = 'off'
"""The resource is powered off, although some components may continue to
   have AUX power such as management controller"""

POWER_STATE_POWERING_ON = 'powering on'
"""A temporary state between Off and On. This temporary state can
   be very short"""

POWER_STATE_POWERING_OFF = 'powering off'
"""A temporary state between On and Off. The power off action can take
   time while the OS is in the shutdown process"""

# Reset action constants

RESET_TYPE_ON = 'on'
"""Turn the unit on"""

RESET_TYPE_FORCE_ON = 'force on'
"""Turn the unit on immediately"""

RESET_TYPE_FORCE_OFF = 'force off'
"""Turn the unit off immediately (non-graceful shutdown)"""

RESET_TYPE_GRACEFUL_SHUTDOWN = 'graceful shutdown'
"""Perform a graceful shutdown and power off"""

RESET_TYPE_GRACEFUL_RESTART = 'graceful restart'
"""Perform a graceful shutdown followed by a restart of the system"""

RESET_TYPE_FORCE_RESTART = 'force restart'
"""Perform an immediate (non-graceful) shutdown, followed by a restart"""

RESET_TYPE_NMI = 'nmi'
"""Generate a Diagnostic Interrupt (usually an NMI on x86 systems) to cease
normal operations, perform diagnostic actions and typically halt the system"""

RESET_TYPE_PUSH_POWER_BUTTON = 'push power button'
"""Simulate the pressing of the physical power button on this unit"""

RESET_TYPE_POWER_CYCLE = 'power cycle'
"""Perform a power cycle of the unit"""

# Protocol type constants

PROTOCOL_TYPE_AHCI = 'Advanced Host Controller Interface'
PROTOCOL_TYPE_CIFS = 'Common Internet File System Protocol'
PROTOCOL_TYPE_FC = 'Fibre Channel'
PROTOCOL_TYPE_FCP = 'Fibre Channel Protocol for SCSI'
PROTOCOL_TYPE_FCoE = 'Fibre Channel over Ethernet'
PROTOCOL_TYPE_FICON = 'FIbre CONnection (FICON)'
PROTOCOL_TYPE_FTP = 'File Transfer Protocol'
PROTOCOL_TYPE_HTTP = 'Hypertext Transport Protocol'
PROTOCOL_TYPE_HTTPS = 'Secure Hypertext Transport Protocol'
PROTOCOL_TYPE_I2C = 'Inter-Integrated Circuit Bus'
PROTOCOL_TYPE_NFS = 'Network File System Protocol'
PROTOCOL_TYPE_NFSv3 = 'Network File System version 3'
PROTOCOL_TYPE_NFSv4 = 'Network File System version 4'
PROTOCOL_TYPE_NVMe = 'Non-Volatile Memory Express'
PROTOCOL_TYPE_NVMeOverFabrics = 'NVMe over Fabrics'
PROTOCOL_TYPE_OEM = 'OEM specific'
PROTOCOL_TYPE_PCIe = 'PCI Express'
PROTOCOL_TYPE_RoCE = 'RDMA over Converged Ethernet Protocol'
PROTOCOL_TYPE_RoCEv2 = 'RDMA over Converged Ethernet Protocol Version 2'
PROTOCOL_TYPE_SAS = 'Serial Attached SCSI'
PROTOCOL_TYPE_SATA = 'Serial AT Attachment'
PROTOCOL_TYPE_SCP = 'Secure File Copy Protocol'
PROTOCOL_TYPE_SFTP = 'Secure File Transfer Protocol'
PROTOCOL_TYPE_SMB = 'Server Message Block (CIFS Common Internet File System)'
PROTOCOL_TYPE_TFTP = 'Trivial File Transfer Protocol'
PROTOCOL_TYPE_UHCI = 'Universal Host Controller Interface'
PROTOCOL_TYPE_USB = 'Universal Serial Bus'
PROTOCOL_TYPE_iSCSI = 'Internet SCSI'
PROTOCOL_TYPE_iWARP = 'Internet Wide Area Remote Direct Memory Access Protocol'

# Durable name format constants

DURABLE_NAME_FORMAT_EUI = 'IEEE-defined 64-bit Extended Unique Identifier'
DURABLE_NAME_FORMAT_FC_WWN = 'Fibre Channel World Wide Name'
DURABLE_NAME_FORMAT_NAA = 'Name Address Authority Format'
DURABLE_NAME_FORMAT_NQN = 'NVMe Qualified Name'
DURABLE_NAME_FORMAT_NSID = 'NVM Namespace Identifier'
DURABLE_NAME_FORMAT_UUID = 'Universally Unique Identifier'
DURABLE_NAME_FORMAT_iQN = 'iSCSI Qualified Name'

# Apply time constants

APPLY_TIME_IMMEDIATE = 'immediate'
APPLY_TIME_ON_RESET = 'on reset'
APPLY_TIME_MAINT_START = 'at maintenance window start'
APPLY_TIME_MAINT_RESET = 'in maintenance window on reset'
