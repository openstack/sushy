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
import os
import ssl
import sys

try:
    from http import server as http_server
except ImportError:
    import BaseHTTPServer as http_server  # Py2

REDFISH_MOCKUP_FILES = None


class RequestHandler(http_server.BaseHTTPRequestHandler):

    REDFISH_SUBURI = '/redfish/v1'

    def _log_request(self, method):
        print(self.headers)
        content_length = int(self.headers.get('content-length', 0))
        if content_length > 0:
            print('Data: %s\n' % self.rfile.read(content_length))

    def do_GET(self):
        self._log_request('GET')
        path = self.path.rstrip('/')
        if not path.startswith(self.REDFISH_SUBURI):
            self.send_error(404)
            return

        resource_path = path.replace(self.REDFISH_SUBURI, '').lstrip('/')
        fpath = os.path.join(REDFISH_MOCKUP_FILES, resource_path, 'index.json')
        if not os.path.exists(fpath):
            self.send_error(404, 'Sub-URI %s not found' % resource_path)
            return

        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()

        with open(fpath, 'r') as f:
            self.wfile.write(f.read().encode('utf-8'))

    def do_POST(self):
        self._log_request('POST')
        self.send_response(204)
        self.end_headers()

    def do_PATCH(self):
        self._log_request('PATCH')
        self.send_response(204)
        self.end_headers()


def parse_args():
    parser = argparse.ArgumentParser('MockupServer')
    parser.add_argument('-p', '--port',
                        type=int,
                        default=8000,
                        help='The port to bind the server to')
    parser.add_argument('-m', '--mockup-files',
                        type=str,
                        required=True,
                        help=('The path to the Redfish Mockup files in '
                              'the filesystem'))
    parser.add_argument('-c', '--ssl-certificate',
                        type=str,
                        help='SSL certificate to use for HTTPS')
    parser.add_argument('-k', '--ssl-key',
                        type=str,
                        help='SSL key to use for HTTPS')
    return parser.parse_args()


if __name__ == '__main__':
    args = parse_args()
    if not os.path.exists(args.mockup_files):
        print('Mockup files %s not found' % args.mockup_files)
        sys.exit(1)

    REDFISH_MOCKUP_FILES = os.path.realpath(args.mockup_files)
    httpd = http_server.HTTPServer(('', args.port), RequestHandler)

    if args.ssl_certificate and args.ssl_key:
        httpd.socket = ssl.wrap_socket(
            httpd.socket, keyfile=args.ssl_key,
            certfile=args.ssl_certificate, server_side=True)

    httpd.serve_forever()
