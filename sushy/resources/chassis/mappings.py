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

from sushy.resources.chassis import constants as cha_cons

CHASSIS_TYPE_VALUE_MAP = {
    'Rack': cha_cons.CHASSIS_TYPE_RACK,
    'Blade': cha_cons.CHASSIS_TYPE_BLADE,
    'Enclosure': cha_cons.CHASSIS_TYPE_ENCLOSURE,
    'StandAlone': cha_cons.CHASSIS_TYPE_STAND_ALONE,
    'RackMount': cha_cons.CHASSIS_TYPE_RACK_MOUNT,
    'Card': cha_cons.CHASSIS_TYPE_CARD,
    'Cartridge': cha_cons.CHASSIS_TYPE_CARTRIDGE,
    'Row': cha_cons.CHASSIS_TYPE_ROW,
    'Pod': cha_cons.CHASSIS_TYPE_POD,
    'Expansion': cha_cons.CHASSIS_TYPE_EXPANSION,
    'Sidecar': cha_cons.CHASSIS_TYPE_SIDECAR,
    'Zone': cha_cons.CHASSIS_TYPE_ZONE,
    'Sled': cha_cons.CHASSIS_TYPE_SLED,
    'Shelf': cha_cons.CHASSIS_TYPE_SHELF,
    'Drawer': cha_cons.CHASSIS_TYPE_DRAWER,
    'Module': cha_cons.CHASSIS_TYPE_MODULE,
    'Component': cha_cons.CHASSIS_TYPE_COMPONENT,
    'IPBasedDrive': cha_cons.CHASSIS_TYPE_IP_BASED_DRIVE,
    'RackGroup': cha_cons.CHASSIS_TYPE_RACK_GROUP,
    'StorageEnclosure': cha_cons.CHASSIS_TYPE_STORAGE_ENCLOSURE,
    'Other': cha_cons.CHASSIS_TYPE_OTHER,
}

CHASSIS_INTRUSION_SENSOR_MAP = {
    'Normal': cha_cons.CHASSIS_INTRUSION_SENSOR_NORMAL,
    'HardwareIntrusion': cha_cons.CHASSIS_INTRUSION_SENSOR_HARDWARE_INTRUSION,
    'TamperingDetected': cha_cons.CHASSIS_INTRUSION_SENSOR_TAMPERING_DETECTED,
}

CHASSIS_INTRUSION_SENSOR_RE_ARM_MAP = {
    'Manual': cha_cons.CHASSIS_INTRUSION_SENSOR_RE_ARM_MANUAL,
    'Automatic': cha_cons.CHASSIS_INTRUSION_SENSOR_RE_ARM_AUTOMATIC,
}
