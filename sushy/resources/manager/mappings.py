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

from sushy.resources.manager import constants as mgr_cons
from sushy import utils


RESET_MANAGER_VALUE_MAP = {
    'GracefulRestart': mgr_cons.RESET_MANAGER_GRACEFUL_RESTART,
    'ForceRestart': mgr_cons.RESET_MANAGER_FORCE_RESTART,
}

RESET_MANAGER_VALUE_MAP_REV = utils.revert_dictionary(RESET_MANAGER_VALUE_MAP)

MANAGER_TYPE_VALUE_MAP = {
    'ManagementController': mgr_cons.MANAGER_TYPE_MANAGEMENT_CONTROLLER,
    'EnclosureManager': mgr_cons.MANAGER_TYPE_ENCLOSURE_MANAGER,
    'BMC': mgr_cons.MANAGER_TYPE_BMC,
    'RackManager': mgr_cons.MANAGER_TYPE_RACK_MANAGER,
    'AuxiliaryController': mgr_cons.MANAGER_TYPE_AUXILIARY_CONTROLLER
}

MANAGER_TYPE_VALUE_MAP_REV = (
    utils.revert_dictionary(MANAGER_TYPE_VALUE_MAP))

GRAPHICAL_CONSOLE_VALUE_MAP = {
    'KVMIP': mgr_cons.GRAPHICAL_CONSOLE_KVMIP,
    'Oem': mgr_cons.GRAPHICAL_CONSOLE_OEM,
}

GRAPHICAL_CONSOLE_VALUE_MAP_REV = (
    utils.revert_dictionary(GRAPHICAL_CONSOLE_VALUE_MAP))

SERIAL_CONSOLE_VALUE_MAP = {
    'SSH': mgr_cons.SERIAL_CONSOLE_SSH,
    'Telnet': mgr_cons.SERIAL_CONSOLE_TELNET,
    'IPMI': mgr_cons.SERIAL_CONSOLE_IPMI,
    'Oem': mgr_cons.SERIAL_CONSOLE_OEM,
}

SERIAL_CONSOLE_VALUE_MAP_REV = (
    utils.revert_dictionary(SERIAL_CONSOLE_VALUE_MAP))

COMMAND_SHELL_VALUE_MAP = {
    'SSH': mgr_cons.COMMAND_SHELL_SSH,
    'Telnet': mgr_cons.COMMAND_SHELL_TELNET,
    'IPMI': mgr_cons.COMMAND_SHELL_IPMI,
    'Oem': mgr_cons.COMMAND_SHELL_OEM,
}

COMMAND_SHELL_VALUE_MAP_REV = (
    utils.revert_dictionary(COMMAND_SHELL_VALUE_MAP))

MEDIA_TYPE_VALUE_MAP = {
    'CD': mgr_cons.VIRTUAL_MEDIA_CD,
    'DVD': mgr_cons.VIRTUAL_MEDIA_DVD,
    'Floppy': mgr_cons.VIRTUAL_MEDIA_FLOPPY,
    'USBStick': mgr_cons.VIRTUAL_MEDIA_USBSTICK
}

CONNECTED_VIA_VALUE_MAP = {
    "Applet": mgr_cons.CONNECTED_VIA_APPLET,
    "NotConnected": mgr_cons.CONNECTED_VIA_NOT_CONNECTED,
    "Oem": mgr_cons.CONNECTED_VIA_OEM,
    "URI": mgr_cons.CONNECTED_VIA_URI
}
