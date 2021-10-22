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

from sushy import exceptions
from sushy.resources import base
from sushy.resources.certificateservice import certificate
from sushy.resources.certificateservice import constants
from sushy.resources import common
from sushy import utils


class ActionsField(base.CompositeField):
    generate_csr = common.ActionField('#CertificateService.GenerateCSR')
    replace_certificate = common.ActionField(
        '#CertificateService.ReplaceCertificate')


class CertificateLocations(base.ResourceLinksBase):

    name = base.Field('Name')
    """The name of the collection"""

    _resource_type = certificate.Certificate

    @property
    def members_identities(self):
        return utils.get_sub_resource_path_by(
            self, ["Links", "Certificates"], is_collection=True)


class CertificateService(base.ResourceBase):

    identity = base.Field('Id', required=True)
    """The certificate service identity"""

    name = base.Field('Name')
    """The certificate service name"""

    _actions = ActionsField('Actions')

    _certificate_locations_path = base.Field(
        ['CertificateLocations', '@odata.id'])

    def _get_replace_certificate_action_element(self):
        reset_action = self._actions.replace_certificate
        if not reset_action:
            raise exceptions.MissingActionError(
                action='#CertificateService.ReplaceCertificate',
                resource=self._path)
        return reset_action

    @property
    @utils.cache_it
    def certificate_locations(self):
        """Property to reference certificate locations instance"""
        if not self._certificate_locations_path:
            raise exceptions.MissingAttributeError(
                attribute='CertificateLocations/@odata.id',
                resource=self._path)

        return CertificateLocations(
            self._conn,
            self._certificate_locations_path,
            redfish_version=self.redfish_version,
            registries=self.registries, root=self.root)

    def replace_certificate(self, certificate_uri, certificate_string,
                            certificate_type):
        """Replace an existing certificate in the service.

        :param certificate_uri: URI of an existing certificate.
        :param certificate_string: the contents of the new certificate.
        :param certificate_type: the type of the new certificate, one of
            :py:class:`sushy.CertificateType`.
        """
        try:
            certificate_type = constants.CertificateType(certificate_type)
        except ValueError:
            raise exceptions.InvalidParameterValueError(
                parameter='certificate_type',
                value=certificate_type,
                valid_values=list(constants.CertificateType))

        target_uri = self._get_replace_certificate_action_element().target_uri

        body = {'CertificateUri': certificate_uri,
                'CertificateString': certificate_string,
                'CertificateType': certificate_type.value}
        self._conn.post(target_uri, data=body)
