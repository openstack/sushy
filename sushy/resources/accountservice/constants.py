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

import enum


class LocalAccountAuth(enum.Enum):
    ENABLED = 'Enabled'

    DISABLED = 'Disabled'

    FALLBACK = 'Fallback'

    LOCAL_FIRST = 'LocalFirst'


class AuthenticationType(enum.Enum):
    TOKEN = 'Token'  # noqa: S105

    KERBEROS_KEYTAB = 'KerberosKeytab'

    USERNAME_AND_PASSWORD = 'UsernameAndPassword'  # noqa: S105

    OEM = 'OEM'


class AccountTypes(enum.Enum):
    REDFISH = 'Redfish'

    SNMP = 'SNMP'

    OEM = 'OEM'

    HOST_CONSOLE = 'HostConsole'

    MANAGER_CONSOLE = 'ManagerConsole'

    IPMI = 'IPMI'

    KVMIP = 'KVMIP'

    VIRTUAL_MEDIA = 'VirtualMedia'

    WEB_UI = 'WebUI'
