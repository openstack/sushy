Overview
========

Sushy is a Python library to communicate with `Redfish`_ based systems.

The goal of the library is to be extremely simple, small, have as few
dependencies as possible and be very conservative when dealing with BMCs
by issuing just enough requests to it (BMCs are very flaky).

Therefore, the scope of the library has been limited to what is supported
by the `OpenStack Ironic <https://wiki.openstack.org/wiki/Ironic>`_
project. As the project grows and more features from `Redfish`_ are
needed we can expand Sushy to fulfill those requirements.

* Free software: Apache license
* Includes Redfish registry files licensed under
    Creative Commons Attribution 4.0 License:
    https://creativecommons.org/licenses/by/4.0/
* Documentation: https://docs.openstack.org/sushy/latest/
* Usage: https://docs.openstack.org/sushy/latest/reference/usage.html
* Source: https://opendev.org/openstack/sushy
* Bugs: https://storyboard.openstack.org/#!/project/960

.. _Redfish: http://www.dmtf.org/standards/redfish
