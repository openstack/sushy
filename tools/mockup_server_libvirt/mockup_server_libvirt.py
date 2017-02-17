#!/usr/bin/env python
#
# Copyright 2017 Red Hat, Inc.
# All Rights Reserved.
#
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

import argparse
import xml.etree.ElementTree as ET

import flask
import libvirt

app = flask.Flask(__name__)
LIBVIRT_CONN = None

SET_BOOT_DEVICES_MAP = {
    'Pxe': 'network',
    'Hdd': 'hd',
    'Cd': 'cdrom',
}


def _get_libvirt_domain(domain):
    try:
        return LIBVIRT_CONN.lookupByName(domain)
    except libvirt.libvirtError:
        flask.abort(404)


@app.route('/redfish/v1/')
def root_resource():
    return flask.render_template('root.json')


@app.route('/redfish/v1/Systems')
def system_collection_resource():
    domains = LIBVIRT_CONN.listDefinedDomains()
    return flask.render_template(
        'system_collection.json', system_count=len(domains), systems=domains)


@app.route('/redfish/v1/Systems/<identity>', methods=['GET', 'PATCH'])
def system_resource(identity):
    domain = _get_libvirt_domain(identity)
    if flask.request.method == 'GET':
        power_state = 'On' if domain.isActive() else 'Off'
        total_memory_gb = int(domain.maxMemory() / 1024 / 1024)
        try:
            total_cpus = domain.maxVcpus()
        except libvirt.libvirtError:
            # NOTE(lucasagomes): Getting the maxVcpus() requires the
            # domain to be running
            total_cpus = 0

        return flask.render_template(
            'system.json', identity=identity, uuid=domain.UUIDString(),
            power_state=power_state, total_memory_gb=total_memory_gb,
            total_cpus=total_cpus)

    elif flask.request.method == 'PATCH':
        boot = flask.request.json.get('Boot')
        if not boot:
            return 'PATCH only works for the Boot element', 400

        target = SET_BOOT_DEVICES_MAP.get(boot.get('BootSourceOverrideTarget'))
        if not target:
            return 'Missing the BootSourceOverrideTarget element', 400

        # NOTE(lucasagomes): In libvirt we always set the boot
        # device frequency to "continuous" so, we are ignoring the
        # BootSourceOverrideEnabled element here

        # TODO(lucasagomes): We should allow changing the boot mode from
        # BIOS to UEFI (and vice-versa)

        tree = ET.fromstring(domain.XMLDesc())
        for os_element in tree.findall('os'):
            # Remove all "boot" elements
            for boot_element in os_element.findall('boot'):
                os_element.remove(boot_element)

            # Add a new boot element with the request boot device
            boot_element = ET.SubElement(os_element, 'boot')
            boot_element.set('dev', target)
        LIBVIRT_CONN.defineXML(ET.tostring(tree).decode('utf-8'))
        return '', 204


@app.route('/redfish/v1/Systems/<identity>/Actions/ComputerSystem.Reset',
           methods=['POST'])
def system_reset_action(identity):
    domain = _get_libvirt_domain(identity)
    reset_type = flask.request.json.get('ResetType')
    try:
        if reset_type in ('On', 'ForceOn'):
            if not domain.isActive():
                domain.create()
        elif reset_type == 'ForceOff':
            if domain.isActive():
                domain.destroy()
        elif reset_type == 'GracefulShutdown':
            if domain.isActive():
                domain.shutdown()
        elif reset_type == 'GracefulRestart':
            if domain.isActive():
                domain.reboot()
        elif reset_type == 'ForceRestart':
            if domain.isActive():
                domain.reset()
        elif reset_type == 'Nmi':
            if domain.isActive():
                domain.injectNMI()
    except libvirt.libvirtError:
        flask.abort(500)

    return '', 204


def parse_args():
    parser = argparse.ArgumentParser('MockupServerLibvirt')
    parser.add_argument('-p', '--port',
                        type=int,
                        default=8000,
                        help='The port to bind the server to')
    parser.add_argument('-u', '--libvirt-uri',
                        type=str,
                        default='qemu:///system',
                        help='The libvirt URI')
    return parser.parse_args()


if __name__ == '__main__':
    args = parse_args()
    LIBVIRT_CONN = libvirt.open(args.libvirt_uri)
    app.run(host='', port=args.port)
