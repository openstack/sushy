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
import os
import sys

import sushy

from sushy.oem.dell import utils

USERNAME = 'root'
PASSWORD = 'calvin'

SERVICE_ROOT = 'http://demo.snmplabs.com:80/redfish/v1'

SYSTEM_ID = '437XR1138R2'

BOOT_DEVICE = sushy.VIRTUAL_MEDIA_CD
BOOT_MODE = sushy.BOOT_SOURCE_MODE_BIOS

BOOT_IMAGE = 'http://demo.snmplabs.com/mini.iso'

LOG = logging.getLogger(__name__)


def main():
    """Boot Dell node from virtual media device"""

    LOG.setLevel(logging.INFO)
    handler = logging.StreamHandler()
    handler.setLevel(logging.INFO)
    LOG.addHandler(handler)

    authenticator = sushy.auth.BasicAuth(USERNAME, PASSWORD)

    conn = sushy.Sushy(SERVICE_ROOT, verify=False, auth=authenticator)

    LOG.info('connected to %s', SERVICE_ROOT)

    system = conn.get_system(
        os.path.join(SERVICE_ROOT, 'Systems', SYSTEM_ID))

    LOG.info('read system resource %s', system.identity)

    for manager in system.managers:

        LOG.info('trying manager %s', manager.identity)

        for v_media in manager.virtual_media.get_members():
            if BOOT_DEVICE not in v_media.media_types:
                continue

            LOG.info(
                'device %s is present at %s', BOOT_DEVICE, manager.identity)

            try:
                manager_oem = manager.get_oem_extension('Dell')

            except sushy.exceptions.OEMExtensionNotFoundError:
                LOG.info('Dell OEM not found')
                continue

            LOG.info('found Dell OEM extension at %s', manager.identity)

            if v_media.inserted:
                v_media.eject_media()

                LOG.info('ejected virtual media')

            v_media.insert_media(BOOT_IMAGE, inserted=True,
                                 write_protected=True)

            LOG.info('inserted boot image %s into virtual media', BOOT_IMAGE)

            # the caller (e.g. ironic) sets boot mode first, boot device second
            system.set_system_boot_source(
                BOOT_DEVICE, enabled=sushy.BOOT_SOURCE_ENABLED_CONTINUOUS,
                mode=BOOT_MODE)

            # with Dell, patching System tree does not work as expected
            # we need to reboot for the new boot mode to take effect
            utils.reboot_system(system)

            LOG.info('set boot mode to %s', BOOT_MODE)

            manager_oem.set_virtual_boot_device(
                BOOT_DEVICE, persistent=False, manager=manager, system=system)

            LOG.info('set boot device to %s', BOOT_DEVICE)

            # real caller should better not use our way to reboot
            utils.reboot_system(system)

            LOG.info('system rebooted')

            return 0


if __name__ == '__main__':
    sys.exit(main())
