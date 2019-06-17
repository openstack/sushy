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

# Volume Initialization Types
VOLUME_INIT_TYPE_FAST = 'fast'
"""The volume is prepared for use quickly, typically by erasing just the
beginning and end of the space so that partitioning can be performed."""

VOLUME_INIT_TYPE_SLOW = 'slow'
"""The volume is prepared for use slowly, typically by completely erasing
the volume."""

# VolumeType Types
VOLUME_TYPE_RAW_DEVICE = 'rawdevice'
"""The volume is a raw physical device without any RAID or other
virtualization applied."""

VOLUME_TYPE_NON_REDUNDANT = 'nonredundant'
"""The volume is a non-redundant storage device."""

VOLUME_TYPE_MIRRORED = 'mirrored'
"""The volume is a mirrored device."""

VOLUME_TYPE_STRIPED_WITH_PARITY = 'stripedwithparity'
"""The volume is a device which uses parity to retain redundant information."""

VOLUME_TYPE_SPANNED_MIRRORS = 'spannedmirrors'
"""The volume is a spanned set of mirrored devices."""

VOLUME_TYPE_SPANNED_STRIPES_WITH_PARITY = 'spannedstripeswithparity'
"""The volume is a spanned set of devices which uses parity to retain
redundant information."""
