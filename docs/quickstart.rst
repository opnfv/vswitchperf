Getting Started with 'vsperf'
=============================

Hardware Requirements
---------------------

VSPERF requires the following hardware to run tests: IXIA traffic
generator (IxNetwork), a machine that runs the IXIA client software and
a CentOS Linux release 7.1.1503 (Core) host.

vSwitch Requirements
--------------------

The vSwitch must support Open Flow 1.3 or greater.

Installation
------------

Follow the `installation instructions <installation.md>`__ to install.

IXIA Setup
----------

On the CentOS 7 system
~~~~~~~~~~~~~~~~~~~~~~

You need to install IxNetworkTclClient$(VER\_NUM)Linux.bin.tgz.

On the IXIA client software system
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Find the IxNetwork TCL server app (start -> All Programs -> IXIA ->
IxNetwork -> IxNetwork\_$(VER\_NUM) -> IxNetwork TCL Server)

Right click on IxNetwork TCL Server, select properties - Under shortcut tab in
the Target dialogue box make sure there is the argument "-tclport xxxx"
where xxxx is your port number (take note of this port number you will
need it for the 10\_custom.conf file).

|Alt text|

Hit Ok and start the TCL server application

Cloning and building src dependencies
-------------------------------------

In order to run VSPERF, you will need to download DPDK and OVS. You can
do this manually and build them in a preferred location, or you could
use vswitchperf/src. The vswitchperf/src directory contains makefiles
that will allow you to clone and build the libraries that VSPERF depends
on, such as DPDK and OVS. To clone and build simply:

  .. code-block:: console

    cd src
    make

VSPERF can be used with OVS without DPDK support. In this case you have
to specify path to the kernel sources by WITH\_LINUX parameter:

  .. code-block:: console

     cd src
     make WITH_LINUX=/lib/modules/`uname -r`/build

To build DPDK and OVS for PVP testing with vhost_user as the guest access
method, use:

  .. code-block:: console

     make VHOST_USER=y

To delete a src subdirectory and its contents to allow you to re-clone simply
use:

  .. code-block:: console

     make clobber

Configure the ``./conf/10_custom.conf`` file
--------------------------------------------

The supplied ``10_custom.conf`` file must be modified, as it contains
configuration items for which there are no reasonable default values.

The configuration items that can be added is not limited to the initial
contents. Any configuration item mentioned in any .conf file in
``./conf`` directory can be added and that item will be overridden by
the custom configuration value.

Using a custom settings file
----------------------------

Alternatively a custom settings file can be passed to ``vsperf`` via the
``--conf-file`` argument.

  .. code-block:: console

    ./vsperf --conf-file <path_to_settings_py> ...

Note that configuration passed in via the environment (``--load-env``)
or via another command line argument will override both the default and
your custom configuration files. This "priority hierarchy" can be
described like so (1 = max priority):

1. Command line arguments
2. Environment variables
3. Configuration file(s)

--------------

Executing tests
---------------

Before running any tests make sure you have root permissions by adding
the following line to /etc/sudoers:

  .. code-block:: console

    username ALL=(ALL)       NOPASSWD: ALL

username in the example above should be replaced with a real username.

To list the available tests:

  .. code-block:: console

    ./vsperf --list-tests

To run a group of tests, for example all tests with a name containing
'RFC2544':

  .. code-block:: console

    ./vsperf --conf-file=user_settings.py --tests="RFC2544"

To run all tests:

  .. code-block:: console

    ./vsperf --conf-file=user_settings.py

Some tests allow for configurable parameters, including test duration
(in seconds) as well as packet sizes (in bytes).

.. code:: bash

    ./vsperf --conf-file user_settings.py
        --tests RFC2544Tput
        --test-param "rfc2544_duration=10;packet_sizes=128"

For all available options, check out the help dialog:

  .. code-block:: console

    ./vsperf --help

Executing PVP tests
-------------------
To run tests using vhost-user as guest access method:

1. Set VHOST_METHOD and VNF of your settings file to:

  .. code-block:: console

   VHOST_METHOD='user'
   VNF = 'QemuDpdkVhost'

2. Recompile src for VHOST USER testing

  .. code-block:: console

     cd src
     make cleanse
     make VHOST_USER=y

3. Run test:

  .. code-block:: console

     ./vsperf --conf-file <path_to_settings_py>

To run tests using vhost-cuse as guest access method:

1. Set VHOST_METHOD and VNF of your settings file to:

  .. code-block:: console

     VHOST_METHOD='cuse'
     VNF = 'QemuDpdkVhostCuse'

2. Recompile src for VHOST USER testing

  .. code-block:: console

     cd src
     make cleanse
     make VHOST_USER=n

3. Run test:

  .. code-block:: console

     ./vsperf --conf-file <path_to_settings_py>



GOTCHAs:
--------

OVS with DPDK and QEMU
~~~~~~~~~~~~~~~~~~~~~~~
If you encounter the following error: "before (last 100 chars):
'-path=/dev/hugepages,share=on: unable to map backing store for
hugepages: Cannot allocate memory\r\n\r\n" with the PVP deployment
scenario, check the amount of hugepages on your system:

.. code:: bash

    cat /proc/meminfo | grep HugePages


By default the vswitchd is launched with 1Gb of memory, to  change
this, modify --socket-mem parameter in conf/02_vswitch.conf to allocate
an appropriate amount of memory:

.. code:: bash

    VSWITCHD_DPDK_ARGS = ['-c', '0x4', '-n', '4', '--socket-mem 1024,0']

--------------

.. |Alt text| image:: images/TCLServerProperties.png
