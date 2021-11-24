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

# Values comes from the Redfish System json-schema 1.0.0:
# http://redfish.dmtf.org/schemas/v1/Manager.v1_0_0.json#/definitions/Manager  # noqa

import enum

from sushy.resources import constants as res_cons

# Manager Reset action constants

RESET_MANAGER_GRACEFUL_RESTART = res_cons.ResetType.GRACEFUL_RESTART
"""Perform a graceful shutdown followed by a restart of the system"""

RESET_MANAGER_FORCE_RESTART = res_cons.ResetType.FORCE_RESTART
"""Perform an immediate (non-graceful) shutdown, followed by a restart"""


class ManagerType(enum.Enum):
    """Manager Type constants"""

    MANAGEMENT_CONTROLLER = 'ManagementController'
    """A controller that primarily monitors or manages the operation of a
    device or system."""

    ENCLOSURE_MANAGER = 'EnclosureManager'
    """A controller that provides management functions for a chassis or
    group of devices or systems."""

    BMC = 'BMC'
    """A controller that provides management functions for a single computer
    system."""

    RACK_MANAGER = 'RackManager'
    """A controller that provides management functions for a whole or part
    of a rack."""

    AUXILIARY_CONTROLLER = 'AuxiliaryController'
    """A controller that provides management functions for a particular
    subsystem or group of devices."""

    SERVICE = 'Service'
    """A software-based service that provides management functions."""


# Backward compatibility
MANAGER_TYPE_MANAGEMENT_CONTROLLER = ManagerType.MANAGEMENT_CONTROLLER
MANAGER_TYPE_ENCLOSURE_MANAGER = ManagerType.ENCLOSURE_MANAGER
MANAGER_TYPE_BMC = ManagerType.BMC
MANAGER_TYPE_RACK_MANAGER = ManagerType.RACK_MANAGER
MANAGER_TYPE_AUXILIARY_CONTROLLER = ManagerType.AUXILIARY_CONTROLLER


class GraphicalConnectType(enum.Enum):
    """Graphical Console constants"""

    KVMIP = 'KVMIP'
    """The controller supports a graphical console connection through a KVM-
    IP (redirection of Keyboard, Video, Mouse over IP) protocol."""

    OEM = 'Oem'
    """The controller supports a graphical console connection through an
    OEM-specific protocol."""


# Backward compatibility
GRAPHICAL_CONSOLE_KVMIP = GraphicalConnectType.KVMIP
GRAPHICAL_CONSOLE_OEM = GraphicalConnectType.OEM


class SerialConnectType(enum.Enum):
    """Serial Console constants"""

    SSH = 'SSH'
    """The controller supports a serial console connection through the SSH
    protocol."""

    TELNET = 'Telnet'
    """The controller supports a serial console connection through the
    Telnet protocol."""

    IPMI = 'IPMI'
    """The controller supports a serial console connection through the IPMI
    Serial Over LAN (SOL) protocol."""

    OEM = 'Oem'
    """The controller supports a serial console connection through an OEM-
    specific protocol."""


# Backward compatibility
SERIAL_CONSOLE_SSH = SerialConnectType.SSH
SERIAL_CONSOLE_TELNET = SerialConnectType.TELNET
SERIAL_CONSOLE_IPMI = SerialConnectType.IPMI
SERIAL_CONSOLE_OEM = SerialConnectType.OEM


class CommandConnectType(enum.Enum):
    """Command Shell constants"""

    SSH = 'SSH'
    """The controller supports a command shell connection through the SSH
    protocol."""

    TELNET = 'Telnet'
    """The controller supports a command shell connection through the Telnet
    protocol."""

    IPMI = 'IPMI'
    """The controller supports a command shell connection through the IPMI
    Serial Over LAN (SOL) protocol."""

    OEM = 'Oem'
    """The controller supports a command shell connection through an OEM-
    specific protocol."""


# Backward compatibility
COMMAND_SHELL_SSH = CommandConnectType.SSH
COMMAND_SHELL_TELNET = CommandConnectType.TELNET
COMMAND_SHELL_IPMI = CommandConnectType.IPMI
COMMAND_SHELL_OEM = CommandConnectType.OEM


class VirtualMediaType(enum.Enum):
    """Supported Virtual Media Type constants"""

    CD = 'CD'
    """A CD-ROM format (ISO) image."""

    FLOPPY = 'Floppy'
    """A floppy disk image."""

    USB_STICK = 'USBStick'
    """An emulation of a USB storage device."""

    DVD = 'DVD'
    """A DVD-ROM format image."""


# Backward compatibility
VIRTUAL_MEDIA_CD = VirtualMediaType.CD
VIRTUAL_MEDIA_DVD = VirtualMediaType.DVD
VIRTUAL_MEDIA_FLOPPY = VirtualMediaType.FLOPPY
VIRTUAL_MEDIA_USBSTICK = VirtualMediaType.USB_STICK


class ConnectedVia(enum.Enum):
    """Connected Via constants"""

    NOT_CONNECTED = 'NotConnected'
    """No current connection."""

    URI = 'URI'
    """Connected to a URI location."""

    APPLET = 'Applet'
    """Connected to a client application."""

    OEM = 'Oem'
    """Connected through an OEM-defined method."""


# Backward compatibility
CONNECTED_VIA_NOT_CONNECTED = ConnectedVia.NOT_CONNECTED
CONNECTED_VIA_URI = ConnectedVia.URI
CONNECTED_VIA_APPLET = ConnectedVia.APPLET
CONNECTED_VIA_OEM = ConnectedVia.OEM


class TransferMethod(enum.Enum):
    """Transfer methods"""

    STREAM = 'Stream'
    """Stream image file data from the source URI."""

    UPLOAD = 'Upload'
    """Upload the entire image file from the source URI to the service."""
