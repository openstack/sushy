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
import ssl
import xml.etree.ElementTree as ET

import flask
import libvirt

app = flask.Flask(__name__)
# Turn off strict_slashes on all routes
app.url_map.strict_slashes = False

LIBVIRT_URI = None

BOOT_DEVICE_MAP = {
    'Pxe': 'network',
    'Hdd': 'hd',
    'Cd': 'cdrom',
}

BOOT_DEVICE_MAP_REV = {v: k for k, v in BOOT_DEVICE_MAP.items()}


class libvirt_open(object):

    def __init__(self, uri, readonly=False):
        self.uri = uri
        self.readonly = readonly

    def __enter__(self):
        try:
            self._conn = (libvirt.openReadOnly(self.uri)
                          if self.readonly else
                          libvirt.open(self.uri))
            return self._conn
        except libvirt.libvirtError as e:
            print('Error when connecting to the libvirt URI "%(uri)s": '
                  '%(error)s' % {'uri': self.uri, 'error': e})
            flask.abort(500)

    def __exit__(self, type, value, traceback):
        self._conn.close()


def get_libvirt_domain(connection, domain):
    try:
        return connection.lookupByName(domain)
    except libvirt.libvirtError:
        flask.abort(404)


@app.route('/redfish/v1/')
def root_resource():
    return flask.render_template('root.json')


@app.route('/redfish/v1/Systems')
def system_collection_resource():
    with libvirt_open(LIBVIRT_URI, readonly=True) as conn:
        domains = conn.listDefinedDomains()
        return flask.render_template(
            'system_collection.json', system_count=len(domains),
            systems=domains)


def _get_total_cpus(domain, tree):
    total_cpus = 0
    if domain.isActive():
        total_cpus = domain.maxVcpus()
    else:
        # If we can't get it from maxVcpus() try to find it by
        # inspecting the domain XML
        if total_cpus <= 0:
            vcpu_element = tree.find('.//vcpu')
            if vcpu_element is not None:
                total_cpus = int(vcpu_element.text)
    return total_cpus


def _get_boot_source_target(tree):
    boot_source_target = None
    boot_element = tree.find('.//boot')
    if boot_element is not None:
        boot_source_target = (
            BOOT_DEVICE_MAP_REV.get(boot_element.get('dev')))
    return boot_source_target


@app.route('/redfish/v1/Systems/<identity>', methods=['GET', 'PATCH'])
def system_resource(identity):
    if flask.request.method == 'GET':
        with libvirt_open(LIBVIRT_URI, readonly=True) as conn:
            domain = get_libvirt_domain(conn, identity)
            power_state = 'On' if domain.isActive() else 'Off'
            total_memory_gb = int(domain.maxMemory() / 1024 / 1024)

            tree = ET.fromstring(domain.XMLDesc())
            total_cpus = _get_total_cpus(domain, tree)
            boot_source_target = _get_boot_source_target(tree)

            return flask.render_template(
                'system.json', identity=identity, uuid=domain.UUIDString(),
                power_state=power_state, total_memory_gb=total_memory_gb,
                total_cpus=total_cpus, boot_source_target=boot_source_target)

    elif flask.request.method == 'PATCH':
        boot = flask.request.json.get('Boot')
        if not boot:
            return 'PATCH only works for the Boot element', 400

        target = BOOT_DEVICE_MAP.get(boot.get('BootSourceOverrideTarget'))
        if not target:
            return 'Missing the BootSourceOverrideTarget element', 400

        # NOTE(lucasagomes): In libvirt we always set the boot
        # device frequency to "continuous" so, we are ignoring the
        # BootSourceOverrideEnabled element here

        # TODO(lucasagomes): We should allow changing the boot mode from
        # BIOS to UEFI (and vice-versa)

        with libvirt_open(LIBVIRT_URI) as conn:
            domain = get_libvirt_domain(conn, identity)
            tree = ET.fromstring(domain.XMLDesc())
            for os_element in tree.findall('os'):
                # Remove all "boot" elements
                for boot_element in os_element.findall('boot'):
                    os_element.remove(boot_element)

                # Add a new boot element with the request boot device
                boot_element = ET.SubElement(os_element, 'boot')
                boot_element.set('dev', target)

            conn.defineXML(ET.tostring(tree).decode('utf-8'))

        return '', 204


@app.route('/redfish/v1/Systems/<identity>/Actions/ComputerSystem.Reset',
           methods=['POST'])
def system_reset_action(identity):
    reset_type = flask.request.json.get('ResetType')
    with libvirt_open(LIBVIRT_URI) as conn:
        domain = get_libvirt_domain(conn, identity)
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
    parser.add_argument('-c', '--ssl-certificate',
                        type=str,
                        help='SSL certificate to use for HTTPS')
    parser.add_argument('-k', '--ssl-key',
                        type=str,
                        help='SSL key to use for HTTPS')
    return parser.parse_args()


if __name__ == '__main__':
    args = parse_args()
    LIBVIRT_URI = args.libvirt_uri

    ssl_context = None
    if args.ssl_certificate and args.ssl_key:
        ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
        ssl_context.load_cert_chain(args.ssl_certificate, args.ssl_key)

    app.run(host='', port=args.port, ssl_context=ssl_context)
