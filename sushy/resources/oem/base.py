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

import logging

from sushy.resources import base


LOG = logging.getLogger(__name__)


class OEMResourceBase(base.ResourceBase):

    def __init__(self,
                 connector,
                 path='',
                 redfish_version=None,
                 registries=None,
                 reader=None):
        """Class representing an OEM vendor extension

        :param connector: A Connector instance
        :param path: sub-URI path to the resource.
        :param redfish_version: The version of Redfish. Used to construct
            the object according to schema of the given version.
        :param registries: Dict of Redfish Message Registry objects to be
            used in any resource that needs registries to parse messages
        """
        self._parent_resource = None
        self._vendor_id = None

        super(OEMResourceBase, self).__init__(
            connector, path, redfish_version, registries, reader)

    def set_parent_resource(self, parent_resource, vendor_id):
        self._parent_resource = parent_resource
        self._vendor_id = vendor_id
        # NOTE(etingof): this is required to pull OEM subtree
        self.invalidate(force_refresh=True)
        return self

    def _parse_attributes(self, json_doc):
        """Parse the attributes of a resource.

        Parsed JSON fields are set to `self` as declared in the class.

        :param json_doc: parsed JSON document in form of Python types
        """
        oem_json = json_doc.get(
            'Oem', {}).get(self._vendor_id, {})

        # NOTE(etingof): temporary copy Actions into Oem subtree for parsing
        # all fields at once

        oem_json = oem_json.copy()

        oem_actions_json = {
            'Actions': json_doc.get(
                'Actions', {}).get('Oem', {})
        }

        oem_json.update(oem_actions_json)

        super(OEMResourceBase, self)._parse_attributes(oem_json)
