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
from sushy.resources import common
from sushy.resources.manager import mappings as mgr_maps


class ActionsField(base.CompositeField):

    insert_media = common.ActionField("#VirtualMedia.InsertMedia")
    eject_media = common.ActionField("#VirtualMedia.EjectMedia")


class VirtualMedia(base.ResourceBase):

    identity = base.Field('Id', required=True)
    """Virtual Media resource identity string"""

    name = base.Field('Name', required=True)
    """The name of resource"""

    image = base.Field('Image')
    """A URI providing the location of the selected image"""

    image_name = base.Field('ImageName')
    """The image name"""

    inserted = base.Field('Inserted')
    """Indicates if virtual media is inserted in the virtual device"""

    write_protected = base.Field('WriteProtected')
    """Indicates the media is write protected"""

    media_types = base.Field(
        'MediaTypes', adapter=(
            lambda x: [mgr_maps.MEDIA_TYPE_VALUE_MAP[v] for v in x
                       if v in mgr_maps.MEDIA_TYPE_VALUE_MAP]),
        default=[])
    """List of supported media types as virtual media"""

    connected_via = base.MappedField('ConnectedVia',
                                     mgr_maps.CONNECTED_VIA_VALUE_MAP)
    """Current virtual media connection methods

    Applet: Connected to a client application
    NotConnected: No current connection
    Oem: Connected via an OEM-defined method
    URI: Connected to a URI location
    """

    _actions = ActionsField('Actions')
    """Insert/eject action for virtual media"""

    def _get_insert_media_element(self):
        insert_media = self._actions.insert_media
        if not insert_media:
            raise exceptions.MissingActionError(
                action='#VirtualMedia.InsertMedia', resource=self._path)
        return insert_media

    def _get_eject_media_element(self):
        eject_media = self._actions.eject_media
        if not eject_media:
            raise exceptions.MissingActionError(
                action='#VirtualMedia.EjectMedia', resource=self._path)
        return eject_media

    def insert_media(self, image, inserted=True, write_protected=False):
        """Attach remote media to virtual media

        :param image: a URI providing the location of the selected image
        :param inserted: specify if the image is to be treated as inserted upon
            completion of the action.
        :param write_protected: indicates the media is write protected
        """
        target_uri = self._get_insert_media_element().target_uri
        self._conn.post(target_uri, data={"Image": image, "Inserted": inserted,
                                          "WriteProtected": write_protected})
        self.invalidate()

    def eject_media(self):
        """Detach remote media from virtual media

        After ejecting media inserted will be False and image_name will be
        empty.
        """
        try:
            target_uri = self._get_eject_media_element().target_uri
            self._conn.post(target_uri)
        except exceptions.HTTPError as response:
            # Some vendors like HPE iLO has this kind of implementation.
            # It needs to pass an empty dict.
            if response.status_code in (
                    http_client.UNSUPPORTED_MEDIA_TYPE,
                    http_client.BAD_REQUEST):
                self._conn.post(target_uri, data={})
        self.invalidate()


class VirtualMediaCollection(base.ResourceCollectionBase):
    """A collection of virtual media attached to a Manager"""

    @property
    def _resource_type(self):
        return VirtualMedia
