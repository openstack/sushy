# -*- coding: utf-8 -*-

# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

import logging

import pbr.version

from sushy.main import Sushy
from sushy.resources.certificateservice.constants import * # noqa
from sushy.resources.chassis.constants import *  # noqa
from sushy.resources.constants import *  # noqa
from sushy.resources.eventservice.constants import * # noqa
from sushy.resources.fabric.constants import *  # noqa
from sushy.resources.ipaddresses import *  # noqa
from sushy.resources.manager.constants import *  # noqa
from sushy.resources.registry.constants import *  # noqa
from sushy.resources.system.constants import *  # noqa
from sushy.resources.system.network.constants import *  # noqa
from sushy.resources.system.storage.constants import *  # noqa
from sushy.resources.updateservice.constants import *  # noqa
from sushy.resources.taskservice.constants import *  # noqa

__all__ = ('Sushy',)
__version__ = pbr.version.VersionInfo(
    'sushy').version_string()

# Set the default handler to avoid "No handler found" warnings. See:
# https://docs.python.org/3/howto/logging.html#library-config
logging.getLogger(__name__).addHandler(logging.NullHandler())
