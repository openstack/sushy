.. _contributing:

=====================
Contributing to Sushy
=====================

How to contribute
=================
.. include:: ../../../CONTRIBUTING.rst


Running a Redfish emulator
==========================

Testing and/or developing Sushy without owning a real baremetal machine
that supports the Redfish protocol is possible by running an emulator,
the `sushy-tools`_ project ships with two emulators that can be used
for this purpose. To install it run::

  sudo pip install --user sushy-tools

.. note::
    Installing the dependencies requires libvirt development files.
    For example, run the following command to install them on Fedora::

        sudo dnf install -y libvirt-devel


Static emulator
~~~~~~~~~~~~~~~

After installing `sushy-tools`_ you will have a new CLI tool named
``sushy-static``. This tool creates a HTTP server to serve any of the
`Redfish mockups <https://www.dmtf.org/standards/redfish>`_. The files
are static so operations like changing the boot device or the power state
**will not** have any effect. But that should be enough for enabling
people to test parts of the library.

To use ``sushy-static`` we need the Redfish mockup files that can be
downloaded from https://www.dmtf.org/standards/redfish, for example::

  wget https://www.dmtf.org/sites/default/files/standards/documents/DSP2043_1.0.0.zip

After the download, extract the files somewhere in the file-system::

  unzip DSP2043_1.0.0.zip -d <output-path>

Now run ``sushy-static`` pointing to those files. For example to serve
the ``DSP2043-server`` mockup files, run::

  sushy-static --mockup-files <output-path>/DSP2043-server


Libvirt emulator
~~~~~~~~~~~~~~~~

The second emulator shipped by `sushy-tools`_ is the CLI tool named
``sushy-emulator``. This tool starts a ReST API that users can use to
interact with virtual machines using the Redfish protocol. So operations
such as changing the boot device or the power state will actually affect
the virtual machines. This allows users to test the library in a more
dynamic way. To run it do

.. code-block:: sh

  sushy-emulator

  # Or, running with custom parameters
  sushy-emulator --port 8000 --libvirt-uri "qemu:///system"

That's it, now you can test Sushy against the ``http://locahost:8000``
endpoint.


Enabling SSL
~~~~~~~~~~~~

Both mockup servers supports `SSL`_ if you want Sushy with it. To set it
up, first you need to generate key and certificate files with OpenSSL
use following command::

  openssl req -x509 -newkey rsa:2048 -keyout key.pem -out cert.pem -days 365

Start the mockup server passing the ``--ssl-certificate`` and
``--ssl-key`` parameters to it, for example::

 sushy-emulator --ssl-key key.pem --ssl-certificate cert.pem

Now to connect with `SSL`_ to the server use the ``verify`` parameter
pointing to the certificate file when instantiating Sushy, for example:

.. code-block:: python

  import sushy

  # Note the HTTP"S"
  s = sushy.Sushy('https://localhost:8000', verify='cert.pem', username='foo', password='bar')

.. _SSL: https://en.wikipedia.org/wiki/Secure_Sockets_Layer
.. _sushy-tools: https://opendev.org/openstack/sushy-tools
