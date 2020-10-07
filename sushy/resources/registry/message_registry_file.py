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

# This is referred from Redfish standard schema.
# https://redfish.dmtf.org/schemas/v1/MessageRegistryFileCollection.json
# https://redfish.dmtf.org/schemas/v1/MessageRegistryFile.v1_1_0.json

import logging

from sushy.resources import base
from sushy.resources.registry import message_registry

LOG = logging.getLogger(__name__)


class LocationListField(base.ListField):
    """Location for each registry file of languages supported

    There are 3 options where the file can be hosted:

    * locally as a single file,
    * locally as a part of archive (zip or other),
    * publicly on the Internet.
    """

    language = base.Field('Language')
    """File's RFC5646 language code or the string 'default'"""

    uri = base.Field('Uri')
    """Location URI for co-located registry file with the Redfish service"""

    archive_uri = base.Field('ArchiveUri')
    """Location URI for  archive file"""

    archive_file = base.Field('ArchiveFile')
    """File name for registry if using archive_uri"""

    publication_uri = base.Field('PublicationUri')
    """Location URI of publicly available schema"""


class RegistryType(base.ResourceBase):
    _odata_type = base.Field('@odata.type', required=True)


class MessageRegistryFile(base.ResourceBase):

    identity = base.Field('Id', required=True)
    """Identity of Message Registry file resource"""

    description = base.Field('Description')
    """Description of Message Registry file resource"""

    name = base.Field('Name', required=True)
    """Name of Message Registry file resource"""

    languages = base.Field('Languages', required=True)
    """List of RFC 5646 language codes supported by this resource"""

    registry = base.Field('Registry', required=True, default='UNKNOWN.0.0')
    """Prefix for MessageId used for messages from this resource

    This attribute is in form Registry_name.Major_version.Minor_version
    """

    location = LocationListField('Location', required=True)
    """List of locations of Registry files for each supported language"""

    def get_message_registry(self, language, public_connector):
        """Load message registry file depending on its source

        Will try to find `MessageRegistry` based on `odata.type` property and
        provided language. If desired language is not found, will pick a
        registry that has 'default' language.

        :param language: RFC 5646 language code for registry files
        :param public_connector: connector to use when downloading registry
            from the Internet
        """

        # NOTE (etingof): as per RFC5646, languages are case-insensitive
        language = language.lower()

        locations = [
            l for l in self.location if l.language.lower() == language]

        locations += [
            l for l in self.location if l.language.lower() == 'default']

        for location in locations:
            if location.uri:
                args = self._conn,
                kwargs = {
                    'path': location.uri,
                    'reader': None,
                    'redfish_version': self.redfish_version
                }

            elif location.archive_uri:
                args = self._conn,
                kwargs = {
                    'path': location.archive_uri,
                    'reader': base.JsonArchiveReader(location.archive_file),
                    'redfish_version': self.redfish_version
                }

            elif location.publication_uri:
                args = public_connector,
                kwargs = {
                    'path': location.publication_uri,
                    'reader': base.JsonPublicFileReader(),
                    'redfish_version': self.redfish_version
                }

            else:
                LOG.warning('Incomplete location for language %(language)s',
                            {'language': language})
                continue

            try:
                registry = RegistryType(*args, **kwargs)

            except Exception as exc:
                LOG.warning(
                    'Cannot load message registry type from location '
                    '%(location)s: %(error)s', {
                        'location': kwargs['path'],
                        'error': exc})
                continue

            if registry._odata_type.endswith('MessageRegistry'):
                try:
                    return message_registry.MessageRegistry(*args, **kwargs)

                except Exception as exc:
                    LOG.warning(
                        'Cannot load message registry from location '
                        '%(location)s: %(error)s', {
                            'location': kwargs['path'],
                            'error': exc})
                    continue

            LOG.debug('Ignoring unsupported flavor of registry %(registry)s',
                      {'registry': registry._odata_type})
            return

        LOG.warning('No message registry found for %(language)s or '
                    'default', {'language': language})


class MessageRegistryFileCollection(base.ResourceCollectionBase):
    """Collection of Message Registry Files"""

    @property
    def _resource_type(self):
        return MessageRegistryFile
