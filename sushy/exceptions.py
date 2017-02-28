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


class SushyError(Exception):
    """Basic exception for errors raised by Sushy"""

    message = None

    def __init__(self, **kwargs):
        if self.message and kwargs:
            self.message = self.message % kwargs

        super(SushyError, self).__init__(self.message)


class ConnectionError(SushyError):
    message = 'Unable to connect to %(url)s. Error: %(error)s'


class MissingAttributeError(SushyError):
    message = ('The attribute %(attribute)s is missing from the '
               'resource %(resource)s')


class MissingActionError(SushyError):
    message = ('The action %(action)s is missing from the '
               'resource %(resource)s')


class InvalidParameterValueError(SushyError):
    message = ('The parameter "%(parameter)s" value "%(value)s" is invalid. '
               'Valid values are: %(valid_values)s')


class HTTPError(SushyError):
    """Basic exception for HTTP errors"""

    status_code = None
    message = ('Error issuing a %(method)s request at %(url)s. '
               'Error: %(error)s')

    def __init__(self, status_code=None, **kwargs):
        super(HTTPError, self).__init__(**kwargs)
        if status_code is not None:
            self.status_code = status_code


class ResourceNotFoundError(HTTPError):
    status_code = 404
    message = 'Resource %(resource)s not found'
