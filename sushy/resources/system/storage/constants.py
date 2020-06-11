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

# RAIDType Types
RAID_TYPE_RAID0 = 'RAID0'
"""A placement policy where consecutive logical blocks of data are uniformly
distributed across a set of independent storage devices without offering any
form of redundancy."""

RAID_TYPE_RAID1 = 'RAID1'
"""A placement policy where each logical block of data is stored on more than
one independent storage device."""

RAID_TYPE_RAID3 = 'RAID3'
"""A placement policy using parity-based protection where logical bytes of
data are uniformly distributed across a set of independent storage devices and
where the parity is stored on a dedicated independent storage device."""

RAID_TYPE_RAID4 = 'RAID4'
"""A placement policy using parity-based protection where logical blocks of
data are uniformly distributed across a set of independent storage devices and
where the parity is stored on a dedicated independent storage device."""

RAID_TYPE_RAID5 = 'RAID5'
"""A placement policy using parity-based protection for storing stripes of 'n'
logical blocks of data and one logical block of parity across a set of 'n+1'
independent storage devices where the parity and data blocks are interleaved
across the storage devices."""

RAID_TYPE_RAID6 = 'RAID6'
"""A placement policy using parity-based protection for storing stripes of 'n'
logical blocks of data and two logical blocks of independent parity across a
set of 'n+2' independent storage devices where the parity and data blocks are
interleaved across the storage devices."""

RAID_TYPE_RAID10 = 'RAID10'
"""A placement policy that creates a striped device (RAID 0) over a set of
mirrored devices (RAID 1)."""

RAID_TYPE_RAID01 = 'RAID01'
"""A data placement policy that creates a mirrored device (RAID 1) over a set
of striped devices (RAID 0)."""

RAID_TYPE_RAID6TP = 'RAID6TP'
"""A placement policy that uses parity-based protection for storing stripes of
'n' logical blocks of data and three logical blocks of independent parity
across a set of 'n+3' independent storage devices where the parity and data
blocks are interleaved across the storage devices."""

RAID_TYPE_RAID1E = 'RAID1E'
"""A placement policy that uses a form of mirroring implemented over a set of
independent storage devices where logical blocks are duplicated on a pair of
independent storage devices so that data is uniformly distributed across the
storage devices."""

RAID_TYPE_RAID50 = 'RAID50'
"""A placement policy that uses a RAID 0 stripe set over two or more RAID 5
sets of independent storage devices."""

RAID_TYPE_RAID60 = 'RAID60'
"""A placement policy that uses a RAID 0 stripe set over two or more RAID 6
sets of independent storage devices."""

RAID_TYPE_RAID00 = 'RAID00'
"""A placement policy that creates a RAID 0 stripe set over two or more RAID 0
sets."""

RAID_TYPE_RAID10E = 'RAID10E'
"""A placement policy that uses a RAID 0 stripe set over two or more RAID 10
sets."""

RAID_TYPE_RAID1Triple = 'RAID1Triple'
"""A placement policy where each logical block of data is mirrored three times
across a set of three independent storage devices."""

RAID_TYPE_RAID10Triple = 'RAID10Triple'
"""A placement policy that uses a striped device (RAID 0) over a set of triple
mirrored devices (RAID 1Triple)."""
