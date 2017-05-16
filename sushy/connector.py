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

import json
import logging

import requests
from six.moves.urllib import parse

from sushy import exceptions

LOG = logging.getLogger(__name__)


class Connector(object):

    def __init__(self, url, username=None, password=None, verify=True):
        self._url = url
        self._auth = (username, password)
        self._verify = verify

    def _op(self, method, path='', data=None, headers=None):
        """Generic RESTful request handler.

        :param method: The HTTP method to be used, e.g: GET, POST,
            PUT, PATCH, etc...
        :param path: The sub-URI path to the resource.
        :param data: Optional JSON data.
        :param headers: Optional dictionary of headers.
        :returns: The response object from the requests library.
        :raises: ConnectionError
        :raises: HTTPError
        """
        if headers is None:
            headers = {}

        headers['Content-Type'] = 'application/json'

        with requests.Session() as session:
            session.headers = headers
            session.verify = self._verify

            if all(v is not None for v in self._auth):
                session.auth = self._auth

            if data is not None:
                data = json.dumps(data)

            url = parse.urljoin(self._url, path)
            # TODO(lucasagomes): We should mask the data to remove sensitive
            # information
            LOG.debug('HTTP request: %(method)s %(url)s; '
                      'headers: %(headers)s; body: %(data)s',
                      {'method': method, 'url': url, 'headers': headers,
                       'data': data})
            try:
                response = session.request(method, url, data=data)
            except requests.ConnectionError as e:
                raise exceptions.ConnectionError(url=url, error=e)

            exceptions.raise_for_response(method, url, response)
            LOG.debug('HTTP response for %(method)s %(url)s: '
                      'status code: %(code)s',
                      {'method': method, 'url': url,
                       'code': response.status_code})

            return response

    def get(self, path='', data=None, headers=None):
        """HTTP GET method.

        :param path: Optional sub-URI path to the resource.
        :param data: Optional JSON data.
        :param headers: Optional dictionary of headers.
        :returns: The response object from the requests library.
        :raises: ConnectionError
        :raises: HTTPError
        """
        return self._op('GET', path, data, headers)

    def post(self, path='', data=None, headers=None):
        """HTTP POST method.

        :param path: Optional sub-URI path to the resource.
        :param data: Optional JSON data.
        :param headers: Optional dictionary of headers.
        :returns: The response object from the requests library.
        :raises: ConnectionError
        :raises: HTTPError
        """
        return self._op('POST', path, data, headers)

    def patch(self, path='', data=None, headers=None):
        """HTTP PATCH method.

        :param path: Optional sub-URI path to the resource.
        :param data: Optional JSON data.
        :param headers: Optional dictionary of headers.
        :returns: The response object from the requests library.
        :raises: ConnectionError
        :raises: HTTPError
        """
        return self._op('PATCH', path, data, headers)
