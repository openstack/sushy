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


class MessageRegistryFile(base.ResourceBase):

    identity = base.Field('Id', required=True)
    """Identity of Message Registry file resource"""

    description = base.Field('Description')
    """Description of Message Registry file resource"""

    name = base.Field('Name', required=True)
    """Name of Message Registry file resource"""

    languages = base.Field('Languages', required=True)
    """List of RFC 5646 language codes supported by this resource"""

    registry = base.Field('Registry', required=True)
    """Prefix for MessageId used for messages from this resource

    This attribute is in form Registry_name.Major_version.Minor_version
    """

    location = LocationListField('Location', required=True)
    """List of locations of Registry files for each supported language"""

    def get_message_registry(self, language, public_connector):
        """Load message registry file depending on its source

        Will try to find a registry based on provided language, if not found
        then will use a registry that has 'default' language.

        :param language: RFC 5646 language code for registry files
        :param public_connector: connector to use when downloading registry
            from the Internet
        """

        location = next((l for l in self.location if l.language == language),
                        [d for d in self.location if d.language == 'default']
                        [0])

        if location.uri:
            return message_registry.MessageRegistry(
                self._conn, path=location.uri,
                redfish_version=self.redfish_version)
        elif location.archive_uri:
            return message_registry.MessageRegistry(
                self._conn, path=location.archive_uri,
                redfish_version=self.redfish_version,
                reader=base.JsonArchiveReader(location.archive_file))
        elif location.publication_uri:
            return message_registry.MessageRegistry(
                public_connector,
                path=location.publication_uri,
                redfish_version=self.redfish_version,
                reader=base.JsonPublicFileReader())
        else:
            LOG.warning('No location defined for language %(language)s',
                        {'language': language})


class MessageRegistryFileCollection(base.ResourceCollectionBase):
    """Collection of Message Registry Files"""

    @property
    def _resource_type(self):
        return MessageRegistryFile
