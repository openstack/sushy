=======================
Sushy Library Reference
=======================

Features
========

* Abstraction around the SystemCollection and System resources (Basic
  server identification and asset information)
* Systems power management (Both soft and hard; Including NMI injection)
* Changing systems boot device, frequency (Once or permanently) and mode
  (UEFI or BIOS)
* Virtual media management
* SessionManagement

.. toctree::
   :maxdepth: 2

   usage

Missing Features
================

These are some features that sushy is presently missing.

* Collect sensor data (Health state, temperature, fans etc...)
* System disk size
* Serial console

Sushy Python API Reference
==========================

* :ref:`modindex`

.. # api/modules is hidden since it's in the modindex link above.
.. toctree::
  :hidden:

  api/modules
