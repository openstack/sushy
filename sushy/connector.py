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

from http import client as http_client
import logging
import re
import time
from urllib import parse as urlparse

import requests
from urllib3.exceptions import InsecureRequestWarning

from sushy import exceptions
from sushy.taskmonitor import TaskMonitor
from sushy import utils

LOG = logging.getLogger(__name__)


class Connector(object):

    def __init__(
            self, url, username=None, password=None, verify=True,
            response_callback=None, server_side_retries=0,
            server_side_retries_delay=0):
        self._url = url
        self._verify = verify
        self._session = requests.Session()
        self._response_callback = response_callback
        self._auth = None
        self._server_side_retries = server_side_retries
        self._server_side_retries_delay = server_side_retries_delay

        # NOTE(TheJulia): In order to help prevent recursive post operations
        # by allowing us to understand that we should stop authentication.
        self._sessions_uri = None
        # NOTE(etingof): field studies reveal that some BMCs choke at
        # long-running persistent HTTP connections (or TCP connections).
        # By default, we ask HTTP server to shut down HTTP connection we've
        # just used.
        self._session.headers['Connection'] = 'close'
        # NOTE(TheJulia): Depending on the BMC, offering compression as an
        # acceptable response changes the ETag behavior to offering an
        # automatic "weak" ETag response, which is appropriate because the
        # body content *may* not be a byte for byte match given compression.
        # Overall, the value of compression is less than the value of concise
        # interaction with the BMC. Setting to identity basically means
        # "without modification or compression". By default, python-requests
        # indicates responses can be compressed.
        self._session.headers['Accept-Encoding'] = 'identity'

        if username or password:
            LOG.warning('Passing username and password to Connector is '
                        'deprecated. Authentication is passed through '
                        'set_auth now, support for these arguments will '
                        'be removed in the future')
            self.set_http_basic_auth(username, password)

        if not self._verify:
            # As the user specifically needs to opt out of certificate
            # validation the user is aware of the security implications
            # and does not need to be overwhelmed by the urllib3 warnings
            requests.packages.urllib3.disable_warnings(
                category=InsecureRequestWarning)

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

    def check_retry_on_exception(self, exception_msg):
        """Checks whether retry on exception is required."""
        retry = False
        exc_str = str(exception_msg)
        if 'SYS518' in exc_str:
            LOG.debug('iDRAC is not yet ready after previous operation. '
                      'Error: %(err)s', {'err': exc_str})
            retry = True
        elif 'iLO.2.15.InvalidOperationForSystemState' in exc_str:
            LOG.debug('iLO is not ready after previous operation. '
                      'Error: %(error)s', {'err': exc_str})
            retry = True
        return retry

    def _op(self, method, path='', data=None, headers=None, blocking=False,
            timeout=60, server_side_retries_left=None,
            **extra_session_req_kwargs):
        """Generic RESTful request handler.

        :param method: The HTTP method to be used, e.g: GET, POST,
            PUT, PATCH, etc...
        :param path: The sub-URI or absolute URL path to the resource.
        :param data: Optional JSON data.
        :param headers: Optional dictionary of headers.
        :param blocking: Whether to block for asynchronous operations.
        :param timeout: Max time in seconds to wait for blocking async call or
                        for requests library to connect and read. If a custom
                        timeout for requests is provided in
                        extra_session_req_kwargs, it will be used instead for
                        those calls.
        :param server_side_retries_left: Remaining retries. If not provided
            will use limit provided by instance's server_side_retries
        :param extra_session_req_kwargs: Optional keyword argument to pass
         requests library arguments which would pass on to requests session
         object.
        :returns: The response object from the requests library.
        :raises: ConnectionError
        :raises: HTTPError
        """
        if server_side_retries_left is None:
            server_side_retries_left = self._server_side_retries

        url = path if urlparse.urlparse(path).netloc else urlparse.urljoin(
            self._url, path)
        headers = headers or {}
        lc_headers = [k.lower() for k in headers]
        if data is not None and 'content-type' not in lc_headers:
            headers['Content-Type'] = 'application/json'
        if 'odata-version' not in lc_headers:
            headers['OData-Version'] = '4.0'
        # TODO(lucasagomes): We should mask the data to remove sensitive
        # information
        LOG.debug('HTTP request: %(method)s %(url)s; headers: %(headers)s; '
                  'body: %(data)s; blocking: %(blocking)s; timeout: '
                  '%(timeout)s; session arguments: %(session)s;',
                  {'method': method, 'url': url,
                   'headers': utils.sanitize(headers),
                   'data': utils.sanitize(data),
                   'blocking': blocking, 'timeout': timeout,
                   'session': extra_session_req_kwargs})
        try:
            response = self._session.request(method, url, json=data,
                                             headers=headers,
                                             verify=self._verify,
                                             timeout=timeout,
                                             **extra_session_req_kwargs)
        except requests.exceptions.RequestException as e:
            # Capture any general exception by looking for the parent
            # class of exceptions in the requests library.
            # Specifically this will cover cases such as transport
            # failures, connection timeouts, and encoding errors.
            # Raising this as sushy ConnectionError allows users to
            # understand something bad has happened, and to
            # allow them to respond accordingly.
            raise exceptions.ConnectionError(url=url, error=e)

        if self._response_callback:
            self._response_callback(response)

        # If we received an AccessError, and we
        # previously established a redfish session
        # there is a chance that the session has timed-out.
        # Attempt to re-establish a session.
        try:
            exceptions.raise_for_response(method, url, response)
        except exceptions.AccessError as e:
            if (method == 'POST'
                    and self._sessions_uri is not None
                    and self._sessions_uri in url):
                LOG.error('Authentication to the session service failed. '
                          'Please check credentials and try again.')
                raise
            if self._auth is not None:
                # self._session.auth value is only set when basic auth is used
                if self._session.auth is not None:
                    LOG.warning('We have encountered an AccessError when '
                                'using \'basic\' authentication. %(err)s',
                                {'err': str(e)})
                    # NOTE(TheJulia): There is no way to recover Basic auth,
                    # as we need the client to be re-launched with new
                    # credentials.
                    raise
                try:
                    if self._auth.can_refresh_session():
                        self._auth.refresh_session()
                    else:
                        LOG.warning('Session authentication appears to have '
                                    'been lost at some point in time. '
                                    'Connectivity may have been lost during '
                                    'a prior session refresh. Attempting to '
                                    're-authenticate.')
                        self._auth.authenticate()
                except exceptions.AccessError as refresh_exc:
                    LOG.error("A failure occured while attempting to refresh "
                              "the session. Error: %s", refresh_exc.message)
                    raise
                LOG.debug("Authentication refreshed successfully, "
                          "retrying the call.")
                try:
                    response = self._session.request(
                        method, url, json=data,
                        headers=headers,
                        verify=self._verify,
                        timeout=timeout,
                        **extra_session_req_kwargs)
                except exceptions.HTTPError as retry_exc:
                    LOG.error("Failure occured while attempting to retry "
                              "request after refreshing the session. Error: "
                              "%s", retry_exc.message)
                    raise
            else:
                if method == 'GET' and url.endswith('SessionService'):
                    LOG.debug('HTTP GET of SessionService failed %s, '
                              'this is expected prior to authentication',
                              e.message)
                else:
                    LOG.error("Authentication error detected. Cannot proceed: "
                              "%s", e.message)
                raise
        except exceptions.ServerSideError as e:
            if ((method.lower() == 'get'
                or self.check_retry_on_exception(e.message))
                    and server_side_retries_left > 0):
                LOG.warning('Got server side error %s in response to a '
                            'request, retrying after %d seconds. Retries '
                            'left %d.',
                            e, self._server_side_retries_delay,
                            server_side_retries_left)
                time.sleep(self._server_side_retries_delay)
                server_side_retries_left -= 1
                return self._op(
                    method, path, data=data, headers=headers,
                    blocking=blocking, timeout=timeout,
                    server_side_retries_left=server_side_retries_left,
                    **extra_session_req_kwargs)
            else:
                raise
        except exceptions.BadRequestError as e:
            if (method.lower() != 'get'
                    and self.check_retry_on_exception(e.message)
                    and server_side_retries_left > 0):
                LOG.warning('Server has indicated a BadRequest for %s but '
                            'the response payload is a known retriable '
                            'condition and we will retry in %d seconds. '
                            'Retries left  %d.',
                            e, self._server_side_retries_delay,
                            server_side_retries_left)
                time.sleep(self._server_side_retries_delay)
                server_side_retries_left -= 1
                return self._op(
                    method, path, data=data, headers=headers,
                    blocking=blocking, timeout=timeout,
                    server_side_retries_left=server_side_retries_left,
                    **extra_session_req_kwargs)
            else:
                raise
        if blocking and response.status_code == 202:
            if not response.headers.get('Location'):
                m = ('HTTP response for %(method)s request to %(url)s '
                     'returned status 202, but no Location header'
                     % {'method': method, 'url': url})
                raise exceptions.ConnectionError(url=url, error=m)

            mon = TaskMonitor.from_response(self, response, path)
            mon.wait(timeout)
            response = mon.response
            exceptions.raise_for_response(method, url, response)

        LOG.debug('HTTP response for %(method)s %(url)s: '
                  'status code: %(code)s',
                  {'method': method, 'url': url,
                   'code': response.status_code})

        return response

    def get(self, path='', data=None, headers=None, blocking=False,
            timeout=60, **extra_session_req_kwargs):
        """HTTP GET method.

        :param path: Optional sub-URI path to the resource.
        :param data: Optional JSON data.
        :param headers: Optional dictionary of headers.
        :param blocking: Whether to block for asynchronous operations.
        :param timeout: Max time in seconds to wait for blocking async call.
        :param extra_session_req_kwargs: Optional keyword argument to pass
         requests library arguments which would pass on to requests session
         object.
        :returns: The response object from the requests library.
        :raises: ConnectionError
        :raises: HTTPError
        """
        return self._op('GET', path, data=data, headers=headers,
                        blocking=blocking, timeout=timeout,
                        **extra_session_req_kwargs)

    def post(self, path='', data=None, headers=None, blocking=False,
             timeout=60, **extra_session_req_kwargs):
        """HTTP POST method.

        :param path: Optional sub-URI path to the resource.
        :param data: Optional JSON data.
        :param headers: Optional dictionary of headers.
        :param blocking: Whether to block for asynchronous operations.
        :param timeout: Max time in seconds to wait for blocking async call.
        :param extra_session_req_kwargs: Optional keyword argument to pass
         requests library arguments which would pass on to requests session
         object.
        :returns: The response object from the requests library.
        :raises: ConnectionError
        :raises: HTTPError
        """
        return self._op('POST', path, data=data, headers=headers,
                        blocking=blocking, timeout=timeout,
                        **extra_session_req_kwargs)

    def _etag_handler(self, path='', data=None, headers=None, etag=None,
                      blocking=False, timeout=60, **extra_session_req_kwargs):
        """eTag handler containing workarounds for PATCH requests with eTags.

        :param path: Optional sub-URI path to the resource.
        :param data: Optional JSON data.
        :param headers: Optional dictionary of headers.
        :param etag: eTag string.
        :param blocking: Whether to block for asynchronous operations.
        :param timeout: Max time in seconds to wait for blocking async call.
        :param extra_session_req_kwargs: Optional keyword argument to pass
         requests library arguments which would pass on to requests session
         object.
        :returns: The response object from the requests library.
        :raises: ConnectionError
        :raises: HTTPError
        """
        if etag is not None:
            if not headers:
                headers = {}
            headers['If-Match'] = etag
        try:
            response = self._op('PATCH', path, data=data,
                                headers=headers,
                                blocking=blocking, timeout=timeout,
                                **extra_session_req_kwargs)
        except exceptions.HTTPError as resp:
            LOG.warning("Initial request with eTag failed: %s",
                        resp)
            if resp.status_code == http_client.PRECONDITION_FAILED:
                # NOTE(janders) if there was no eTag provided AND the response
                # is HTTP 412 Precondition Failed, raise the exception
                if not etag:
                    raise
                # checking for weak eTag
                pattern = re.compile(r'^(W\/)("\w*")$')
                match = pattern.match(etag)
                if match:
                    LOG.info("Weak eTag provided with original request to "
                             "%s. Attempting to conversion to strong eTag "
                             "and re-trying.", path)
                    # trying weak eTag converted to strong
                    headers['If-Match'] = match.group(2)
                    try:
                        response = self._op('PATCH', path, data=data,
                                            headers=headers,
                                            blocking=blocking,
                                            timeout=timeout,
                                            **extra_session_req_kwargs)
                    except exceptions.HTTPError as resp:
                        if (resp.status_code == http_client.
                           PRECONDITION_FAILED):
                            LOG.warning("Request to %s with weak eTag "
                                        "converted to strong eTag also "
                                        "failed. Making the final attempt "
                                        "with no eTag specified.", path)
                        response = None
                    if response:
                        return response
                else:
                    # eTag is strong, if it failed the only other thing
                    # to try is removing it entirely
                    # info
                    LOG.warning("Strong eTag provided - retrying request to "
                                "%s with eTag removed.", path)
                del headers['If-Match']
                try:
                    response = self._op('PATCH', path, data=data,
                                        headers=headers,
                                        blocking=blocking, timeout=timeout,
                                        **extra_session_req_kwargs)
                except exceptions.HTTPError as resp:
                    LOG.error("Final re-try with eTag removed has failed, "
                              "raising exception %s", resp)
                    raise
            else:
                raise
        return response

    def patch(self, path='', data=None, headers=None, etag=None,
              blocking=False, timeout=60, **extra_session_req_kwargs):
        """HTTP PATCH method.

        :param path: Optional sub-URI path to the resource.
        :param data: Optional JSON data.
        :param headers: Optional dictionary of headers.
        :param etag: Optional eTag string.
        :param blocking: Whether to block for asynchronous operations.
        :param timeout: Max time in seconds to wait for blocking async call.
        :param extra_session_req_kwargs: Optional keyword argument to pass
         requests library arguments which would pass on to requests session
         object.
        :returns: The response object from the requests library.
        :raises: ConnectionError
        :raises: HTTPError
        """
        return self._etag_handler(path, data,
                                  headers, etag,
                                  blocking, timeout,
                                  **extra_session_req_kwargs)

    def put(self, path='', data=None, headers=None, blocking=False,
            timeout=60, **extra_session_req_kwargs):
        """HTTP PUT method.

        :param path: Optional sub-URI path to the resource.
        :param data: Optional JSON data.
        :param headers: Optional dictionary of headers.
        :param blocking: Whether to block for asynchronous operations.
        :param timeout: Max time in seconds to wait for blocking async call.
        :param extra_session_req_kwargs: Optional keyword argument to pass
         requests library arguments which would pass on to requests session
         object.
        :returns: The response object from the requests library.
        :raises: ConnectionError
        :raises: HTTPError
        """
        return self._op('PUT', path, data=data, headers=headers,
                        blocking=blocking, timeout=timeout,
                        **extra_session_req_kwargs)

    def delete(self, path='', data=None, headers=None, blocking=False,
               timeout=60, **extra_session_req_kwargs):
        """HTTP DELETE method.

        :param path: Optional sub-URI path to the resource.
        :param data: Optional JSON data.
        :param headers: Optional dictionary of headers.
        :param blocking: Whether to block for asynchronous operations.
        :param timeout: Max time in seconds to wait for blocking async call.
        :param extra_session_req_kwargs: Optional keyword argument to pass
         requests library arguments which would pass on to requests session
         object.
        :returns: The response object from the requests library.
        :raises: ConnectionError
        :raises: HTTPError
        """
        return self._op('DELETE', path, data=data, headers=headers,
                        blocking=blocking, timeout=timeout,
                        **extra_session_req_kwargs)

    def __enter__(self):
        return self

    def __exit__(self, *_args):
        self.close()
