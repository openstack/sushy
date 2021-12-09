..  _usage:

Using Sushy
===========

To use sushy in a project:

-----------------------------------------
Specifying an authentication type
-----------------------------------------

There are three authentication objects. By default we use SessionOrBasicAuth.

Authentication Modes:

* auth.SessionOrBasicAuth: Use session based authentication. If we are unable
  to create a session we will fallback to basic authentication.
* auth.BasicAuth: Use basic authentication only.
* auth.SessionAuth: Use session based authentication only.

.. code-block:: python

  import logging

  import sushy
  from sushy import auth

  # Enable logging at DEBUG level
  LOG = logging.getLogger('sushy')
  LOG.setLevel(logging.DEBUG)
  LOG.addHandler(logging.StreamHandler())

  basic_auth = auth.BasicAuth(username='foo', password='bar')
  session_auth = auth.SessionAuth(username='foo', password='bar')
  session_or_basic_auth = auth.SessionOrBasicAuth(username='foo',
                                                  password='bar')

  s = sushy.Sushy('http://localhost:8000/redfish/v1',
                  auth=basic_auth)

  s = sushy.Sushy('http://localhost:8000/redfish/v1',
                  auth=session_auth)

  s = sushy.Sushy('http://localhost:8000/redfish/v1',
                  auth=session_or_basic_auth)

  # It is important to note that you can
  # call sushy without supplying an
  # authentication object. In that case we
  # will use the SessionOrBasicAuth authentication
  # object in an attempt to connect to all different
  # types of redfish servers.
  s = sushy.Sushy('http://localhost:8000/redfish/v1',
                  username='foo',
                  password='bar')

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
  #
  # See below for more options on how to refresh resources.
  sys_col.refresh()


  # Using system actions


  # Power the system ON
  sys_inst.reset_system(sushy.ResetType.ON)

  # Get a list of allowed reset values
  print(sys_inst.get_allowed_reset_system_values())

  # Refresh the system object (with all its sub-resources)
  sys_inst.refresh()

  # Alternatively, you can only refresh the resource if it is stale by passing
  # force=False:
  sys_inst.refresh(force=False)

  # A resource can be marked stale by calling invalidate. Note that its
  # subresources won't be marked as stale, and thus they won't be refreshed by
  # a call to refresh(force=False)
  sys_inst.invalidate()

  # Get the current power state
  print(sys_inst.power_state)

  # Set the next boot device to boot once from PXE in UEFI mode
  sys_inst.set_system_boot_source(sushy.BootSource.PXE,
                                  enabled=sushy.BootSourceOverrideEnabled.ONCE,
                                  mode=sushy.BootSourceOverrideMode.UEFI)

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
  mgr_col.invalidate()
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
  mgr_inst.reset_manager(sushy.ResetType.FORCE_RESTART)

  # Refresh the manager object (with all its sub-resources)
  mgr_inst.refresh(force=True)


  # Using Virtual Media

  # Instantiate a VirtualMediaCollection object
  virtmedia_col = mgr_inst.virtual_media

  # Print the ID of the VirtualMedia available in the collection
  print(virtmedia_col.members_identities)

  # Get a list of VirtualMedia objects available in the collection
  virtmedia_insts = virtmedia_col.get_members()

  # Instantiate a VirtualMedia object
  virtmedia_inst = virtmedia_col.get_member(
      virtmedia_col.members_identities[0])


  # Print out some of the VirtualMedia properties
  print(virtmedia_inst.name,
        virtmedia_inst.media_types)

  # Insert virtual media (invalidates virtmedia_inst contents)
  virtmedia_inst.insert_media('https://www.dmtf.org/freeImages/Sardine.img')

  # Refresh the resource to load actual contents
  virtmedia_inst.refresh()

  # Print out some of the VirtualMedia properties
  print(virtmedia_inst.image,
        virtmedia_inst.image_path,
        virtmedia_inst.inserted,
        virtmedia_inst.write_protected)

  # ... Boot the system off the virtual media...

  # Eject virtual media (invalidates virtmedia_inst contents)
  virtmedia_inst.eject_media()


-----------------------------------------------
Creating and using a sushy client with Sessions
-----------------------------------------------

.. code-block:: python

  import logging

  import sushy

  # Enable logging at DEBUG level
  LOG = logging.getLogger('sushy')
  LOG.setLevel(logging.DEBUG)
  LOG.addHandler(logging.StreamHandler())

  s = sushy.Sushy('http://localhost:8000/redfish/v1',
                  username='foo', password='bar')

  # Get the ComputerSystem object (if there is only one), otherwise
  # the identity must be provided as a path to the system.
  system = s.get_system()

  # A session is created automatically for you.
  # Print the boot field in the ComputerSystem.
  print(system.boot)

  # Upon session timeout, Sushy recreates the session based upon
  # provided credentials. If this fails, an exception is raised.

  # Explicitly request a session_key and session_uri.
  # This is not stored, but may be useful.
  session_key, session_uri = s.create_session(username='foo',
                                              password='bar')

  # Retrieve the session
  session = s.get_session(session_uri)

  # Delete the session
  session.delete()

--------------------
Using OEM extensions
--------------------

Before running this example, please make sure you have a Redfish BMC that
includes the OEM piece for a specific vendor, as well as the Sushy OEM
extension package installed in the system for the same vendor.

You can check the presence of the OEM extension within each Redfish
resource by specifying the vendor ID and search for them.

In the following example, we are looking up "Acme" vendor extension to Redfish
Manager resource.

.. code-block:: python

  import sushy

  root = sushy.Sushy('http://localhost:8000/redfish/v1')

  # Instantiate a system object
  system = root.get_system('/redfish/v1/Systems/437XR1138R2')

  print('Working on system resource %s' % system.identity)

  for manager in system.managers:

      print('Using System manager %s' % manager.identity)

      # Get a list of OEM extension names for the system manager
      oem_vendors = manager.oem_vendors

      print('Listing OEM extension name(s) for the System '
            'manager %s' % manager.identity )

      print(*oem_vendors, sep="\n")

      try:
          manager_oem = manager.get_oem_extension('Acme')

      except sushy.exceptions.OEMExtensionNotFoundError:
          print('ERROR: Acme OEM extension not found in '
                'Manager %s' % manager.identity)
          continue

      print('%s is an OEM extension of Manager %s'
             % (manager_oem.get_extension(), manager.identity))

      # set boot device to a virtual media device image
      manager_oem.set_virtual_boot_device(sushy.VirtualMediaType.CD,
                                          manager=manager)


If you do not have any real baremetal machine that supports the Redfish
protocol you can look at the :ref:`contributing` page to learn how to
run a Redfish emulator.

For the OEM extension example, presently, both of the emulators
(static/dynamic) do not expose any OEM; as a result, users may need to add
manually some OEM resources to emulators' templates. It may be easier to
start with a static emulator.
