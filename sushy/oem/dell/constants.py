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

IDRAC_CONFIG_PENDING = 'LC068'
IDRAC_JOB_RUNNING = 'RAC0679'
NO_FOREIGN_CONFIG = 'STOR018'
# Job states in which the Lifecycle Controller has stopped working on a
# job: it will make no further progress without a new request. Any other
# state means the job is still in flight, including transient ones such
# as 'Downloading', 'RebootPending' and 'UserIntervention' (which iDRAC
# uses for firmware that is staged but not yet flashed during POST), and
# any state a future iDRAC firmware may introduce.
TERMINAL_JOB_STATES = ['Completed',
                       'CompletedWithErrors',
                       'Failed',
                       'RebootFailed']

# Deprecated: an allowlist of only some of the incomplete job states, and
# therefore unusable for deciding whether a job has finished. Retained
# for backward compatibility; use TERMINAL_JOB_STATES instead.
INCOMPLETE_JOB_STATES = ['Scheduled',
                         'Running',
                         'Paused']
