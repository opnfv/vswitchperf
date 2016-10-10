.. This work is licensed under a Creative Commons Attribution 4.0 International License.
.. http://creativecommons.org/licenses/by/4.0
.. (c) OPNFV, Intel Corporation, AT&T and others.

vSwitchPerf test suites userguide
---------------------------------

General
^^^^^^^

VSPERF requires a traffic generators to run tests, automated traffic gen
support in VSPERF includes:

- IXIA traffic generator (IxNetwork hardware) and a machine that runs the IXIA
  client software.
- Spirent traffic generator (TestCenter hardware chassis or TestCenter virtual
  in a VM) and a VM to run the Spirent Virtual Deployment Service image,
  formerly known as "Spirent LabServer".
- Xena Network traffic generator (Xena hardware chassis) that houses the Xena
  Traffic generator modules.
- Moongen software traffic generator. Requires a separate machine running
  moongen to execute packet generation.

If you want to use another traffic generator, please select the Dummy generator
option as shown in `Traffic generator instructions
<http://artifacts.opnfv.org/vswitchperf/docs/configguide/trafficgen.html>`__

VSPERF Installation
^^^^^^^^^^^^^^^^^^^

To see the supported Operating Systems, vSwitches and system requirements,
please follow the `installation instructions
<http://artifacts.opnfv.org/vswitchperf/docs/configguide/installation.html>`__ to
install.

Traffic Generator Setup
^^^^^^^^^^^^^^^^^^^^^^^

Follow the `Traffic generator instructions
<http://artifacts.opnfv.org/vswitchperf/docs/configguide/trafficgen.html>`__ to
install and configure a suitable traffic generator.

Cloning and building src dependencies
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

In order to run VSPERF, you will need to download DPDK and OVS. You can
do this manually and build them in a preferred location, OR you could
use vswitchperf/src. The vswitchperf/src directory contains makefiles
that will allow you to clone and build the libraries that VSPERF depends
on, such as DPDK and OVS. To clone and build simply:

.. code-block:: console

    $ cd src
    $ make

VSPERF can be used with stock OVS (without DPDK support). When build
is finished, the libraries are stored in src_vanilla directory.

The 'make' builds all options in src:

* Vanilla OVS
* OVS with vhost_user as the guest access method (with DPDK support)

The vhost_user build will reside in src/ovs/
The Vanilla OVS build will reside in vswitchperf/src_vanilla

To delete a src subdirectory and its contents to allow you to re-clone simply
use:

.. code-block:: console

     $ make clobber

Configure the ``./conf/10_custom.conf`` file
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The ``10_custom.conf`` file is the configuration file that overrides
default configurations in all the other configuration files in ``./conf``
The supplied ``10_custom.conf`` file **MUST** be modified, as it contains
configuration items for which there are no reasonable default values.

The configuration items that can be added is not limited to the initial
contents. Any configuration item mentioned in any .conf file in
``./conf`` directory can be added and that item will be overridden by
the custom configuration value.

Further details about configuration files evaluation and special behaviour
of options with ``GUEST_`` prefix could be found at `design document
<http://artifacts.opnfv.org/vswitchperf/docs/design/vswitchperf_design.html#configuration>`__.

Using a custom settings file
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

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

Further details about configuration files evaluation and special behaviour
of options with ``GUEST_`` prefix could be found at `design document
<http://artifacts.opnfv.org/vswitchperf/docs/design/vswitchperf_design.html#configuration>`__.

vloop_vnf
^^^^^^^^^

vsperf uses a VM image called vloop_vnf for looping traffic in the deployment
scenarios involving VMs. The image can be downloaded from
`<http://artifacts.opnfv.org/>`__.

.. code-block:: console

    $ wget http://artifacts.opnfv.org/vswitchperf/vloop-vnf-ubuntu-14.04_20151216.qcow2

Newer vloop_vnf images are available. Please reference the
installation instructions for information on these images
`installation instructions
<http://artifacts.opnfv.org/vswitchperf/docs/configguide/installation.html>`__


vloop_vnf forwards traffic through a VM using one of:
* DPDK testpmd
* Linux Bridge
* l2fwd kernel Module.

Alternatively you can use your own QEMU image.

l2fwd Kernel Module
^^^^^^^^^^^^^^^^^^^

A Kernel Module that provides OSI Layer 2 Ipv4 termination or forwarding with
support for Destination Network Address Translation (DNAT) for both the MAC and
IP addresses. l2fwd can be found in <vswitchperf_dir>/src/l2fwd

Executing tests
^^^^^^^^^^^^^^^

All examples inside these docs assume, that user is inside the VSPERF
directory. VSPERF can be executed from any directory.

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
        --test-params "duration=10;pkt_sizes=128"

For all available options, check out the help dialog:

.. code-block:: console

    $ ./vsperf --help

Executing Vanilla OVS tests
^^^^^^^^^^^^^^^^^^^^^^^^^^^

1. If needed, recompile src for all OVS variants

.. code-block:: console

     $ cd src
     $ make distclean
     $ make

2. Update your ''10_custom.conf'' file to use the appropriate variables
for Vanilla OVS:

.. code-block:: console

   VSWITCH = 'OvsVanilla'

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


Executing tests with VMs
^^^^^^^^^^^^^^^^^^^^^^^^

To run tests using vhost-user as guest access method:

1. Set VHOST_METHOD and VNF of your settings file to:

.. code-block:: console

   VSWITCH = 'OvsDpdkVhost'
   VNF = 'QemuDpdkVhost'

2. If needed, recompile src for all OVS variants

.. code-block:: console

     $ cd src
     $ make distclean
     $ make

3. Run test:

.. code-block:: console

     $ ./vsperf --conf-file=<path_to_custom_conf>/10_custom.conf

Executing tests with VMs using Vanilla OVS
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

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

   $ ./vsperf --conf-file=<path_to_custom_conf>/10_custom.conf
              --test-params "vanilla_tgen_tx_ip=n.n.n.n;
                            vanilla_tgen_tx_mac=nn:nn:nn:nn:nn:nn"


2. If needed, recompile src for all OVS variants

.. code-block:: console

     $ cd src
     $ make distclean
     $ make

3. Run test:

.. code-block:: console

     $ ./vsperf --conf-file<path_to_custom_conf>/10_custom.conf

.. _vfio-pci:

Using vfio_pci with DPDK
^^^^^^^^^^^^^^^^^^^^^^^^^

To use vfio with DPDK instead of igb_uio add into your custom configuration
file the following parameter:

.. code-block:: console

    PATHS['dpdk']['src']['modules'] = ['uio', 'vfio-pci']


**NOTE:** In case, that DPDK is installed from binary package, then please
set ``PATHS['dpdk']['bin']['modules']`` instead.

**NOTE:** Please ensure that Intel VT-d is enabled in BIOS.

**NOTE:** Please ensure your boot/grub parameters include
the following:

.. code-block:: console

    iommu=pt intel_iommu=on

To check that IOMMU is enabled on your platform:

.. code-block:: console

    $ dmesg | grep IOMMU
    [    0.000000] Intel-IOMMU: enabled
    [    0.139882] dmar: IOMMU 0: reg_base_addr fbffe000 ver 1:0 cap d2078c106f0466 ecap f020de
    [    0.139888] dmar: IOMMU 1: reg_base_addr ebffc000 ver 1:0 cap d2078c106f0466 ecap f020de
    [    0.139893] IOAPIC id 2 under DRHD base  0xfbffe000 IOMMU 0
    [    0.139894] IOAPIC id 0 under DRHD base  0xebffc000 IOMMU 1
    [    0.139895] IOAPIC id 1 under DRHD base  0xebffc000 IOMMU 1
    [    3.335744] IOMMU: dmar0 using Queued invalidation
    [    3.335746] IOMMU: dmar1 using Queued invalidation
    ....

.. _SRIOV-support:

Using SRIOV support
^^^^^^^^^^^^^^^^^^^

To use virtual functions of NIC with SRIOV support, use extended form
of NIC PCI slot definition:

.. code-block:: python

    WHITELIST_NICS = ['0000:05:00.0|vf0', '0000:05:00.1|vf3']

Where 'vf' is an indication of virtual function usage and following
number defines a VF to be used. In case that VF usage is detected,
then vswitchperf will enable SRIOV support for given card and it will
detect PCI slot numbers of selected VFs.

So in example above, one VF will be configured for NIC '0000:05:00.0'
and four VFs will be configured for NIC '0000:05:00.1'. Vswitchperf
will detect PCI addresses of selected VFs and it will use them during
test execution.

At the end of vswitchperf execution, SRIOV support will be disabled.

SRIOV support is generic and it can be used in different testing scenarios.
For example:

* vSwitch tests with DPDK or without DPDK support to verify impact
  of VF usage on vSwitch performance
* tests without vSwitch, where traffic is forwared directly
  between VF interfaces by packet forwarder (e.g. testpmd application)
* tests without vSwitch, where VM accesses VF interfaces directly
  by PCI-passthrough_ to measure raw VM throughput performance.

.. _PCI-passthrough:

Using QEMU with PCI passthrough support
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Raw virtual machine throughput performance can be measured by execution of PVP
test with direct access to NICs by PCI passthrough. To execute VM with direct
access to PCI devices, enable vfio-pci_. In order to use virtual functions,
SRIOV-support_ must be enabled.

Execution of test with PCI passthrough with vswitch disabled:

.. code-block:: console

    $ ./vsperf --conf-file=<path_to_custom_conf>/10_custom.conf
               --vswitch none --vnf QemuPciPassthrough pvp_tput

Any of supported guest-loopback-application_ can be used inside VM with
PCI passthrough support.

Note: Qemu with PCI passthrough support can be used only with PVP test
deployment.

.. _guest-loopback-application:

Selection of loopback application for tests with VMs
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

To select loopback application, which will perform traffic forwarding
inside VM, following configuration parameter should be configured:

.. code-block:: console

     GUEST_LOOPBACK = ['testpmd']

or use --test-param

.. code-block:: console

        $ ./vsperf --conf-file=<path_to_custom_conf>/10_custom.conf
              --test-params "guest_loopback=testpmd"

Supported loopback applications are:

.. code-block:: console

     'testpmd'       - testpmd from dpdk will be built and used
     'l2fwd'         - l2fwd module provided by Huawei will be built and used
     'linux_bridge'  - linux bridge will be configured
     'buildin'       - nothing will be configured by vsperf; VM image must
                       ensure traffic forwarding between its interfaces

Guest loopback application must be configured, otherwise traffic
will not be forwarded by VM and testcases with VM related deployments
will fail. Guest loopback application is set to 'testpmd' by default.

Note: In case that only 1 or more than 2 NICs are configured for VM,
then 'testpmd' should be used. As it is able to forward traffic between
multiple VM NIC pairs.

Note: In case of linux_bridge, all guest NICs are connected to the same
bridge inside the guest.

Multi-Queue Configuration
^^^^^^^^^^^^^^^^^^^^^^^^^

VSPerf currently supports multi-queue with the following limitations:

 1.  Requires QEMU 2.5 or greater and any OVS version higher than 2.5. The
     default upstream package versions installed by VSPerf satisfies this
     requirement.

 2.  Guest image must have ethtool utility installed if using l2fwd or linux
     bridge inside guest for loopback.

 3.  If using OVS versions 2.5.0 or less enable old style multi-queue as shown
     in the ''02_vswitch.conf'' file.

  .. code-block:: console

     OVS_OLD_STYLE_MQ = True

To enable multi-queue for dpdk modify the ''02_vswitch.conf'' file.

  .. code-block:: console

     VSWITCH_DPDK_MULTI_QUEUES = 2

**NOTE:** you should consider using the switch affinity to set a pmd cpu mask
that can optimize your performance. Consider the numa of the NIC in use if this
applies by checking /sys/class/net/<eth_name>/device/numa_node and setting an
appropriate mask to create PMD threads on the same numa node.

When multi-queue is enabled, each dpdk or dpdkvhostuser port that is created
on the switch will set the option for multiple queues. If old style multi queue
has been enabled a global option for multi queue will be used instead of the
port by port option.

To enable multi-queue on the guest modify the ''04_vnf.conf'' file.

  .. code-block:: console

     GUEST_NIC_QUEUES = 2

Enabling multi-queue at the guest will add multiple queues to each NIC port when
qemu launches the guest.

In case of Vanilla OVS, multi-queue is enabled on the tuntap ports and nic
queues will be enabled inside the guest with ethtool. Simply enabling the
multi-queue on the guest is sufficient for Vanilla OVS multi-queue.

Testpmd should be configured to take advantage of multi-queue on the guest if
using DPDKVhostUser. This can be done by modifying the ''04_vnf.conf'' file.

  .. code-block:: console

     GUEST_TESTPMD_CPU_MASK = '-l 0,1,2,3,4'

     GUEST_TESTPMD_NB_CORES = 4
     GUEST_TESTPMD_TXQ = 2
     GUEST_TESTPMD_RXQ = 2

**NOTE:** The guest SMP cores must be configured to allow for testpmd to use the
optimal number of cores to take advantage of the multiple guest queues.

In case of using Vanilla OVS and qemu virtio-net you can increase performance
by binding vhost-net threads to cpus. This can be done by enabling the affinity
in the ''04_vnf.conf'' file. This can be done to non multi-queue enabled
configurations as well as there will be 2 vhost-net threads.

  .. code-block:: console

     VSWITCH_VHOST_NET_AFFINITIZATION = True

     VSWITCH_VHOST_CPU_MAP = [4,5,8,11]

**NOTE:** This method of binding would require a custom script in a real
environment.

**NOTE:** For optimal performance guest SMPs and/or vhost-net threads should be
on the same numa as the NIC in use if possible/applicable. Testpmd should be
assigned at least (nb_cores +1) total cores with the cpu mask.

The following CLI parameters override the corresponding configuration settings:
     1. guest_nic_queues, which overrides all GUEST_NIC_QUEUES values
     2. guest_testpmd_txq, which overrides all GUEST_TESTPMD_TXQ
     3. guest_testpmd_rxq, which overrides all GUEST_TESTPMD_RXQ
     4. guest_testpmd_nb_cores, which overrides all GUEST_TESTPMD_NB_CORES
        values
     5. guest_testpmd_cpu_mask, which overrides all GUEST_TESTPMD_CPU_MASK
        values
     6. vswitch_dpdk_multi_queues, which overrides VSWITCH_DPDK_MULTI_QUEUES
     7. guest_smp, which overrides all GUEST_SMP values
     8. guest_core_binding, which overrides all GUEST_CORE_BINDING values

Executing Packet Forwarding tests
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

To select application, which will perform packet forwarding,
following configuration parameter should be configured:

  .. code-block:: console

     VSWITCH = 'none'
     PKTFWD = 'TestPMD'

     or use --vswitch and --fwdapp

     $ ./vsperf --conf-file user_settings.py
              --vswitch none
              --fwdapp TestPMD

Supported Packet Forwarding applications are:

  .. code-block:: console

     'testpmd'       - testpmd from dpdk


1. Update your ''10_custom.conf'' file to use the appropriate variables
for selected Packet Forwarder:

  .. code-block:: console

   # testpmd configuration
   TESTPMD_ARGS = []
   # packet forwarding mode supported by testpmd; Please see DPDK documentation
   # for comprehensive list of modes supported by your version.
   # e.g. io|mac|mac_retry|macswap|flowgen|rxonly|txonly|csum|icmpecho|...
   # Note: Option "mac_retry" has been changed to "mac retry" since DPDK v16.07
   TESTPMD_FWD_MODE = 'csum'
   # checksum calculation layer: ip|udp|tcp|sctp|outer-ip
   TESTPMD_CSUM_LAYER = 'ip'
   # checksum calculation place: hw (hardware) | sw (software)
   TESTPMD_CSUM_CALC = 'sw'
   # recognize tunnel headers: on|off
   TESTPMD_CSUM_PARSE_TUNNEL = 'off'

2. Run test:

  .. code-block:: console

     $ ./vsperf --conf-file <path_to_settings_py>

VSPERF modes of operation
^^^^^^^^^^^^^^^^^^^^^^^^^

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
            "trafficgen-pause" - execute vSwitch and VNF but wait before traffic transmission

In case, that VSPERF is executed in "trafficgen" mode, then configuration
of traffic generator should be configured through --test-params option.
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

    $ ./vsperf -m trafficgen --trafficgen IxNet --conf-file vsperf.conf
        --test-params "traffic_type=continuous;bidirectional=True;iload=60"

Code change verification by pylint
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Every developer participating in VSPERF project should run
pylint before his python code is submitted for review. Project
specific configuration for pylint is available at 'pylint.rc'.

Example of manual pylint invocation:

.. code-block:: console

          $ pylint --rcfile ./pylintrc ./vsperf

GOTCHAs:
^^^^^^^^

OVS with DPDK and QEMU
~~~~~~~~~~~~~~~~~~~~~~~

If you encounter the following error: "before (last 100 chars):
'-path=/dev/hugepages,share=on: unable to map backing store for
hugepages: Cannot allocate memory\r\n\r\n" during qemu initialization,
check the amount of hugepages on your system:

.. code-block:: console

    $ cat /proc/meminfo | grep HugePages


By default the vswitchd is launched with 1Gb of memory, to  change
this, modify --socket-mem parameter in conf/02_vswitch.conf to allocate
an appropriate amount of memory:

.. code-block:: console

    VSWITCHD_DPDK_ARGS = ['-c', '0x4', '-n', '4', '--socket-mem 1024,0']
    VSWITCHD_DPDK_CONFIG = {
        'dpdk-init' : 'true',
        'dpdk-lcore-mask' : '0x4',
        'dpdk-socket-mem' : '1024,0',
    }

Note: Option VSWITCHD_DPDK_ARGS is used for vswitchd, which supports --dpdk
parameter. In recent vswitchd versions, option VSWITCHD_DPDK_CONFIG will be
used to configure vswitchd via ovs-vsctl calls.


More information
^^^^^^^^^^^^^^^^

For more information and details refer to the vSwitchPerf user guide at:
http://artifacts.opnfv.org/vswitchperf/docs/userguide/index.html

