..  _usage:

=====
Usage
=====

To use sushy in a project:

.. code-block:: python

  import logging

  import sushy

  # Enable logging at DEBUG level
  LOG = logging.getLogger('sushy')
  LOG.setLevel(logging.DEBUG)
  LOG.addHandler(logging.StreamHandler())

  s = sushy.Sushy('http://127.0.0.1:8000/redfish/v1',
                  username='foo', password='bar')

  # Get the Redfish version
  print(s.redfish_version)

  # Instantiate a system object
  sys_inst = s.get_system('437XR1138R2')


  # Using system collections


  # Instantiate a SystemCollection object
  sys_col = s.get_system_collection()

  # Print the ID of the systems available in the collection
  print(sys_col.members_identities)

  # Get a list of systems objects available in the collection
  sys_col_insts = sys_col.get_members()

  # Instantiate a system object, same as getting it directly
  # from the s.get_system()
  sys_inst = sys_col.get_member(sys_col.members_identities[0])

  # Refresh the system collection object
  sys_col.refresh()


  # Using system actions


  # Power the system ON
  sys_inst.reset_system(sushy.RESET_ON)

  # Get a list of allowed reset values
  print(sys_inst.get_allowed_reset_system_values())

  # Refresh the system object
  sys_inst.refresh()

  # Get the current power state
  print(sys_inst.power_state)

  # Set the next boot device to boot once from PXE in UEFI mode
  sys_inst.set_system_boot_source(sushy.BOOT_SOURCE_TARGET_PXE,
                                  enabled=sushy.BOOT_SOURCE_ENABLED_ONCE,
                                  mode=sushy.BOOT_SOURCE_MODE_UEFI)

  # Get the current boot source information
  print(sys_inst.boot)

  # Get a list of allowed boot source target values
  print(sys_inst.get_allowed_system_boot_source_values())


Running the mockup server
-------------------------

Sushy ships with a small script at ``tools/mockup_server.py``
that creates a HTTP server to serve any of the `Redfish mockups
<https://www.dmtf.org/standards/redfish>`_. This enables users to test
the library without having a real hardware.

To run it, do:

#. Download the .zip containing the Redfish mockups files from
   https://www.dmtf.org/standards/redfish, for example::

     wget https://www.dmtf.org/sites/default/files/standards/documents/DSP2043_1.0.0.zip

#. Extract it somewhere in the file-system::

    unzip DSP2043_1.0.0.zip -d <output-path>

#. Now run the ``mockup_server.py`` script::

    python sushy/tools/mockup_server.py -m <output-path>/DSP2043-server
