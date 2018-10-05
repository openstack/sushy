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

from sushy.resources import constants as res_cons

# Manager Reset action constants

RESET_MANAGER_GRACEFUL_RESTART = res_cons.RESET_TYPE_GRACEFUL_RESTART
"""Perform a graceful shutdown followed by a restart of the system"""

RESET_MANAGER_FORCE_RESTART = res_cons.RESET_TYPE_FORCE_RESTART
"""Perform an immediate (non-graceful) shutdown, followed by a restart"""

# Manager Type constants

MANAGER_TYPE_MANAGEMENT_CONTROLLER = 'management controller'
"""A controller used primarily to monitor or manage the operation of
   a device or system"""

MANAGER_TYPE_ENCLOSURE_MANAGER = 'enclosure manager'
"""A controller which provides management functions for a chassis
   or group of devices or systems"""

MANAGER_TYPE_BMC = 'bmc'
"""A controller which provides management functions for a single
   computer system"""

MANAGER_TYPE_RACK_MANAGER = 'rack manager'
"""A controller which provides management functions for a whole or part
   of a rack"""

MANAGER_TYPE_AUXILIARY_CONTROLLER = 'auxiliary controller'
"""A controller which provides management functions for a particular
   subsystem or group of devices"""

# Graphical Console constants

GRAPHICAL_CONSOLE_KVMIP = 'graphical console kvmip'
"""Graphical Console connection using a KVM-IP (redirection of Keyboard,
   Video, Mouse over IP) protocol"""

GRAPHICAL_CONSOLE_OEM = 'graphical console oem'
"""Graphical Console connection using an OEM-specific protocol"""

# Serial Console constants

SERIAL_CONSOLE_SSH = 'serial console ssh'
"""Serial Console connection using the SSH protocol"""

SERIAL_CONSOLE_TELNET = 'serial console telnet'
"""Serial Console connection using the Telnet protocol"""

SERIAL_CONSOLE_IPMI = 'serial console ipmi'
"""Serial Console connection using the IPMI Serial-over-LAN (SOL) protocol"""

SERIAL_CONSOLE_OEM = 'serial console oem'
"""Serial Console connection using an OEM-specific protocol"""

# Command Shell constants

COMMAND_SHELL_SSH = 'command shell ssh'
"""Command Shell connection using the SSH protocol"""

COMMAND_SHELL_TELNET = 'command shell telnet'
"""Command Shell connection using the Telnet protocol"""

COMMAND_SHELL_IPMI = 'command shell ipmi'
"""Command Shell connection using the IPMI Serial-over-LAN (SOL) protocol"""

COMMAND_SHELL_OEM = 'command shell oem'
"""Command Shell connection using an OEM-specific protocol"""

# Supported Virtual Media Type constants

VIRTUAL_MEDIA_CD = 'cd'
VIRTUAL_MEDIA_DVD = 'dvd'
VIRTUAL_MEDIA_FLOPPY = 'floppy'
VIRTUAL_MEDIA_USBSTICK = 'usb'

# Connected Via constants

CONNECTED_VIA_APPLET = 'applet'
CONNECTED_VIA_NOT_CONNECTED = 'not_connected'
CONNECTED_VIA_OEM = 'oem'
CONNECTED_VIA_URI = 'uri'
