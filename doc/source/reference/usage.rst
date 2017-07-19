..  _usage:

Using Sushy
===========

To use sushy in a project:

----------------------------------------
Creating and using a sushy system object
----------------------------------------

.. code-block:: python

  import logging

  import sushy

  # Enable logging at DEBUG level
  LOG = logging.getLogger('sushy')
  LOG.setLevel(logging.DEBUG)
  LOG.addHandler(logging.StreamHandler())

  s = sushy.Sushy('http://localhost:8000/redfish/v1',
                  username='foo', password='bar')

  # Get the Redfish version
  print(s.redfish_version)

  # Instantiate a system object
  sys_inst = s.get_system('/redfish/v1/Systems/437XR1138R2')


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

  # Get the memory summary
  print(sys_inst.memory_summary)

  # Get the processor summary
  print(sys_inst.processors.summary)


-----------------------------------------
Creating and using a sushy manager object
-----------------------------------------

.. code-block:: python

  import logging

  import sushy

  # Enable logging at DEBUG level
  LOG = logging.getLogger('sushy')
  LOG.setLevel(logging.DEBUG)
  LOG.addHandler(logging.StreamHandler())

  s = sushy.Sushy('http://localhost:8000/redfish/v1',
                  username='foo', password='bar')

  # Instantiate a manager object
  mgr_inst = s.get_manager('BMC')

  # Get the manager name & description
  print(mgr_inst.name)
  print(mgr_inst.description)


  # Using manager collections


  # Instantiate a ManagerCollection object
  mgr_col = s.get_manager_collection()

  # Print the ID of the managers available in the collection
  print(mgr_col.members_identities)

  # Get a list of manager objects available in the collection
  mgr_insts = mgr_col.get_members()

  # Instantiate a manager object, same as getting it directly
  # from the s.get_manager()
  mgr_inst = mgr_col.get_member(mgr_col.members_identities[0])

  # Refresh the manager collection object
  mgr_col.refresh()


  # Using manager actions


  # Get supported graphical console types
  print(mgr_inst.get_supported_graphical_console_types())

  # Get supported serial console types
  print(mgr_inst.get_supported_serial_console_types())

  # Get supported command shell types
  print(mgr_inst.get_supported_command_shell_types())

  # Get a list of allowed manager reset values
  print(mgr_inst.get_allowed_reset_manager_values())

  # Reset the manager
  mgr_inst.reset_manager(sushy.RESET_MANAGER_FORCE_RESTART)

  # Refresh the manager object
  mgr_inst.refresh()


If you do not have any real baremetal machine that supports the Redfish
protocol you can look at the :ref:`contributing` page to learn how to
run a Redfish emulator.
