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

from sushy.resources.system.storage import constants as store_cons
from sushy import utils

VOLUME_INIT_TYPE_MAP = {
    'Fast': store_cons.VOLUME_INIT_TYPE_FAST,
    'Slow': store_cons.VOLUME_INIT_TYPE_SLOW
}

VOLUME_INIT_TYPE_MAP_REV = (
    utils.revert_dictionary(VOLUME_INIT_TYPE_MAP)
)

VOLUME_TYPE_TYPE_MAP = {
    'RawDevice': store_cons.VOLUME_TYPE_RAW_DEVICE,
    'NonRedundant': store_cons.VOLUME_TYPE_NON_REDUNDANT,
    'Mirrored': store_cons.VOLUME_TYPE_MIRRORED,
    'StripedWithParity': store_cons.VOLUME_TYPE_STRIPED_WITH_PARITY,
    'SpannedMirrors': store_cons.VOLUME_TYPE_SPANNED_MIRRORS,
    'SpannedStripesWithParity':
        store_cons.VOLUME_TYPE_SPANNED_STRIPES_WITH_PARITY
}

RAID_TYPE_TYPE_MAP = {
    'RAID0': store_cons.RAID_TYPE_RAID0,
    'RAID1': store_cons.RAID_TYPE_RAID1,
    'RAID3': store_cons.RAID_TYPE_RAID3,
    'RAID4': store_cons.RAID_TYPE_RAID4,
    'RAID5': store_cons.RAID_TYPE_RAID5,
    'RAID6': store_cons.RAID_TYPE_RAID6,
    'RAID10': store_cons.RAID_TYPE_RAID10,
    'RAID01': store_cons.RAID_TYPE_RAID01,
    'RAID6TP': store_cons.RAID_TYPE_RAID6TP,
    'RAID1E': store_cons.RAID_TYPE_RAID1E,
    'RAID50': store_cons.RAID_TYPE_RAID50,
    'RAID60': store_cons.RAID_TYPE_RAID60,
    'RAID00': store_cons.RAID_TYPE_RAID00,
    'RAID10E': store_cons.RAID_TYPE_RAID10E,
    'RAID1Triple': store_cons.RAID_TYPE_RAID1Triple,
    'RAID10Triple': store_cons.RAID_TYPE_RAID10Triple,
}
