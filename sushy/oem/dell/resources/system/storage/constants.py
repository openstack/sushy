# Copyright (c) 2022 Dell Inc. or its subsidiaries.
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


class ControllerMode(enum.Enum):
    """RAID controller modes."""

    RAID = "RAID"
    """RAID mode."""

    HBA = "HBA"
    """HBA/Passthru mode. Does not support RAID. For PERC 9 controllers."""

    EHBA = "EnhancedHBA"
    """Enhanced HBA mode. Limited RAID support. For PERC 10 controllers."""
