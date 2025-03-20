# Copyright (c) 2020-2021 Dell Inc. or its subsidiaries.
#
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
import secrets

from sushy import exceptions
from sushy.resources import base
from sushy.resources import common

from sushy.oem.dell.resources.manager import constants as mgr_cons

LOG = logging.getLogger(__name__)


class ForceActionField(base.CompositeField):
    target_uri = base.Field('target', required=True)
    allowed_values = base.Field('Force@Redfish.AllowableValues',
                                adapter=list)


class ActionsField(base.CompositeField):
    reset_idrac = ForceActionField('#DelliDRACCardService.iDRACReset')
    get_kvm_session = common.ActionField('#DelliDRACCardService.GetKVMSession')


class DelliDRACCardService(base.ResourceBase):

    _actions = ActionsField('Actions')
    identity = base.Field('Id', required=True)

    def __init__(self, connector, identity, redfish_version=None,
                 registries=None):
        """A class representing a DelliDRACCardService.

        :param connector: A Connector instance
        :param identity: The identity of the DelliDRACCardService resource
        :param redfish_version: The version of Redfish. Used to construct
            the object according to schema of the given version.
        :param registries: Dict of Redfish Message Registry objects to be
            used in any resource that needs registries to parse messages.
        """
        super().__init__(
            connector, identity, redfish_version, registries)

    def get_allowed_reset_idrac_values(self):
        """Get the allowed values for resetting the idrac.

        :returns: A set of allowed values.
        """
        reset_action = self._actions.reset_idrac

        if not reset_action.allowed_values:
            LOG.warning('Could not figure out the allowed values for the '
                        'reset idrac action for %s', self.identity)
            return set(mgr_cons.ResetType)

        return {v for v in mgr_cons.ResetType
                if v.value in reset_action.allowed_values}

    def reset_idrac(self):
        """Reset the iDRAC.

        """
        reset_type = mgr_cons.ResetType.GRACEFUL
        valid_resets = self.get_allowed_reset_idrac_values()
        if reset_type not in valid_resets:
            raise exceptions.InvalidParameterValueError(
                parameter='value', value=reset_type, valid_values=valid_resets)
        target_uri = self._actions.reset_idrac.target_uri
        payload = {"Force": reset_type.value}
        LOG.debug('Resetting the iDRAC %s ...', self.identity)
        self._conn.post(target_uri, data=payload)
        LOG.info('The iDRAC %s is being reset', self.identity)

    def get_kvm_session(self):
        """Get temporary credentials for KVM session

        The TempUsername and TempPassword fields can be used in the following
        url template:
        https://{host}/console?username={}&tempUsername={}&tempPassword={}
        The username is the user used to generate these session-credentials.

        :returns: Dict with the fields TempUsername and TempPassword as strings
                  None, if the API did not return any credentials, but did not
                  raise an error. When and why that should happen is unclear,
                  but specified in the API doc.
        """
        target_uri = self._actions.get_kvm_session.target_uri
        LOG.debug('Getting KVM session from iDRAC %s ...', self.identity)

        # SessionTypeName: A random string value upto 32 bytes.
        name = secrets.token_urlsafe(32)
        data = {"SessionTypeName": name}
        result = self._conn.post(target_uri, data=data)
        if result.status_code in (200, 201):
            return result.json()
        return None
