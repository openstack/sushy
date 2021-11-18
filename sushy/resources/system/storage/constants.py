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

# From http://redfish.dmtf.org/schemas/swordfish/v1/Volume.json

import enum


# FIXME(dtantsur): this is deprecated in favour of InitializeMethod
class VolumeInitializeType(enum.Enum):
    FAST = 'Fast'
    """The volume is prepared for use quickly, typically by erasing just the
    beginning and end of the space so that partitioning can be performed."""

    SLOW = 'Slow'
    """The volume is prepared for use slowly, typically by completely
    erasing the volume."""


# Backward compatibility
VOLUME_INIT_TYPE_FAST = VolumeInitializeType.FAST
VOLUME_INIT_TYPE_SLOW = VolumeInitializeType.SLOW


class VolumeType(enum.Enum):
    RAW_DEVICE = 'RawDevice'
    """The volume is a raw physical device without any RAID or other
    virtualization applied."""

    NON_REDUNDANT = 'NonRedundant'
    """The volume is a non-redundant storage device."""

    MIRRORED = 'Mirrored'
    """The volume is a mirrored device."""

    STRIPED_WITH_PARITY = 'StripedWithParity'
    """The volume is a device which uses parity to retain redundant
    information."""

    SPANNED_MIRRORS = 'SpannedMirrors'
    """The volume is a spanned set of mirrored devices."""

    SPANNED_STRIPES_WITH_PARITY = 'SpannedStripesWithParity'
    """The volume is a spanned set of devices which uses parity to retain
    redundant information."""


# Backward compatibility
VOLUME_TYPE_RAW_DEVICE = VolumeType.RAW_DEVICE
VOLUME_TYPE_NON_REDUNDANT = VolumeType.NON_REDUNDANT
VOLUME_TYPE_MIRRORED = VolumeType.MIRRORED
VOLUME_TYPE_STRIPED_WITH_PARITY = VolumeType.STRIPED_WITH_PARITY
VOLUME_TYPE_SPANNED_MIRRORS = VolumeType.SPANNED_MIRRORS
VOLUME_TYPE_SPANNED_STRIPES_WITH_PARITY = \
    VolumeType.SPANNED_STRIPES_WITH_PARITY


class RAIDType(enum.Enum):
    RAID0 = 'RAID0'
    """A placement policy where consecutive logical blocks of data are
    uniformly distributed across a set of independent storage devices
    without offering any form of redundancy."""

    RAID1 = 'RAID1'
    """A placement policy where each logical block of data is stored on more
    than one independent storage device."""

    RAID3 = 'RAID3'
    """A placement policy using parity-based protection where logical bytes
    of data are uniformly distributed across a set of independent storage
    devices and where the parity is stored on a dedicated independent
    storage device."""

    RAID4 = 'RAID4'
    """A placement policy using parity-based protection where logical blocks
    of data are uniformly distributed across a set of independent storage
    devices and where the parity is stored on a dedicated independent
    storage device."""

    RAID5 = 'RAID5'
    """A placement policy using parity-based protection for storing stripes
    of 'n' logical blocks of data and one logical block of parity across
    a set of 'n+1' independent storage devices where the parity and data
    blocks are interleaved across the storage devices."""

    RAID6 = 'RAID6'
    """A placement policy using parity-based protection for storing stripes
    of 'n' logical blocks of data and two logical blocks of independent
    parity across a set of 'n+2' independent storage devices where the
    parity and data blocks are interleaved across the storage devices."""

    RAID10 = 'RAID10'
    """A placement policy that creates a striped device (RAID 0) over a set
    of mirrored devices (RAID 1)."""

    RAID01 = 'RAID01'
    """A data placement policy that creates a mirrored device (RAID 1) over
    a set of striped devices (RAID 0)."""

    RAID6TP = 'RAID6TP'
    """A placement policy that uses parity-based protection for storing
    stripes of 'n' logical blocks of data and three logical blocks of
    independent parity across a set of 'n+3' independent storage devices
    where the parity and data blocks are interleaved across the storage
    devices."""

    RAID1E = 'RAID1E'
    """A placement policy that uses a form of mirroring implemented over a
    set of independent storage devices where logical blocks are
    duplicated on a pair of independent storage devices so that data is
    uniformly distributed across the storage devices."""

    RAID50 = 'RAID50'
    """A placement policy that uses a RAID 0 stripe set over two or more
    RAID 5 sets of independent storage devices."""

    RAID60 = 'RAID60'
    """A placement policy that uses a RAID 0 stripe set over two or more
    RAID 6 sets of independent storage devices."""

    RAID00 = 'RAID00'
    """A placement policy that creates a RAID 0 stripe set over two or more
    RAID 0 sets."""

    RAID10E = 'RAID10E'
    """A placement policy that uses a RAID 0 stripe set over two or more
    RAID 10 sets."""

    RAID1_TRIPLE = 'RAID1Triple'
    """A placement policy where each logical block of data is mirrored three
    times across a set of three independent storage devices."""

    RAID10_TRIPLE = 'RAID10Triple'
    """A placement policy that uses a striped device (RAID 0) over a set of
    triple mirrored devices (RAID 1Triple)."""

    NONE = 'None'
    """A placement policy with no redundancy at the device level."""


# Backward compatibility
RAID_TYPE_RAID0 = RAIDType.RAID0
RAID_TYPE_RAID1 = RAIDType.RAID1
RAID_TYPE_RAID3 = RAIDType.RAID3
RAID_TYPE_RAID4 = RAIDType.RAID4
RAID_TYPE_RAID5 = RAIDType.RAID5
RAID_TYPE_RAID6 = RAIDType.RAID6
RAID_TYPE_RAID10 = RAIDType.RAID10
RAID_TYPE_RAID01 = RAIDType.RAID01
RAID_TYPE_RAID6TP = RAIDType.RAID6TP
RAID_TYPE_RAID1E = RAIDType.RAID1E
RAID_TYPE_RAID50 = RAIDType.RAID50
RAID_TYPE_RAID60 = RAIDType.RAID60
RAID_TYPE_RAID00 = RAIDType.RAID00
RAID_TYPE_RAID10E = RAIDType.RAID10E
RAID_TYPE_RAID1Triple = RAIDType.RAID1_TRIPLE
RAID_TYPE_RAID10Triple = RAIDType.RAID10_TRIPLE
RAID_TYPE_NONE = RAIDType.NONE
