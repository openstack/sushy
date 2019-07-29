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

import logging

import requests
from six.moves.urllib import parse

from sushy import exceptions

LOG = logging.getLogger(__name__)


class Connector(object):

    def __init__(self, url, username=None, password=None, verify=True):
        self._url = url
        self._verify = verify
        self._session = requests.Session()
        self._session.verify = self._verify

        # NOTE(etingof): field studies reveal that some BMCs choke at
        # long-running persistent HTTP connections (or TCP connections).
        # By default, we ask HTTP server to shut down HTTP connection we've
        # just used.
        self._session.headers['Connection'] = 'close'

        if username or password:
            LOG.warning('Passing username and password to Connector is '
                        'deprecated. Authentication is passed through '
                        'set_auth now, support for these arguments will '
                        'be removed in the future')
            self.set_http_basic_auth(username, password)

    def set_auth(self, auth):
        """Sets the authentication mechanism for our connector."""
        self._auth = auth

    def set_http_basic_auth(self, username, password):
        """Sets the http basic authentication information."""
        self._session.auth = (username, password)

    def set_http_session_auth(self, session_auth_token):
        """Sets the session authentication information."""
        self._session.auth = None
        self._session.headers.update({'X-Auth-Token': session_auth_token})

    def close(self):
        """Close this connector and the associated HTTP session."""
        self._session.close()

    def _op(self, method, path='', data=None, headers=None,
            **extra_session_req_kwargs):
        """Generic RESTful request handler.

        :param method: The HTTP method to be used, e.g: GET, POST,
            PUT, PATCH, etc...
        :param path: The sub-URI path to the resource.
        :param data: Optional JSON data.
        :param headers: Optional dictionary of headers.
        :param extra_session_req_kwargs: Optional keyword argument to pass
         requests library arguments which would pass on to requests session
         object.
        :returns: The response object from the requests library.
        :raises: ConnectionError
        :raises: HTTPError
        """
        url = parse.urljoin(self._url, path)
        headers = headers or {}
        if not any(k.lower() == 'odata-version' for k in headers):
            headers['OData-Version'] = '4.0'
        # TODO(lucasagomes): We should mask the data to remove sensitive
        # information
        LOG.debug('HTTP request: %(method)s %(url)s; headers: %(headers)s; '
                  'body: %(data)s; session arguments: %(session)s;',
                  {'method': method, 'url': url, 'headers': headers,
                   'data': data, 'session': extra_session_req_kwargs})
        try:
            response = self._session.request(method, url, json=data,
                                             headers=headers,
                                             **extra_session_req_kwargs)
        except requests.ConnectionError as e:
            raise exceptions.ConnectionError(url=url, error=e)
        # If we received an AccessError, and we
        # previously established a redfish session
        # there is a chance that the session has timed-out.
        # Attempt to re-establish a session.
        try:
            exceptions.raise_for_response(method, url, response)
        except exceptions.AccessError:
            if self._auth.can_refresh_session():
                self._auth.refresh_session()
                LOG.debug("Authentication refreshed successfully, "
                          "retrying the call.")
                response = self._session.request(method, url, json=data,
                                                 headers=headers,
                                                 **extra_session_req_kwargs)
            else:
                raise

        LOG.debug('HTTP response for %(method)s %(url)s: '
                  'status code: %(code)s',
                  {'method': method, 'url': url,
                   'code': response.status_code})

        return response

    def get(self, path='', data=None, headers=None,
            **extra_session_req_kwargs):
        """HTTP GET method.

        :param path: Optional sub-URI path to the resource.
        :param data: Optional JSON data.
        :param headers: Optional dictionary of headers.
        :param extra_session_req_kwargs: Optional keyword argument to pass
         requests library arguments which would pass on to requests session
         object.
        :returns: The response object from the requests library.
        :raises: ConnectionError
        :raises: HTTPError
        """
        return self._op('GET', path, data=data, headers=headers,
                        **extra_session_req_kwargs)

    def post(self, path='', data=None, headers=None,
             **extra_session_req_kwargs):
        """HTTP POST method.

        :param path: Optional sub-URI path to the resource.
        :param data: Optional JSON data.
        :param headers: Optional dictionary of headers.
        :param extra_session_req_kwargs: Optional keyword argument to pass
         requests library arguments which would pass on to requests session
         object.
        :returns: The response object from the requests library.
        :raises: ConnectionError
        :raises: HTTPError
        """
        return self._op('POST', path, data=data, headers=headers,
                        **extra_session_req_kwargs)

    def patch(self, path='', data=None, headers=None,
              **extra_session_req_kwargs):
        """HTTP PATCH method.

        :param path: Optional sub-URI path to the resource.
        :param data: Optional JSON data.
        :param headers: Optional dictionary of headers.
        :param extra_session_req_kwargs: Optional keyword argument to pass
         requests library arguments which would pass on to requests session
         object.
        :returns: The response object from the requests library.
        :raises: ConnectionError
        :raises: HTTPError
        """
        return self._op('PATCH', path, data=data, headers=headers,
                        **extra_session_req_kwargs)

    def put(self, path='', data=None, headers=None,
            **extra_session_req_kwargs):
        """HTTP PUT method.

        :param path: Optional sub-URI path to the resource.
        :param data: Optional JSON data.
        :param headers: Optional dictionary of headers.
        :param extra_session_req_kwargs: Optional keyword argument to pass
         requests library arguments which would pass on to requests session
         object.
        :returns: The response object from the requests library.
        :raises: ConnectionError
        :raises: HTTPError
        """
        return self._op('PUT', path, data=data, headers=headers,
                        **extra_session_req_kwargs)

    def delete(self, path='', data=None, headers=None,
               **extra_session_req_kwargs):
        """HTTP DELETE method.

        :param path: Optional sub-URI path to the resource.
        :param data: Optional JSON data.
        :param headers: Optional dictionary of headers.
        :param extra_session_req_kwargs: Optional keyword argument to pass
         requests library arguments which would pass on to requests session
         object.
        :returns: The response object from the requests library.
        :raises: ConnectionError
        :raises: HTTPError
        """
        return self._op('DELETE', path, data=data, headers=headers,
                        **extra_session_req_kwargs)

    def __enter__(self):
        return self

    def __exit__(self, *_args):
        self.close()
