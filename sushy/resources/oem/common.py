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

import stevedore

from sushy import exceptions
from sushy import utils


LOG = logging.getLogger(__name__)

_global_extn_mgrs_by_resource = {}


def _raise(m, ep, e):
    raise exceptions.ExtensionError(
        error='Failed to load entry point target: %(error)s' % {'error': e})


def _create_extension_manager(namespace):
    """Create the resource specific ExtensionManager instance.

    Use stevedore to find all vendor extensions of resource from their
    namespace and return the ExtensionManager instance.
    :param namespace: The namespace for the entry points. It maps to a
        specific Sushy resource type.
    :returns: the ExtensionManager instance
    :raises ExtensionError: on resource OEM extension load error.
    """
    # namespace format is:
    # ``sushy.resources.<underscore_joined_resource_name>.oems``
    resource_name = namespace.split('.')[-2]

    extension_manager = (
        stevedore.ExtensionManager(namespace=namespace,
                                   propagate_map_exceptions=True,
                                   on_load_failure_callback=_raise))

    LOG.debug('Resource OEM extensions for "%(resource)s" under namespace '
              '"%(namespace)s":',
              {'resource': resource_name, 'namespace': namespace})
    for extension in extension_manager:
        LOG.debug('Found vendor: %(name)s target: %(target)s',
                  {'name': extension.name,
                   'target': extension.entry_point_target})

    if not extension_manager.names():
        m = (('No extensions found for "%(resource)s" under namespace '
              '"%(namespace)s"') %
             {'resource': resource_name,
              'namespace': namespace})
        LOG.error(m)
        raise exceptions.ExtensionError(error=m)

    return extension_manager


@utils.synchronized
def _get_extension_manager_of_resource(resource_name):
    """Get the resource specific ExtensionManager instance.

    :param resource_name: The name of the resource e.g.
        'system' / 'ethernet_interface' / 'update_service'
    :returns: the ExtensionManager instance
    :raises ExtensionError: on resource OEM extension load error.
    """
    global _global_extn_mgrs_by_resource

    if resource_name not in _global_extn_mgrs_by_resource:
        resource_namespace = 'sushy.resources.' + resource_name + '.oems'
        _global_extn_mgrs_by_resource[resource_name] = (
            _create_extension_manager(resource_namespace)
        )
    return _global_extn_mgrs_by_resource[resource_name]


def get_resource_extension_by_vendor(
        resource_name, vendor, resource):
    """Helper method to get Resource specific OEM extension object for vendor

    :param resource_name: The underscore joined name of the resource e.g.
        'system' / 'ethernet_interface' / 'update_service'
    :param vendor: This is the OEM vendor string which is the vendor-specific
        extensibility identifier. Examples are: 'Contoso', 'Hpe'. As a matter
        of fact the lowercase of this string will be the plugin entry point
        name.
    :param resource: The Sushy resource instance
    :returns: The object returned by ``plugin(*args, **kwds)`` of extension.
    :raises OEMExtensionNotFoundError: if no valid resource OEM extension
        found.
    """
    if resource_name in _global_extn_mgrs_by_resource:
        resource_extn_mgr = _global_extn_mgrs_by_resource[resource_name]
    else:
        resource_extn_mgr = _get_extension_manager_of_resource(resource_name)

    try:
        resource_vendor_extn = resource_extn_mgr[vendor.lower()]
    except KeyError:
        raise exceptions.OEMExtensionNotFoundError(
            resource=resource_name, name=vendor.lower())

    oem_resource = resource_vendor_extn.plugin()
    return resource.clone_resource(
        oem_resource).set_parent_resource(resource, vendor)
