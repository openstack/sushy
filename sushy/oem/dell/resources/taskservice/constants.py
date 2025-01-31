# Copyright (c) 2021 Dell Inc. or its subsidiaries.
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


class JobState(enum.Enum):
    """Job state constants"""

    COMPLETED = "Completed"
    """A job is in completed state"""

    COMPLETED_ERRORS = "CompletedWithErrors"
    """A job is in completed state with errors"""

    DOWNLOADED = "Downloaded"
    """A job is in downloaded state"""

    DOWNLOADING = "Downloading"
    """A job is in downloading state"""

    FAILED = "Failed"
    """A job is in failed state"""

    NEW = "New"
    """A job is in newly created state"""

    PAUSED = "Paused"
    """A job is in paused state"""

    PENDING_ACTIVATION = "PendingActivation"
    """A job is in pending activation state"""

    READY_EXECUTION = "ReadyForExecution"
    """A job is in ready for execution state"""

    REBOOT_COMPLETED = "RebootCompleted"
    """A job is in reboot completed state"""

    REBOOT_FAILED = "RebootFailed"
    """A job is in reboot failed state"""

    REBOOT_PENDING = "RebootPending"
    """A job is in pending state for reboot"""

    RUNNING = "Running"
    """A job is in running state"""

    SCHEDULED = "Scheduled"
    """A job is in scheduled state"""

    SCHEDULING = "Scheduling"
    """A job is in scheduling state"""

    UNKNOWN = "Unknown"
    """A job is in unknown state"""

    WAITING = "Waiting"
    """A job is in waiting state"""


# Backward compatibility
JOB_STATE_COMPLETED = JobState.COMPLETED
JOB_STATE_COMPLETED_ERRORS = JobState.COMPLETED_ERRORS
JOB_STATE_DOWNLOADED = JobState.DOWNLOADED
JOB_STATE_DOWNLOADING = JobState.DOWNLOADING
JOB_STATE_FAILED = JobState.FAILED
JOB_STATE_NEW = JobState.NEW
JOB_STATE_PAUSED = JobState.PAUSED
JOB_STATE_PENDING_ACTIVATION = JobState.PENDING_ACTIVATION
JOB_STATE_READY_EXECUTION = JobState.READY_EXECUTION
JOB_STATE_REBOOT_COMPLETED = JobState.REBOOT_COMPLETED
JOB_STATE_REBOOT_FAILED = JobState.REBOOT_FAILED
JOB_STATE_REBOOT_PENDING = JobState.REBOOT_PENDING
JOB_STATE_RUNNING = JobState.RUNNING
JOB_STATE_SCHEDULED = JobState.SCHEDULED
JOB_STATE_SCHEDULING = JobState.SCHEDULING
JOB_STATE_UNKNOWN = JobState.UNKNOWN
JOB_STATE_WAITING = JobState.WAITING


class JobType(enum.Enum):
    """Job type constants"""

    BIOS_CONF = "BIOSConfiguration"
    """A BIOS configuration job"""

    EXPORT_CONF = "ExportConfiguration"
    """A server configuration profile export job"""

    FC_CONF = "FCConfiguration"
    """A Fibre Channel configuration job"""

    FACTORY_CONF_EXPORT = "FactoryConfigurationExport"
    """A factory configuration export job"""

    FIRMWARE_ROLLBACK = "FirmwareRollback"
    """A firmware rollback job"""

    FIRMWARE_UPDATE = "FirmwareUpdate"
    """A firmware update job"""

    HW_INVENTORY_EXPORT = "HardwareInventoryExport"
    """A hardware inventory export job"""

    IMPORT_CONF = "ImportConfiguration"
    """A server configuration profile import job"""

    INBAND_BIOS_CONF = "InbandBIOSConfiguration"
    """An inband BIOS configuration job"""

    LC_CONF = "LCConfig"
    """A lifecycle controller attribute configuration job"""

    LC_EXPORT = "LCExport"
    """A lifecycle controller export job"""

    LC_LOG_EXPORT = "LCLogExport"
    """A lifecycle controller log export job"""

    LICENSE_EXPORT = "LicenseExport"
    """A license export job"""

    LICENSE_IMPORT = "LicenseImport"
    """A license import job"""

    MSG_REG_EXPORT = "MessageRegistryExport"
    """Export message registry report job"""

    NIC_CONF = "NICConfiguration"
    """A NIC configuration job"""

    OS_DEPLOY = "OSDeploy"
    """Operating System deploy job"""

    RAID_CONF = "RAIDConfiguration"
    """A RAID configuration job"""

    RT_NO_REBOOT_CONF = "RealTimeNoRebootConfiguration"
    """A real time configuration job without reboot"""

    REBOOT_FORCE = "RebootForce"
    """A reboot job with forced shutdown"""

    REBOOT_NO_FORCE = "RebootNoForce"
    """A graceful reboot job without forced shutdown"""

    REBOOT_POWER_CYCLE = "RebootPowerCycle"
    """A power cycle job"""

    REMOTE_DIAG = "RemoteDiagnostics"
    """A remote diagnostics job"""

    REPO_UPDATE = "RepositoryUpdate"
    """An update job from a repository"""

    SA_COL_EXP_HEALTH_DATA = "SACollectExportHealthData"
    """Support Assist collect and export health data job"""

    SA_COL_HEALTH_DATA = "SACollectHealthData"
    """Support Assist collect health data job"""

    SA_EXP_HEALTH_DATA = "SAExportHealthData"
    """Support Assist export health data job"""

    SA_ISM = "SAExposeISM"
    """Support Assist expose ISM installer package to host job"""

    SA_REG = "SARegistration"
    """Support Assist register iDRAC to Dell backend server job"""

    SEKM_REKEY = "SEKMRekey"
    """A Secure Enterprise Key Manager rekey job"""

    SEKM_STATUS_SET = "SEKMStatusSet"
    """A Secure Enterprise Key Manager status set job"""

    SHUTDOWN = "Shutdown"
    """A shutdown job"""

    SYS_ERASE = "SystemErase"
    """A selective system erase job"""

    SYS_INFO_CONF = "SystemInfoConfiguration"
    """A system info configuration job"""

    THERMAL_HIST_EXP = "ThermalHistoryExport"
    """A thermal history export job"""

    UNKNOWN = "Unknown"
    """An unknown job"""

    IDRAC_CONF = "iDRACConfiguration"
    """An iDRAC configuration job"""


# Backward compatibility
JOB_TYPE_BIOS_CONF = JobType.BIOS_CONF
JOB_TYPE_EXPORT_CONF = JobType.EXPORT_CONF
JOB_TYPE_FC_CONF = JobType.FC_CONF
JOB_TYPE_FACTORY_CONF_EXPORT = JobType.FACTORY_CONF_EXPORT
JOB_TYPE_FIRMWARE_ROLLBACK = JobType.FIRMWARE_ROLLBACK
JOB_TYPE_FIRMWARE_UPDATE = JobType.FIRMWARE_UPDATE
JOB_TYPE_HW_INVENTORY_EXPORT = JobType.HW_INVENTORY_EXPORT
JOB_TYPE_IMPORT_CONF = JobType.IMPORT_CONF
JOB_TYPE_INBAND_BIOS_CONF = JobType.INBAND_BIOS_CONF
JOB_TYPE_LC_CONF = JobType.LC_CONF
JOB_TYPE_LC_EXPORT = JobType.LC_EXPORT
JOB_TYPE_LC_LOG_EXPORT = JobType.LC_LOG_EXPORT
JOB_TYPE_LICENSE_EXPORT = JobType.LICENSE_EXPORT
JOB_TYPE_LICENSE_IMPORT = JobType.LICENSE_IMPORT
JOB_TYPE_MSG_REG_EXPORT = JobType.MSG_REG_EXPORT
JOB_TYPE_NIC_CONF = JobType.NIC_CONF
JOB_TYPE_OS_DEPLOY = JobType.OS_DEPLOY
JOB_TYPE_RAID_CONF = JobType.RAID_CONF
JOB_TYPE_RT_NO_REBOOT_CONF = JobType.RT_NO_REBOOT_CONF
JOB_TYPE_REBOOT_FORCE = JobType.REBOOT_FORCE
JOB_TYPE_REBOOT_NO_FORCE = JobType.REBOOT_NO_FORCE
JOB_TYPE_REBOOT_POWER_CYCLE = JobType.REBOOT_POWER_CYCLE
JOB_TYPE_REMOTE_DIAG = JobType.REMOTE_DIAG
JOB_TYPE_REPO_UPDATE = JobType.REPO_UPDATE
JOB_TYPE_SA_COL_EXP_HEALTH_DATA = JobType.SA_COL_EXP_HEALTH_DATA
JOB_TYPE_SA_COL_HEALTH_DATA = JobType.SA_COL_HEALTH_DATA
JOB_TYPE_SA_EXP_HEALTH_DATA = JobType.SA_EXP_HEALTH_DATA
JOB_TYPE_SA_ISM = JobType.SA_ISM
JOB_TYPE_SA_REG = JobType.SA_REG
JOB_TYPE_SEKM_REKEY = JobType.SEKM_REKEY
JOB_TYPE_SEKM_STATUS_SET = JobType.SEKM_STATUS_SET
JOB_TYPE_SHUTDOWN = JobType.SHUTDOWN
JOB_TYPE_SYS_ERASE = JobType.SYS_ERASE
JOB_TYPE_SYS_INFO_CONF = JobType.SYS_INFO_CONF
JOB_TYPE_THERMAL_HIST_EXP = JobType.THERMAL_HIST_EXP
JOB_TYPE_UNKNOWN = JobType.UNKNOWN
JOB_TYPE_IDRAC_CONF = JobType.IDRAC_CONF
