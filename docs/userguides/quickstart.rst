=============================
Getting Started with 'vsperf'
=============================

Requirements
-------------

VSPERF requires a traffic generators to run tests, automated traffic gen
support in VSPERF includes:

- IXIA traffic generator (IxNetwork hardware) and a machine that runs the IXIA
  client software.
- Spirent traffic generator (TestCenter hardware chassis or TestCenter virtual
  in a VM) and a VM to run the Spirent Virtual Deployment Service image,
  formerly known as "Spirent LabServer".

If you want to use another traffic generator, please select the Dummy generator
option as shown in `Traffic generator instructions
<http://artifacts.opnfv.org/vswitchperf/docs/docs/guides/trafficgen.html>`__

Supported OSes include:

* CentOS Linux release 7.1.1503 (Core) host.
* Fedora 21 and 22.
* Ubuntu 14.04

vSwitch Requirements
--------------------

The vSwitch must support Open Flow 1.3 or greater. VSPERF supports both:

* OVS
* OVS with DPDK

VSPERF Installation
--------------------

Follow the `installation instructions
<http://artifacts.opnfv.org/vswitchperf/docs/docs/guides/index.html>`__ to
install.

Traffic Generator Setup
-----------------------
Follow the `Traffic generator instructions
<http://artifacts.opnfv.org/vswitchperf/docs/docs/guides/trafficgen.html>`__ to
install and configure a suitable traffic generator.

Cloning and building src dependencies
-------------------------------------

In order to run VSPERF, you will need to download DPDK and OVS. You can
do this manually and build them in a preferred location, OR you could
use vswitchperf/src. The vswitchperf/src directory contains makefiles
that will allow you to clone and build the libraries that VSPERF depends
on, such as DPDK and OVS. To clone and build simply:

.. code-block:: console

    $ cd src
    $ make

VSPERF can be used with stock OVS (without DPDK support). In this case you have
to specify path to the kernel sources when building OVS in src by specifying
WITH\_LINUX parameter:

.. code-block:: console

     $ cd src
     $ make WITH_LINUX=/lib/modules/`uname -r`/build

To build DPDK and OVS in the src directory for PVP and PVVP testing with
vhost_user as the guest access method, use:

.. code-block:: console

     $ make VHOST_USER=y

To build all options in src:

* Vanilla OVS
* OVS with vhost_user as the guest access method (with DPDK support)
* OVS with vhost_cuse s the guest access method (with DPDK support)

simply call 'make' in the src directory :

.. code-block:: console

     $ make

The vhost_user build will reside in src/ovs/
The vhost_cuse build will reside in vswitchperf/src_cuse
The Vanilla OVS build will reside in vswitchperf/src_vanilla

To delete a src subdirectory and its contents to allow you to re-clone simply
use:

.. code-block:: console

     $ make clobber

Configure the ``./conf/10_custom.conf`` file
--------------------------------------------
The ``10_custom.conf`` file is the configuration file that overrides
default configurations in all the other configuration files in ``./conf``
The supplied ``10_custom.conf`` file **MUST** be modified, as it contains
configuration items for which there are no reasonable default values.

The configuration items that can be added is not limited to the initial
contents. Any configuration item mentioned in any .conf file in
``./conf`` directory can be added and that item will be overridden by
the custom configuration value.

Using a custom settings file
----------------------------

If your ``10_custom.conf`` doesn't reside in the ``./conf`` directory
of if you want to use an alternative configuration file, the file can
be passed to ``vsperf`` via the ``--conf-file`` argument.

.. code-block:: console

    $ ./vsperf --conf-file <path_to_custom_conf> ...

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

    $ ./vsperf --list

To run a single test:

.. code-block:: console

    $ ./vsperf $TESTNAME

Where $TESTNAME is the name of the vsperf test you would like to run.

To run a group of tests, for example all tests with a name containing
'RFC2544':

.. code-block:: console

    $ ./vsperf --conf-file=<path_to_custom_conf>/10_custom.conf --tests="RFC2544"

To run all tests:

.. code-block:: console

    $ ./vsperf --conf-file=<path_to_custom_conf>/10_custom.conf

Some tests allow for configurable parameters, including test duration
(in seconds) as well as packet sizes (in bytes).

.. code:: bash

    $ ./vsperf --conf-file user_settings.py
        --tests RFC2544Tput
        --test-param "duration=10;pkt_sizes=128"

For all available options, check out the help dialog:

.. code-block:: console

    $ ./vsperf --help

Executing Vanilla OVS tests
----------------------------
If you have compiled all the variants of OVS in ''src/'' please skip
step 1.

1. Recompile src for Vanilla OVS testing

.. code-block:: console

     $ cd src
     $ make cleanse
     $ make WITH_LINUX=/lib/modules/`uname -r`/build

2. Update your ''10_custom.conf'' file to use the appropriate variables
for Vanilla OVS:

.. code-block:: console

   VSWITCH = 'OvsVanilla'
   VSWITCH_VANILLA_PHY_PORT_NAMES = ['$PORT1', '$PORT1']

Where $PORT1 and $PORT2 are the Linux interfaces you'd like to bind
to the vswitch.

3. Run test:

.. code-block:: console

     $ ./vsperf --conf-file=<path_to_custom_conf>

Please note if you don't want to configure Vanilla OVS through the
configuration file, you can pass it as a CLI argument; BUT you must
set the ports.

.. code-block:: console

    $ ./vsperf --vswitch OvsVanilla


Executing PVP and PVVP tests
----------------------------
To run tests using vhost-user as guest access method:

1. Set VHOST_METHOD and VNF of your settings file to:

.. code-block:: console

   VHOST_METHOD='user'
   VNF = 'QemuDpdkVhost'

2. Recompile src for VHOST USER testing

.. code-block:: console

     $ cd src
     $ make cleanse
     $ make VHOST_USER=y

3. Run test:

.. code-block:: console

     $ ./vsperf --conf-file=<path_to_custom_conf>/10_custom.conf

To run tests using vhost-cuse as guest access method:

1. Set VHOST_METHOD and VNF of your settings file to:

.. code-block:: console

     VHOST_METHOD='cuse'
     VNF = 'QemuDpdkVhostCuse'

2. Recompile src for VHOST USER testing

.. code-block:: console

     $ cd src
     $ make cleanse
     $ make VHOST_USER=n

3. Run test:

.. code-block:: console

     $ ./vsperf --conf-file=<path_to_custom_conf>/10_custom.conf

Executing PVP tests using Vanilla OVS
-------------------------------------
To run tests using Vanilla OVS:

1. Set the following variables:

.. code-block:: console

   VSWITCH = 'OvsVanilla'
   VNF = 'QemuVirtioNet'

   VANILLA_TGEN_PORT1_IP = n.n.n.n
   VANILLA_TGEN_PORT1_MAC = nn:nn:nn:nn:nn:nn

   VANILLA_TGEN_PORT2_IP = n.n.n.n
   VANILLA_TGEN_PORT2_MAC = nn:nn:nn:nn:nn:nn

   VANILLA_BRIDGE_IP = n.n.n.n

   or use --test-param

   ./vsperf --conf-file=<path_to_custom_conf>/10_custom.conf
            --test-param "vanilla_tgen_tx_ip=n.n.n.n;
                          vanilla_tgen_tx_mac=nn:nn:nn:nn:nn:nn"


2. Recompile src for Vanilla OVS testing

.. code-block:: console

     $ cd src
     $ make cleanse
     $ make WITH_LINUX=/lib/modules/`uname -r`/build

3. Run test:

.. code-block:: console

     $ ./vsperf --conf-file<path_to_custom_conf>/10_custom.conf

Selection of loopback application for PVP and PVVP tests
--------------------------------------------------------
To select loopback application, which will perform traffic forwarding
inside VM, following configuration parameter should be configured:

.. code-block:: console

     GUEST_LOOPBACK = ['testpmd', 'testpmd']

or use --test-param

.. code-block:: console

        $ ./vsperf --conf-file=<path_to_custom_conf>/10_custom.conf
              --test-param "guest_loopback=testpmd"

Supported loopback applications are:

.. code-block:: console

     'testpmd'       - testpmd from dpdk will be built and used
     'l2fwd'         - l2fwd module provided by Huawei will be built and used
     'linux_bridge'  - linux bridge will be configured
     'buildin'       - nothing will be configured by vsperf; VM image must
                       ensure traffic forwarding between its interfaces

Guest loopback application must be configured, otherwise traffic
will not be forwarded by VM and testcases with PVP and PVVP deployments
will fail. Guest loopback application is set to 'testpmd' by default.

VSPERF modes of operation
-------------------------
VSPERF can be run in different modes. By default it will configure vSwitch,
traffic generator and VNF. However it can be used just for configuration
and execution of traffic generator. Another option is execution of all
components except traffic generator itself.

Mode of operation is driven by configuration parameter -m or --mode

.. code-block:: console

    -m MODE, --mode MODE  vsperf mode of operation;
        Values:
            "normal" - execute vSwitch, VNF and traffic generator
            "trafficgen" - execute only traffic generator
            "trafficgen-off" - execute vSwitch and VNF

In case, that VSPERF is executed in "trafficgen" mode, then configuration
of traffic generator should be configured through --test-param option.
Supported CLI options useful for traffic generator configuration are:

.. code-block:: console

    'traffic_type'  - One of the supported traffic types. E.g. rfc2544,
                      back2back or continuous
                      Default value is "rfc2544".
    'bidirectional' - Specifies if generated traffic will be full-duplex (true)
                      or half-duplex (false)
                      Default value is "false".
    'iload'         - Defines desired percentage of frame rate used during
                      continuous stream tests.
                      Default value is 100.
    'multistream'   - Defines number of flows simulated by traffic generator.
                      Value 0 disables MultiStream feature
                      Default value is 0.
    'stream_type'   - Stream Type is an extension of the "MultiStream" feature.
                      If MultiStream is disabled, then Stream Type will be
                      ignored. Stream Type defines ISO OSI network layer used
                      for simulation of multiple streams.
                      Default value is "L4".

Example of execution of VSPERF in "trafficgen" mode:

.. code-block:: console

    ./vsperf -m trafficgen --trafficgen IxNet --conf-file vsperf.conf
        --test-params "traffic_type=continuous;bidirectional=True;iload=60"

Code change verification by pylint
----------------------------------
Every developer participating in VSPERF project should run
pylint before his python code is submitted for review. Project
specific configuration for pylint is available at 'pylint.rc'.

Example of manual pylint invocation:

.. code-block:: console

          $ pylint --rcfile ./pylintrc ./vsperf

GOTCHAs:
--------

OVS with DPDK and QEMU
~~~~~~~~~~~~~~~~~~~~~~~
If you encounter the following error: "before (last 100 chars):
'-path=/dev/hugepages,share=on: unable to map backing store for
hugepages: Cannot allocate memory\r\n\r\n" with the PVP or PVVP
deployment scenario, check the amount of hugepages on your system:

.. code-block:: console

    $ cat /proc/meminfo | grep HugePages


By default the vswitchd is launched with 1Gb of memory, to  change
this, modify --socket-mem parameter in conf/02_vswitch.conf to allocate
an appropriate amount of memory:

.. code-block:: console

    VSWITCHD_DPDK_ARGS = ['-c', '0x4', '-n', '4', '--socket-mem 1024,0']

