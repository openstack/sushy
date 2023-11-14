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

# This is referred from Redfish standard schema.
# https://redfish.dmtf.org/schemas/VirtualMedia.v1_2_0.json

from http import client as http_client

from sushy import exceptions
from sushy.resources import base
from sushy.resources.certificateservice import certificate
from sushy.resources import common
from sushy.resources.manager import constants as mgr_cons
from sushy import utils


class ActionsField(base.CompositeField):

    insert_media = common.ActionField("#VirtualMedia.InsertMedia")
    eject_media = common.ActionField("#VirtualMedia.EjectMedia")


class VirtualMedia(base.ResourceBase):

    identity = base.Field('Id', required=True)
    """Virtual Media resource identity string"""

    name = base.Field('Name', required=True)
    """The name of resource"""

    connected_via = base.MappedField('ConnectedVia', mgr_cons.ConnectedVia)
    """Current virtual media connection methods

    Applet: Connected to a client application
    NotConnected: No current connection
    Oem: Connected via an OEM-defined method
    URI: Connected to a URI location
    """

    image = base.Field('Image')
    """A URI providing the location of the selected image"""

    image_name = base.Field('ImageName')
    """The image name"""

    inserted = base.Field('Inserted')
    """Indicates if virtual media is inserted in the virtual device"""

    media_types = base.MappedListField(
        'MediaTypes', mgr_cons.VirtualMediaType, default=[])
    """List of supported media types as virtual media"""

    status = common.StatusField('Status')
    """The virtual media status"""

    transfer_method = base.MappedField('TransferMethod',
                                       mgr_cons.TransferMethod)
    """The transfer method to use with the Image"""

    user_name = base.Field('UserName')
    """The user name to access the Image parameter-specified URI"""

    verify_certificate = base.Field('VerifyCertificate', adapter=bool)
    """Whether to verify the certificate of the server for the Image"""

    write_protected = base.Field('WriteProtected')
    """Indicates the media is write protected"""

    _actions = ActionsField('Actions')
    """Insert/eject action for virtual media"""

    _certificates_path = base.Field(['Certificates', '@odata.id'])

    def _get_insert_media_uri(self):
        insert_media = self._actions.insert_media if self._actions else None
        use_patch = False
        if not insert_media:
            insert_uri = self.path
            use_patch = self._allow_patch()
            if not use_patch:
                raise exceptions.MissingActionError(
                    action='#VirtualMedia.InsertMedia', resource=self._path)
        else:
            insert_uri = insert_media.target_uri
        return insert_uri, use_patch

    def _get_eject_media_uri(self):
        eject_media = self._actions.eject_media if self._actions else None
        use_patch = False
        if not eject_media:
            eject_uri = self.path
            use_patch = self._allow_patch()
            if not use_patch:
                raise exceptions.MissingActionError(
                    action='#VirtualMedia.EjectMedia', resource=self._path)
        else:
            eject_uri = eject_media.target_uri
        return eject_uri, use_patch

    def is_transfer_protocol_required(self, error=None):
        """Check the response code and body and in case of failure

        Try to determine if it happened due to missing TransferProtocolType.
        """
        if (error.code.endswith('GeneralError')
           and 'TransferProtocolType' in error.detail):
            return True

        return (
            (error.code.endswith(".ActionParameterMissing")
             or error.code.endswith(".PropertyMissing"))
            and "#/TransferProtocolType" in error.related_properties
        )

    def is_transfer_method_required(self, error=None):
        """Check the response code and body and in case of failure

        Try to determine if it happened due to missing TransferMethod
        """
        if (error.code.endswith('GeneralError')
                and 'TransferMethod' in error.detail):
            return True
        return False

    def insert_media(self, image, inserted=True, write_protected=True,
                     username=None, password=None, transfer_method=None):
        """Attach remote media to virtual media

        :param image: a URI providing the location of the selected image
        :param inserted: specify if the image is to be treated as inserted upon
            completion of the action.
        :param write_protected: indicates the media is write protected
        :param username: User name for the image URI.
        :param password: Password for the image URI.
        :param transfer_method: Transfer method (stream or upload) to use
            for the image.
        """
        target_uri, use_patch = self._get_insert_media_uri()
        # NOTE(janders) Inserted and WriteProtected attributes are optional
        # as per Redfish schema 2021.1. However - some BMCs (e.g. Lenovo SD530
        # which is using PATCH method as opposed to InsertMedia action) will
        # not attach vMedia if Inserted is not specified.
        # On the other hand, machines such as SuperMicro X11 will return
        # an error if Inserted or WriteProtected are specified. In order to
        # make both work, we remove Inserted and WriteProtected from payload
        # for BMCs which don't use PATCH if their values are set to defaults
        # as per the spec (True, True). We continue to set Inserted and
        # WriteProtected in payload if PATCH method is used.
        payload = {'Image': image}
        if username is not None:
            payload['UserName'] = username
        if password is not None:
            payload['Password'] = password
        if transfer_method is not None:
            try:
                payload['TransferMethod'] = \
                    mgr_cons.TransferMethod(transfer_method).value
            except ValueError:
                raise exceptions.InvalidParameterValueError(
                    parameter='transfer_method',
                    value=transfer_method,
                    valid_values=', '.join(map(str, mgr_cons.TransferMethod)))

        if use_patch:
            payload['Inserted'] = inserted
            payload['WriteProtected'] = write_protected
            headers = None
            etag = self._get_etag()
            if etag is not None:
                headers = {"If-Match": etag}
            self._conn.patch(target_uri, data=payload, headers=headers)
        else:
            # NOTE(janders) only include Inserted and WriteProtected
            # in request payload if values other than defaults (True,True)
            # are set (fix for SuperMicro X11/X12).
            if not inserted:
                payload['Inserted'] = False
            if not write_protected:
                payload['WriteProtected'] = False
            # NOTE(janders) attempting to detect whether attachment failure is
            # due to absence of TransferProtocolType param and if so adding it
            try:
                self._conn.post(target_uri, data=payload)
            except exceptions.HTTPError as error:
                if self.is_transfer_protocol_required(error):
                    if payload['Image'].startswith('https://'):
                        payload['TransferProtocolType'] = "HTTPS"
                    elif payload['Image'].startswith('http://'):
                        payload['TransferProtocolType'] = "HTTP"

                    # NOTE (iurygregory) we try to handle the case where a
                    # a TransferMethod is also required in the payload.
                    try:
                        self._conn.post(target_uri, data=payload)
                    except exceptions.HTTPError as error2:
                        if self.is_transfer_method_required(error2):
                            payload['TransferMethod'] = "Stream"
                            self._conn.post(target_uri, data=payload)
                        else:
                            raise

                else:
                    raise
        self.invalidate()

    def eject_media(self):
        """Detach remote media from virtual media

        After ejecting media inserted will be False and image_name will be
        empty.
        """
        try:
            target_uri, use_patch = self._get_eject_media_uri()
            if use_patch:
                payload = {
                    "Image": None,
                    "Inserted": False
                }
                headers = None
                etag = self._get_etag()
                if etag is not None:
                    headers = {"If-Match": etag}
                self._conn.patch(target_uri, data=payload, headers=headers)
            else:
                self._conn.post(target_uri)
        except exceptions.HTTPError as response:
            # Some vendors like HPE iLO has this kind of implementation.
            # It needs to pass an empty dict.
            if response.status_code in (
                    http_client.UNSUPPORTED_MEDIA_TYPE,
                    http_client.BAD_REQUEST):
                self._conn.post(target_uri, data={})
        self.invalidate()

    def set_verify_certificate(self, verify_certificate):
        """Enable or disable certificate validation."""
        if not isinstance(verify_certificate, bool):
            raise exceptions.InvalidParameterValueError(
                parameter='verify_certificate', value=verify_certificate,
                valid_values='boolean (True, False)')

        etag = self._get_etag()
        self._conn.patch(self.path,
                         data={'VerifyCertificate': verify_certificate},
                         etag=etag)
        self.invalidate()

    @property
    @utils.cache_it
    def certificates(self):
        """Get the collection of certificates for this device."""
        if not self._certificates_path:
            raise exceptions.MissingAttributeError(
                attribute='Certificates/@odata.id',
                resource=self._path)

        return certificate.CertificateCollection(
            self._conn, self._certificates_path,
            redfish_version=self.redfish_version,
            registries=self.registries, root=self.root)


class VirtualMediaCollection(base.ResourceCollectionBase):
    """A collection of virtual media attached to a Manager"""

    @property
    def _resource_type(self):
        return VirtualMedia
