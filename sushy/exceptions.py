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


LOG = logging.getLogger(__name__)


class SushyError(Exception):
    """Basic exception for errors raised by Sushy"""

    message = None

    def __init__(self, message=None, **kwargs):
        if message is not None:
            self.message = message
        if self.message and kwargs:
            self.message = self.message % kwargs

        super(SushyError, self).__init__(self.message)


class ConnectionError(SushyError):
    message = 'Unable to connect to %(url)s. Error: %(error)s'


class MissingAttributeError(SushyError):
    message = ('The attribute %(attribute)s is missing from the '
               'resource %(resource)s')


class MalformedAttributeError(SushyError):
    message = ('The attribute %(attribute)s is malformed in the '
               'resource %(resource)s: %(error)s')


class MissingActionError(SushyError):
    message = ('The action %(action)s is missing from the '
               'resource %(resource)s')


class InvalidParameterValueError(SushyError):
    message = ('The parameter "%(parameter)s" value "%(value)s" is invalid. '
               'Valid values are: %(valid_values)s')


class ArchiveParsingError(SushyError):
    message = 'Failed parsing archive "%(path)s": %(error)s'


class UnknownDefaultError(SushyError):
    message = 'Failed at determining default for "%(entity)s": %(error)s'


class ExtensionError(SushyError):
    message = ('Sushy Extension Error: %(error)s')


class OEMExtensionNotFoundError(SushyError):
    message = 'No %(resource)s OEM extension found by name "%(name)s".'


class MissingHeaderError(SushyError):
    message = 'Response to %(target_uri)s did not contain a %(header)s header'


class HTTPError(SushyError):
    """Basic exception for HTTP errors"""

    status_code = None
    """HTTP status code."""

    body = None
    """Error JSON body, if present."""

    code = 'Base.1.0.GeneralError'
    """Error code defined in the Redfish specification, if present."""

    detail = None
    """Error message defined in the Redfish specification, if present."""

    message = ('HTTP %(method)s %(url)s returned code %(code)s. %(error)s '
               'Extended information: %(ext_info)s')

    def __init__(self, method, url, response):
        self.status_code = response.status_code
        try:
            body = response.json()
        except ValueError:
            LOG.warning('Error response from %(method)s %(url)s '
                        'with status code %(code)s has no JSON body',
                        {'method': method, 'url': url, 'code':
                         self.status_code})
            error = 'unknown error'
            ext_info = 'none'
        else:
            self.body = body.get('error', {})
            self.code = self.body.get('code', 'Base.1.0.GeneralError')
            self.detail = self.body.get('message')
            ext_info = self.body.get('@Message.ExtendedInfo', [{}])
            index = self._get_most_severe_msg_index(ext_info)
            self.detail = ext_info[index].get('Message', self.detail)
            error = '%s: %s' % (self.code, self.detail or 'unknown error.')

        kwargs = {'method': method, 'url': url, 'code': self.status_code,
                  'error': error, 'ext_info': ext_info}
        LOG.debug('HTTP response for %(method)s %(url)s: '
                  'status code: %(code)s, error: %(error)s, '
                  'extended: %(ext_info)s', kwargs)
        super(HTTPError, self).__init__(**kwargs)

    @staticmethod
    def _get_most_severe_msg_index(extended_info):
        if len(extended_info) > 0:
            for sev in ['Critical', 'Warning']:
                for i, m in enumerate(extended_info):
                    if m.get('Severity') == sev:
                        return i
        return 0


class BadRequestError(HTTPError):
    pass


class ResourceNotFoundError(HTTPError):
    # Overwrite the complex generic message with a simpler one.
    message = 'Resource %(url)s not found'


class ServerSideError(HTTPError):
    pass


class AccessError(HTTPError):
    pass


class MissingXAuthToken(HTTPError):
    message = ('No X-Auth-Token returned from remote host when '
               'attempting to establish a session. Error: %(error)s')


def raise_for_response(method, url, response):
    """Raise a correct error class, if needed."""
    if response.status_code < http_client.BAD_REQUEST:
        return
    elif response.status_code == http_client.NOT_FOUND:
        raise ResourceNotFoundError(method, url, response)
    elif response.status_code == http_client.BAD_REQUEST:
        raise BadRequestError(method, url, response)
    elif response.status_code in (http_client.UNAUTHORIZED,
                                  http_client.FORBIDDEN):
        raise AccessError(method, url, response)
    elif response.status_code >= http_client.INTERNAL_SERVER_ERROR:
        raise ServerSideError(method, url, response)
    else:
        raise HTTPError(method, url, response)
