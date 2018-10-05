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

# Values comes from the Redfish Chassis json-schema 1.8.0:
# http://redfish.dmtf.org/schemas/v1/Chassis.v1_8_0.json#/definitions/Chassis

# Chassis Types constants

CHASSIS_TYPE_RACK = 'rack chassis type'
"""An equipment rack, typically a 19-inch wide freestanding unit"""

CHASSIS_TYPE_BLADE = 'blade chassis type'
"""Blade

An enclosed or semi-enclosed, typically vertically-oriented, system
chassis which must be plugged into a multi-system chassis to function
normally.
"""

CHASSIS_TYPE_ENCLOSURE = 'enclosure chassis type'
"""A generic term for a chassis that does not fit any other description"""

CHASSIS_TYPE_STAND_ALONE = 'stand alone chassis type'
"""StandAlone

A single, free-standing system, commonly called a tower or desktop
chassis.
"""

CHASSIS_TYPE_RACK_MOUNT = 'rack mount chassis type'
"""RackMount

A single system chassis designed specifically for mounting in an
equipment rack.
"""

CHASSIS_TYPE_CARD = 'card chassis type'
"""Card

A loose device or circuit board intended to be installed in a system or
other enclosure.
"""

CHASSIS_TYPE_CARTRIDGE = 'cartridge chassis type'
"""Cartridge

A small self-contained system intended to be plugged into a multi-system
chassis"""

CHASSIS_TYPE_ROW = 'row chassis type'
"""A collection of equipment rack"""

CHASSIS_TYPE_POD = 'pod chassis type'
"""Pod

A collection of equipment racks in a large, likely transportable,
container"""

CHASSIS_TYPE_EXPANSION = 'expansion chassis type'
"""A chassis which expands the capabilities or capacity of another chassis"""

CHASSIS_TYPE_SIDECAR = 'sidecar chassis type'
"""Sidecar

A chassis that mates mechanically with another chassis to expand its
capabilities or capacity.
"""

CHASSIS_TYPE_ZONE = 'zone chassis type'
"""Zone

A logical division or portion of a physical chassis that contains multiple
devices or systems that cannot be physically separated.
"""

CHASSIS_TYPE_SLED = 'sled chassis type'
"""Sled

An enclosed or semi-enclosed, system chassis which must be plugged into a
multi-system chassis to function normally similar to a blade type chassis.
"""

CHASSIS_TYPE_SHELF = 'shelf chassis type'
"""Shelf

An enclosed or semi-enclosed, typically horizontally-oriented, system chassis
which must be plugged into a multi-system chassis to function
normally.
"""

CHASSIS_TYPE_DRAWER = 'drawer chassis type'
"""Drawer

An enclosed or semi-enclosed, typically horizontally-oriented, system
chassis which may be slid into a multi-system chassis.
"""

CHASSIS_TYPE_MODULE = 'module chassis type'
"""Module

A small, typically removable, chassis or card which contains devices for
a particular subsystem or function.
"""

CHASSIS_TYPE_COMPONENT = 'component chassis type'
"""Component

A small chassis, card, or device which contains devices for a particular
subsystem or function.
"""

CHASSIS_TYPE_IP_BASED_DRIVE = 'IP based drive chassis type'
"""A chassis in a drive form factor with IP-based network connections"""

CHASSIS_TYPE_RACK_GROUP = 'rack group chassis type'
"""A group of racks which form a single entity or share infrastructure"""

CHASSIS_TYPE_STORAGE_ENCLOSURE = 'storage enclosure chassis type'
"""A chassis which encloses storage"""

CHASSIS_TYPE_OTHER = 'other chassis type'
"""A chassis that does not fit any of these definitions"""

# Chassis IntrusionSensor constants

CHASSIS_INTRUSION_SENSOR_NORMAL = 'normal chassis intrusion sensor'
"""No abnormal physical security conditions are detected at this time"""

CHASSIS_INTRUSION_SENSOR_HARDWARE_INTRUSION = 'hardware intrusion chassis ' \
                                              'intrusion sensor'
"""HardwareIntrusion

A door, lock, or other mechanism protecting the internal system hardware from
being accessed is detected as being in an insecure state.
"""

CHASSIS_INTRUSION_SENSOR_TAMPERING_DETECTED = 'tampering detected chassis ' \
                                              'intrusion sensor'
"""Physical tampering of the monitored entity is detected"""

# Chassis IntrusionSensorReArm constants

CHASSIS_INTRUSION_SENSOR_RE_ARM_MANUAL = 'manual re arm chassis intrusion ' \
                                         'sensor'
"""This sensor would be restored to the Normal state by a manual re-arm"""

CHASSIS_INTRUSION_SENSOR_RE_ARM_AUTOMATIC = 'automatic re arm chassis ' \
                                            'intrusion sensor'
"""Automatic

This sensor would be restored to the Normal state automatically as no abnormal
physical security conditions are detected.
"""
