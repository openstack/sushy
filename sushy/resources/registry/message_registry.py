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
# https://redfish.dmtf.org/schemas/v1/MessageRegistry.v1_1_1.json

import logging

from sushy.resources import base
from sushy.resources import constants as res_cons
from sushy.resources import mappings as res_maps

LOG = logging.getLogger(__name__)


class MessageDictionaryField(base.DictionaryField):

    description = base.Field('Description', required=True, default='')
    """Indicates how and when the message is returned by the Redfish service"""

    message = base.Field('Message', required=True)
    """Template text of the message

    Template can include placeholders for message arguments in form
    %<integer> where <integer> denotes a position passed from MessageArgs.
    """

    number_of_args = base.Field('NumberOfArgs', required=True)
    """Number of arguments to be expected to be passed in as MessageArgs
    for this message
    """

    param_types = base.Field('ParamTypes',
                             adapter=lambda x:
                                 [res_maps.PARAMTYPE_VALUE_MAP[v.lower()]
                                  for v in x])
    """Mapped MessageArg types, in order, for the message"""

    resolution = base.Field('Resolution', required=True)
    """Suggestions on how to resolve the situation that caused the error"""

    severity = base.MappedField('Severity',
                                res_maps.SEVERITY_VALUE_MAP,
                                required=True,
                                default=res_cons.SEVERITY_WARNING)
    """Mapped severity of the message"""


class MessageRegistry(base.ResourceBase):

    identity = base.Field('Id', required=True)
    """The Message registry identity string"""

    name = base.Field('Name', required=True)
    """The name of the message registry"""

    description = base.Field('Description')
    """Human-readable description of the message registry"""

    language = base.Field('Language', required=True)
    """RFC 5646 compliant language code for the registry"""

    owning_entity = base.Field('OwningEntity', required=True)
    """Organization or company that publishes this registry"""

    registry_prefix = base.Field('RegistryPrefix', required=True)
    """Prefix used in messageIDs which uniquely identifies all of
    the messages in this registry as belonging to this registry
    """

    registry_version = base.Field('RegistryVersion', required=True)
    """Message registry version which is used in the middle portion
    of a messageID
    """

    messages = MessageDictionaryField('Messages')
    """List of messages in this registry"""


def parse_message(message_registries, message_field):
    """Using message registries parse the message and substitute any parms

    :param message_registries: dict of Message Registries
    :param message_field: settings.MessageListField to parse

    :returns: parsed settings.MessageListField with missing attributes filled
    """

    reg_msg = None
    if '.' in message_field.message_id:
        registry, msg_key = message_field.message_id.rsplit('.', 1)

        if (registry in message_registries and msg_key
                in message_registries[registry].messages):
            reg_msg = message_registries[registry].messages[msg_key]
    else:
        # Some firmware only reports the MessageKey and no RegistryName.
        # Fall back to the MessageRegistryFile with Id of Messages next, and
        # BaseMessages as a last resort
        registry = 'unknown'
        msg_key = message_field.message_id

        mrf_ids = ['Messages', 'BaseMessages']
        for mrf_id in mrf_ids:
            if (mrf_id in message_registries and msg_key in
                    message_registries[mrf_id].messages):
                reg_msg = message_registries[mrf_id].messages[msg_key]
                break

    if not reg_msg:
        LOG.warning(
            'Unable to find message for registry %(registry), '
            'message ID %(msg_key)', {
                'registry': registry,
                'msg_key': msg_key})
        if message_field.message is None:
            message_field.message = 'unknown'
        return message_field

    msg = reg_msg.message
    for i in range(1, reg_msg.number_of_args + 1):
        if i <= len(message_field.message_args):
            msg = msg.replace('%%%i' % i,
                              str(message_field.message_args[i - 1]))
        else:
            msg = msg.replace('%%%i' % i, 'unknown')

    message_field.message = msg
    if not message_field.severity:
        message_field.severity = reg_msg.severity
    if not message_field.resolution:
        message_field.resolution = reg_msg.resolution

    return message_field
