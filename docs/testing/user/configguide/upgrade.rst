.. This work is licensed under a Creative Commons Attribution 4.0 International License.
.. http://creativecommons.org/licenses/by/4.0
.. (c) OPNFV, Intel Corporation, AT&T and others.

=====================
Upgrading vswitchperf
=====================

Generic
-------

In case, that VSPERF is cloned from git repository, then it is easy to
upgrade it to the newest stable version or to the development version.

You could get a list of stable releases by ``git`` command. It is necessary
to update local git repository first.

**NOTE:** Git commands must be executed from directory, where VSPERF repository
was cloned, e.g. ``vswitchperf``.

Update of local git repository:

.. code:: bash

   $ git pull

List of stable releases:

.. code:: bash

   $ git tag

   brahmaputra.1.0
   colorado.1.0
   colorado.2.0
   colorado.3.0
   danube.1.0
   euphrates.1.0

You could select which stable release should be used. For example, select ``danube.1.0``:

.. code:: bash

   $ git checkout danube.1.0


Development version of VSPERF can be selected by:

.. code:: bash

   $ git checkout master

Colorado to Danube upgrade notes
--------------------------------

Obsoleted features
~~~~~~~~~~~~~~~~~~

Support of vHost Cuse interface has been removed in Danube release. It means,
that it is not possible to select ``QemuDpdkVhostCuse`` as a VNF anymore. Option
``QemuDpdkVhostUser`` should be used instead. Please check you configuration files
and definition of your testcases for any occurrence of:

.. code:: python

   VNF = "QemuDpdkVhostCuse"

or

.. code:: python

   "VNF" : "QemuDpdkVhostCuse"

In case that ``QemuDpdkVhostCuse`` is found, it must be modified to ``QemuDpdkVhostUser``.

**NOTE:** In case that execution of VSPERF is automated by scripts (e.g. for
CI purposes), then these scripts must be checked and updated too. It means,
that any occurrence of:

.. code:: bash

   ./vsperf --vnf QemuDpdkVhostCuse

must be updated to:

.. code:: bash

   ./vsperf --vnf QemuDpdkVhostUser

Configuration
~~~~~~~~~~~~~

Several configuration changes were introduced during Danube release. The most
important changes are discussed below.

Paths to DPDK, OVS and QEMU
===========================

VSPERF uses external tools for proper testcase execution. Thus it is important
to properly configure paths to these tools. In case that tools are installed
by installation scripts and are located inside ``./src`` directory inside
VSPERF home, then no changes are needed. On the other hand, if path settings
was changed by custom configuration file, then it is required to update configuration
accordingly. Please check your configuration files for following configuration
options:

.. code:: bash

   OVS_DIR
   OVS_DIR_VANILLA
   OVS_DIR_USER
   OVS_DIR_CUSE

   RTE_SDK_USER
   RTE_SDK_CUSE

   QEMU_DIR
   QEMU_DIR_USER
   QEMU_DIR_CUSE
   QEMU_BIN

In case that any of these options is defined, then configuration must be updated.
All paths to the tools are now stored inside ``PATHS`` dictionary. Please
refer to the :ref:`paths-documentation` and update your configuration where necessary.

Configuration change via CLI
============================

In previous releases it was possible to modify selected configuration options
(mostly VNF specific) via command line interface, i.e. by ``--test-params``
argument. This concept has been generalized in Danube release and it is
possible to modify any configuration parameter via CLI or via **Parameters**
section of the testcase definition. Old configuration options were obsoleted
and it is required to specify configuration parameter name in the same form
as it is defined inside configuration file, i.e. in uppercase. Please
refer to the :ref:`overriding-parameters-documentation` for additional details.

**NOTE:** In case that execution of VSPERF is automated by scripts (e.g. for
CI purposes), then these scripts must be checked and updated too. It means,
that any occurrence of

.. code:: bash

   guest_loopback
   vanilla_tgen_port1_ip
   vanilla_tgen_port1_mac
   vanilla_tgen_port2_ip
   vanilla_tgen_port2_mac
   tunnel_type

shall be changed to the uppercase form and data type of entered values must
match to data types of original values from configuration files.

In case that ``guest_nic1_name`` or ``guest_nic2_name`` is changed,
then new dictionary ``GUEST_NICS`` must be modified accordingly.
Please see :ref:`configuration-of-guest-options` and ``conf/04_vnf.conf`` for additional
details.

Traffic configuration via CLI
=============================

In previous releases it was possible to modify selected attributes of generated
traffic via command line interface. This concept has been enhanced in Danube
release and it is now possible to modify all traffic specific options via
CLI or by ``TRAFFIC`` dictionary in configuration file. Detailed description
is available at :ref:`configuration-of-traffic-dictionary` section of documentation.

Please check your automated scripts for VSPERF execution for following CLI
parameters and update them according to the documentation:

.. code:: bash

   bidir
   duration
   frame_rate
   iload
   lossrate
   multistream
   pkt_sizes
   pre-installed_flows
   rfc2544_tests
   stream_type
   traffic_type
