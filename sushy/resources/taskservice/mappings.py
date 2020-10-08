# Copyright (c) 2020 Dell, Inc. or its subsidiaries
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from sushy.resources import constants as res_cons
from sushy.resources.taskservice import constants as ts_cons
from sushy import utils


TASK_STATE_VALUE_MAP = {
    'New': res_cons.TASK_STATE_NEW,
    'Starting': res_cons.TASK_STATE_STARTING,
    'Running': res_cons.TASK_STATE_RUNNING,
    'Suspended': res_cons.TASK_STATE_SUSPENDED,
    'Interrupted': res_cons.TASK_STATE_INTERRUPTED,
    'Pending': res_cons.TASK_STATE_PENDING,
    'Stopping': res_cons.TASK_STATE_STOPPING,
    'Completed': res_cons.TASK_STATE_COMPLETED,
    'Killed': res_cons.TASK_STATE_KILLED,
    'Exception': res_cons.TASK_STATE_EXCEPTION,
    'Service': res_cons.TASK_STATE_SERVICE,
    'Cancelling': res_cons.TASK_STATE_CANCELLING,
    'Cancelled': res_cons.TASK_STATE_CANCELLED
}

OVERWRITE_POLICY_VALUE_MAP = {
    'Oldest': ts_cons.OVERWRITE_POLICY_OLDEST,
    'Manual': ts_cons.OVERWRITE_POLICY_MANUAL,
}

OVERWRITE_POLICY_VALUE_MAP_REV = (
    utils.revert_dictionary(OVERWRITE_POLICY_VALUE_MAP))
