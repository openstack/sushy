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

# Values come from the Redfish UpdateService json-schema.
# https://redfish.dmtf.org/schemas/v1/TaskService.v1_1_5.json#/definitions/OverWritePolicy

import enum


class TaskState(enum.Enum):
    """Task state related constants."""
    CANCELLED = 'Cancelled'
    CANCELLING = 'Cancelling'
    COMPLETED = 'Completed'
    EXCEPTION = 'Exception'
    INTERRUPTED = 'Interrupted'
    NEW = 'New'
    PENDING = 'Pending'
    RUNNING = 'Running'
    SERVICE = 'Service'
    STARTING = 'Starting'
    STOPPING = 'Stopping'
    SUSPENDED = 'Suspended'

    # Deprecated in 1.2.0
    KILLED = 'Killed'


class OverWritePolicy(enum.Enum):
    """Overwrite Policy constants"""

    MANUAL = 'Manual'
    """Completed tasks are not automatically overwritten."""

    OLDEST = 'Oldest'
    """Oldest completed tasks are overwritten."""


# Backward compatibility
OVERWRITE_POLICY_MANUAL = OverWritePolicy.MANUAL
OVERWRITE_POLICY_OLDEST = OverWritePolicy.OLDEST
