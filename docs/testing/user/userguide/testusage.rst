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
- T-Rex software traffic generator. Requires a separate machine running T-Rex
  Server to execute packet generation.

If you want to use another traffic generator, please select the :ref:`trafficgen-dummy`
generator.

VSPERF Installation
^^^^^^^^^^^^^^^^^^^

To see the supported Operating Systems, vSwitches and system requirements,
please follow the `installation instructions <vsperf-installation>`.

Traffic Generator Setup
^^^^^^^^^^^^^^^^^^^^^^^

Follow the `Traffic generator instructions <trafficgen-installation>` to
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
of options with ``GUEST_`` prefix could be found at :ref:`design document
<design-configuration>`.

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

1. Testcase definition section ``Parameters``
2. Command line arguments
3. Environment variables
4. Configuration file(s)

Further details about configuration files evaluation and special behaviour
of options with ``GUEST_`` prefix could be found at :ref:`design document
<design-configuration>`.

.. _overriding-parameters-documentation:

Referencing parameter values
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

It is possible to use a special macro ``#PARAM()`` to refer to the value of
another configuration parameter. This reference is evaluated during
access of the parameter value (by ``settings.getValue()`` call), so it
can refer to parameters created during VSPERF runtime, e.g. NICS dictionary.
It can be used to reflect DUT HW details in the testcase definition.

Example:

.. code:: python

    {
        ...
        "Name": "testcase",
        "Parameters" : {
            "TRAFFIC" : {
                'l2': {
                    # set destination MAC to the MAC of the first
                    # interface from WHITELIST_NICS list
                    'dstmac' : '#PARAM(NICS[0]["mac"])',
                },
            },
        ...

Overriding values defined in configuration files
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The configuration items can be overridden by command line argument
``--test-params``. In this case, the configuration items and
their values should be passed in form of ``item=value`` and separated
by semicolon.

Example:

.. code:: console

    $ ./vsperf --test-params "TRAFFICGEN_DURATION=10;TRAFFICGEN_PKT_SIZES=(128,);" \
                             "GUEST_LOOPBACK=['testpmd','l2fwd']" pvvp_tput

The ``--test-params`` command line argument can also be used to override default
configuration values for multiple tests. Providing a list of parameters will apply each
element of the list to the test with the same index. If more tests are run than
parameters provided the last element of the list will repeat.

.. code:: console

    $ ./vsperf --test-params "['TRAFFICGEN_DURATION=10;TRAFFICGEN_PKT_SIZES=(128,)',"
                             "'TRAFFICGEN_DURATION=10;TRAFFICGEN_PKT_SIZES=(64,)']" \
                             pvvp_tput pvvp_tput

The second option is to override configuration items by ``Parameters`` section
of the test case definition. The configuration items can be added into ``Parameters``
dictionary with their new values. These values will override values defined in
configuration files or specified by ``--test-params`` command line argument.

Example:

.. code:: python

    "Parameters" : {'TRAFFICGEN_PKT_SIZES' : (128,),
                    'TRAFFICGEN_DURATION' : 10,
                    'GUEST_LOOPBACK' : ['testpmd','l2fwd'],
                   }

**NOTE:** In both cases, configuration item names and their values must be specified
in the same form as they are defined inside configuration files. Parameter names
must be specified in uppercase and data types of original and new value must match.
Python syntax rules related to data types and structures must be followed.
For example, parameter ``TRAFFICGEN_PKT_SIZES`` above is defined as a tuple
with a single value ``128``. In this case trailing comma is mandatory, otherwise
value can be wrongly interpreted as a number instead of a tuple and vsperf
execution would fail. Please check configuration files for default values and their
types and use them as a basis for any customized values. In case of any doubt, please
check official python documentation related to data structures like tuples, lists
and dictionaries.

**NOTE:** Vsperf execution will terminate with runtime error in case, that unknown
parameter name is passed via ``--test-params`` CLI argument or defined in ``Parameters``
section of test case definition. It is also forbidden to redefine a value of
``TEST_PARAMS`` configuration item via CLI or ``Parameters`` section.

vloop_vnf
^^^^^^^^^

VSPERF uses a VM image called vloop_vnf for looping traffic in the deployment
scenarios involving VMs. The image can be downloaded from
`<http://artifacts.opnfv.org/>`__.

Please see the installation instructions for information on :ref:`vloop-vnf`
images.

.. _l2fwd-module:

l2fwd Kernel Module
^^^^^^^^^^^^^^^^^^^

A Kernel Module that provides OSI Layer 2 Ipv4 termination or forwarding with
support for Destination Network Address Translation (DNAT) for both the MAC and
IP addresses. l2fwd can be found in <vswitchperf_dir>/src/l2fwd

Additional Tools Setup
^^^^^^^^^^^^^^^^^^^^^^

Follow the `Additional tools instructions <additional-tools-configuration>` to
install and configure additional tools such as collectors and loadgens.

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

To run a test multiple times, repeat it:

.. code-block:: console

    $ ./vsperf $TESTNAME $TESTNAME $TESTNAME

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

    $ ./vsperf --conf-file user_settings.py \
        --tests RFC2544Tput \
        --test-params "TRAFFICGEN_DURATION=10;TRAFFICGEN_PKT_SIZES=(128,)"

To specify configurable parameters for multiple tests, use a list of
parameters. One element for each test.

.. code:: console

    $ ./vsperf --conf-file user_settings.py \
        --test-params "['TRAFFICGEN_DURATION=10;TRAFFICGEN_PKT_SIZES=(128,)',"\
        "'TRAFFICGEN_DURATION=10;TRAFFICGEN_PKT_SIZES=(64,)']" \
        phy2phy_cont phy2phy_cont

If the ``CUMULATIVE_PARAMS`` setting is set to True and there are different parameters
provided for each test using ``--test-params``, each test will take the parameters of
the previous test before appyling it's own.
With ``CUMULATIVE_PARAMS`` set to True the following command will be equivalent to the
previous example:

.. code:: console

    $ ./vsperf --conf-file user_settings.py \
        --test-params "['TRAFFICGEN_DURATION=10;TRAFFICGEN_PKT_SIZES=(128,)',"\
        "'TRAFFICGEN_PKT_SIZES=(64,)']" \
        phy2phy_cont phy2phy_cont
        "

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

2. Update your ``10_custom.conf`` file to use Vanilla OVS:

   .. code-block:: python

       VSWITCH = 'OvsVanilla'

3. Run test:

   .. code-block:: console

       $ ./vsperf --conf-file=<path_to_custom_conf>

   Please note if you don't want to configure Vanilla OVS through the
   configuration file, you can pass it as a CLI argument.

   .. code-block:: console

       $ ./vsperf --vswitch OvsVanilla


Executing tests with VMs
^^^^^^^^^^^^^^^^^^^^^^^^

To run tests using vhost-user as guest access method:

1. Set VSWITCH and VNF of your settings file to:

   .. code-block:: python

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

**NOTE:** By default vSwitch is acting as a server for dpdk vhost-user sockets.
In case, that QEMU should be a server for vhost-user sockets, then parameter
``VSWITCH_VHOSTUSER_SERVER_MODE`` should be set to ``False``.

Executing tests with VMs using Vanilla OVS
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

To run tests using Vanilla OVS:

1. Set the following variables:

   .. code-block:: python

       VSWITCH = 'OvsVanilla'
       VNF = 'QemuVirtioNet'

       VANILLA_TGEN_PORT1_IP = n.n.n.n
       VANILLA_TGEN_PORT1_MAC = nn:nn:nn:nn:nn:nn

       VANILLA_TGEN_PORT2_IP = n.n.n.n
       VANILLA_TGEN_PORT2_MAC = nn:nn:nn:nn:nn:nn

       VANILLA_BRIDGE_IP = n.n.n.n

   or use ``--test-params`` option

   .. code-block:: console

       $ ./vsperf --conf-file=<path_to_custom_conf>/10_custom.conf \
                  --test-params "VANILLA_TGEN_PORT1_IP=n.n.n.n;" \
                                "VANILLA_TGEN_PORT1_MAC=nn:nn:nn:nn:nn:nn;" \
                                "VANILLA_TGEN_PORT2_IP=n.n.n.n;" \
                                "VANILLA_TGEN_PORT2_MAC=nn:nn:nn:nn:nn:nn"

2. If needed, recompile src for all OVS variants

   .. code-block:: console

       $ cd src
       $ make distclean
       $ make

3. Run test:

   .. code-block:: console

       $ ./vsperf --conf-file<path_to_custom_conf>/10_custom.conf

.. _vpp-test:

Executing VPP tests
^^^^^^^^^^^^^^^^^^^

Currently it is not possible to use standard scenario deployments for execution of
tests with VPP. It means, that deployments ``p2p``, ``pvp``, ``pvvp`` and in general any
:ref:`pxp-deployment` won't work with VPP. However it is possible to use VPP in
:ref:`step-driven-tests`. A basic set of VPP testcases covering ``phy2phy``, ``pvp``
and ``pvvp`` tests are already prepared.

List of performance tests with VPP support follows:

* phy2phy_tput_vpp:              VPP: LTD.Throughput.RFC2544.PacketLossRatio
* phy2phy_cont_vpp:              VPP: Phy2Phy Continuous Stream
* phy2phy_back2back_vpp:         VPP: LTD.Throughput.RFC2544.BackToBackFrames
* pvp_tput_vpp:                  VPP: LTD.Throughput.RFC2544.PacketLossRatio
* pvp_cont_vpp:                  VPP: PVP Continuous Stream
* pvp_back2back_vpp:             VPP: LTD.Throughput.RFC2544.BackToBackFrames
* pvvp_tput_vpp:                 VPP: LTD.Throughput.RFC2544.PacketLossRatio
* pvvp_cont_vpp:                 VPP: PVP Continuous Stream
* pvvp_back2back_vpp:            VPP: LTD.Throughput.RFC2544.BackToBackFrames

In order to execute testcases with VPP it is required to:

* install VPP manually, see :ref:`vpp-installation`
* configure ``WHITELIST_NICS``, with two physical NICs connected to the traffic generator
* configure traffic generator, see :ref:`trafficgen-installation`

After that it is possible to execute VPP testcases listed above.

For example:

.. code-block:: console

    $ ./vsperf --conf-file=<path_to_custom_conf> phy2phy_tput_vpp

.. _vfio-pci:

Using vfio_pci with DPDK
^^^^^^^^^^^^^^^^^^^^^^^^^

To use vfio with DPDK instead of igb_uio add into your custom configuration
file the following parameter:

.. code-block:: python

    PATHS['dpdk']['src']['modules'] = ['uio', 'vfio-pci']


**NOTE:** In case, that DPDK is installed from binary package, then please
set ``PATHS['dpdk']['bin']['modules']`` instead.

**NOTE:** Please ensure that Intel VT-d is enabled in BIOS.

**NOTE:** Please ensure your boot/grub parameters include
the following:

**NOTE:** In case of VPP, it is required to explicitly define, that vfio-pci
DPDK driver should be used. It means to update dpdk part of VSWITCH_VPP_ARGS
dictionary with uio-driver section, e.g. VSWITCH_VPP_ARGS['dpdk'] = 'uio-driver vfio-pci'

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
* tests without vSwitch, where traffic is forwarded directly
  between VF interfaces by packet forwarder (e.g. testpmd application)
* tests without vSwitch, where VM accesses VF interfaces directly
  by PCI-passthrough_ to measure raw VM throughput performance.

.. _PCI-passthrough:

Using QEMU with PCI passthrough support
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Raw virtual machine throughput performance can be measured by execution of PVP
test with direct access to NICs by PCI pass-through. To execute VM with direct
access to PCI devices, enable vfio-pci_. In order to use virtual functions,
SRIOV-support_ must be enabled.

Execution of test with PCI pass-through with vswitch disabled:

.. code-block:: console

    $ ./vsperf --conf-file=<path_to_custom_conf>/10_custom.conf \
               --vswitch none --vnf QemuPciPassthrough pvp_tput

Any of supported guest-loopback-application_ can be used inside VM with
PCI pass-through support.

Note: Qemu with PCI pass-through support can be used only with PVP test
deployment.

.. _guest-loopback-application:

Selection of loopback application for tests with VMs
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

To select the loopback applications which will forward packets inside VMs,
the following parameter should be configured:

.. code-block:: python

     GUEST_LOOPBACK = ['testpmd']

or use ``--test-params`` CLI argument:

.. code-block:: console

        $ ./vsperf --conf-file=<path_to_custom_conf>/10_custom.conf \
              --test-params "GUEST_LOOPBACK=['testpmd']"

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

**NOTE:** In case that only 1 or more than 2 NICs are configured for VM,
then 'testpmd' should be used. As it is able to forward traffic between
multiple VM NIC pairs.

**NOTE:** In case of linux_bridge, all guest NICs are connected to the same
bridge inside the guest.

Mergable Buffers Options with QEMU
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Mergable buffers can be disabled with VSPerf within QEMU. This option can
increase performance significantly when not using jumbo frame sized packets.
By default VSPerf disables mergable buffers. If you wish to enable it you
can modify the setting in the a custom conf file.

.. code-block:: python

    GUEST_NIC_MERGE_BUFFERS_DISABLE = [False]

Then execute using the custom conf file.

.. code-block:: console

        $ ./vsperf --conf-file=<path_to_custom_conf>/10_custom.conf

Alternatively you can just pass the param during execution.

.. code-block:: console

        $ ./vsperf --test-params "GUEST_NIC_MERGE_BUFFERS_DISABLE=[False]"


Selection of dpdk binding driver for tests with VMs
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

To select dpdk binding driver, which will specify which driver the vm NICs will
use for dpdk bind, the following configuration parameter should be configured:

.. code-block:: console

     GUEST_DPDK_BIND_DRIVER = ['igb_uio_from_src']

The supported dpdk guest bind drivers are:

.. code-block:: console

    'uio_pci_generic'      - Use uio_pci_generic driver
    'igb_uio_from_src'     - Build and use the igb_uio driver from the dpdk src
                             files
    'vfio_no_iommu'        - Use vfio with no iommu option. This requires custom
                             guest images that support this option. The default
                             vloop image does not support this driver.

Note: uio_pci_generic does not support sr-iov testcases with guests attached.
This is because uio_pci_generic only supports legacy interrupts. In case
uio_pci_generic is selected with the vnf as QemuPciPassthrough it will be
modified to use igb_uio_from_src instead.

Note: vfio_no_iommu requires kernels equal to or greater than 4.5 and dpdk
16.04 or greater. Using this option will also taint the kernel.

Please refer to the dpdk documents at http://dpdk.org/doc/guides for more
information on these drivers.

Guest Core and Thread Binding
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

VSPERF provides options to achieve better performance by guest core binding and
guest vCPU thread binding as well. Core binding is to bind all the qemu threads.
Thread binding is to bind the house keeping threads to some CPU and vCPU thread to
some other CPU, this helps to reduce the noise from qemu house keeping threads.


.. code-block:: python

   GUEST_CORE_BINDING = [('#EVAL(6+2*#VMINDEX)', '#EVAL(7+2*#VMINDEX)')]

**NOTE** By default the GUEST_THREAD_BINDING will be none, which means same as
the GUEST_CORE_BINDING, i.e. the vcpu threads are sharing the physical CPUs with
the house keeping threads. Better performance using vCPU thread binding can be
achieved by enabling affinity in the custom configuration file.

For example, if an environment requires 32,33 to be core binded and 29,30&31 for
guest thread binding to achieve better performance.

.. code-block:: python

   VNF_AFFINITIZATION_ON = True
   GUEST_CORE_BINDING = [('32','33')]
   GUEST_THREAD_BINDING = [('29', '30', '31')]

Qemu CPU features
^^^^^^^^^^^^^^^^^

QEMU default to a compatible subset of performance enhancing cpu features.
To pass all available host processor features to the guest.

.. code-block:: python

   GUEST_CPU_OPTIONS = ['host,migratable=off']

**NOTE** To enhance the performance, cpu features tsc deadline timer for guest,
the guest PMU, the invariant TSC can be provided in the custom configuration file.

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

    .. code-block:: python

        OVS_OLD_STYLE_MQ = True

To enable multi-queue for dpdk modify the ''02_vswitch.conf'' file.

.. code-block:: python

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

.. code-block:: python

    GUEST_NIC_QUEUES = [2]

Enabling multi-queue at the guest will add multiple queues to each NIC port when
qemu launches the guest.

In case of Vanilla OVS, multi-queue is enabled on the tuntap ports and nic
queues will be enabled inside the guest with ethtool. Simply enabling the
multi-queue on the guest is sufficient for Vanilla OVS multi-queue.

Testpmd should be configured to take advantage of multi-queue on the guest if
using DPDKVhostUser. This can be done by modifying the ''04_vnf.conf'' file.

.. code-block:: python

    GUEST_TESTPMD_PARAMS = ['-l 0,1,2,3,4  -n 4 --socket-mem 512 -- '
                            '--burst=64 -i --txqflags=0xf00 '
                            '--nb-cores=4 --rxq=2 --txq=2 '
                            '--disable-hw-vlan']

**NOTE:** The guest SMP cores must be configured to allow for testpmd to use the
optimal number of cores to take advantage of the multiple guest queues.

In case of using Vanilla OVS and qemu virtio-net you can increase performance
by binding vhost-net threads to cpus. This can be done by enabling the affinity
in the ''04_vnf.conf'' file. This can be done to non multi-queue enabled
configurations as well as there will be 2 vhost-net threads.

.. code-block:: python

    VSWITCH_VHOST_NET_AFFINITIZATION = True

    VSWITCH_VHOST_CPU_MAP = [4,5,8,11]

**NOTE:** This method of binding would require a custom script in a real
environment.

**NOTE:** For optimal performance guest SMPs and/or vhost-net threads should be
on the same numa as the NIC in use if possible/applicable. Testpmd should be
assigned at least (nb_cores +1) total cores with the cpu mask.

Jumbo Frame Testing
^^^^^^^^^^^^^^^^^^^

VSPERF provides options to support jumbo frame testing with a jumbo frame supported
NIC and traffic generator for the following vswitches:

1.  OVSVanilla

2.  OvsDpdkVhostUser

3.  TestPMD loopback with or without a guest

**NOTE:** There is currently no support for SR-IOV or VPP at this time with jumbo
frames.

All packet forwarding applications for pxp testing is supported.

To enable jumbo frame testing simply enable the option in the conf files and set the
maximum size that will be used.

.. code-block:: python

    VSWITCH_JUMBO_FRAMES_ENABLED = True
    VSWITCH_JUMBO_FRAMES_SIZE = 9000

To enable jumbo frame testing with OVSVanilla the NIC in test on the host must have
its mtu size changed manually using ifconfig or applicable tools:

.. code-block:: console

    ifconfig eth1 mtu 9000 up

**NOTE:** To make the setting consistent across reboots you should reference the OS
documents as it differs from distribution to distribution.

To start a test for jumbo frames modify the conf file packet sizes or pass the option
through the VSPERF command line.

.. code-block:: python

    TEST_PARAMS = {'TRAFFICGEN_PKT_SIZES':(2000,9000)}

.. code-block:: python

    ./vsperf --test-params "TRAFFICGEN_PKT_SIZES=2000,9000"

It is recommended to increase the memory size for OvsDpdkVhostUser testing from the default
1024. Your size required may vary depending on the number of guests in your testing. 4096
appears to work well for most typical testing scenarios.

.. code-block:: python

    DPDK_SOCKET_MEM = ['4096', '0']

**NOTE:** For Jumbo frames to work with DpdkVhostUser, mergable buffers will be enabled by
default. If testing with mergable buffers in QEMU is desired, disable Jumbo Frames and only
test non jumbo frame sizes. Test Jumbo Frames sizes separately to avoid this collision.


Executing Packet Forwarding tests
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

To select the applications which will forward packets,
the following parameters should be configured:

.. code-block:: python

    VSWITCH = 'none'
    PKTFWD = 'TestPMD'

or use ``--vswitch`` and ``--fwdapp`` CLI arguments:

.. code-block:: console

    $ ./vsperf phy2phy_cont --conf-file user_settings.py \
               --vswitch none \
               --fwdapp TestPMD

Supported Packet Forwarding applications are:

.. code-block:: console

    'testpmd'       - testpmd from dpdk


1. Update your ''10_custom.conf'' file to use the appropriate variables
   for selected Packet Forwarder:

   .. code-block:: python

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

      $ ./vsperf phy2phy_tput --conf-file <path_to_settings_py>

Executing Packet Forwarding tests with one guest
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

TestPMD with DPDK 16.11 or greater can be used to forward packets as a switch to a single guest using TestPMD vdev
option. To set this configuration the following parameters should be used.

    .. code-block:: python

        VSWITCH = 'none'
        PKTFWD = 'TestPMD'

or use ``--vswitch`` and ``--fwdapp`` CLI arguments:

    .. code-block:: console

        $ ./vsperf pvp_tput --conf-file user_settings.py \
                   --vswitch none \
                   --fwdapp TestPMD

Guest forwarding application only supports TestPMD in this configuration.

    .. code-block:: python

        GUEST_LOOPBACK = ['testpmd']

For optimal performance one cpu per port +1 should be used for TestPMD. Also set additional params for packet forwarding
application to use the correct number of nb-cores.

    .. code-block:: python

        DPDK_SOCKET_MEM = ['1024', '0']
        VSWITCHD_DPDK_ARGS = ['-l', '46,44,42,40,38', '-n', '4']
        TESTPMD_ARGS = ['--nb-cores=4', '--txq=1', '--rxq=1']

For guest TestPMD 3 VCpus should be assigned with the following TestPMD params.

    .. code-block:: python

        GUEST_TESTPMD_PARAMS = ['-l 0,1,2 -n 4 --socket-mem 1024 -- '
                                '--burst=64 -i --txqflags=0xf00 '
                                '--disable-hw-vlan --nb-cores=2 --txq=1 --rxq=1']

Execution of TestPMD can be run with the following command line

    .. code-block:: console

        ./vsperf pvp_tput --vswitch=none --fwdapp=TestPMD --conf-file <path_to_settings_py>

**NOTE:** To achieve the best 0% loss numbers with rfc2544 throughput testing, other tunings should be applied to host
and guest such as tuned profiles and CPU tunings to prevent possible interrupts to worker threads.

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
of traffic generator can be modified through ``TRAFFIC`` dictionary passed to the
``--test-params`` option. It is not needed to specify all values of ``TRAFFIC``
dictionary. It is sufficient to specify only values, which should be changed.
Detailed description of ``TRAFFIC`` dictionary can be found at
:ref:`configuration-of-traffic-dictionary`.

Example of execution of VSPERF in "trafficgen" mode:

.. code-block:: console

    $ ./vsperf -m trafficgen --trafficgen IxNet --conf-file vsperf.conf \
        --test-params "TRAFFIC={'traffic_type':'rfc2544_continuous','bidir':'False','framerate':60}"

Performance Matrix
^^^^^^^^^^^^^^^^^^

The ``--matrix`` command line argument analyses and displays the performance of
all the tests run. Using the metric specified by ``MATRIX_METRIC`` in the conf-file,
the first test is set as the baseline and all the other tests are compared to it.
The ``MATRIX_METRIC`` must always refer to a numeric value to enable comparision.
A table, with the test ID, metric value, the change of the metric in %, testname
and the test parameters used for each test, is printed out as well as saved into the
results directory.

Example of 2 tests being compared using Performance Matrix:

.. code-block:: console

    $ ./vsperf --conf-file user_settings.py \
        --test-params "['TRAFFICGEN_PKT_SIZES=(64,)',"\
        "'TRAFFICGEN_PKT_SIZES=(128,)']" \
        phy2phy_cont phy2phy_cont --matrix

Example output:

.. code-block:: console

    +------+--------------+---------------------+----------+---------------------------------------+
    |   ID | Name         |   throughput_rx_fps |   Change | Parameters, CUMULATIVE_PARAMS = False |
    +======+==============+=====================+==========+=======================================+
    |    0 | phy2phy_cont |        23749000.000 |        0 | 'TRAFFICGEN_PKT_SIZES': [64]          |
    +------+--------------+---------------------+----------+---------------------------------------+
    |    1 | phy2phy_cont |        16850500.000 |  -29.048 | 'TRAFFICGEN_PKT_SIZES': [128]         |
    +------+--------------+---------------------+----------+---------------------------------------+


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

Custom image fails to boot
~~~~~~~~~~~~~~~~~~~~~~~~~~

Using custom VM images may not boot within VSPerf pxp testing because of
the drive boot and shared type which could be caused by a missing scsi
driver inside the image. In case of issues you can try changing the drive
boot type to ide.

.. code-block:: python

    GUEST_BOOT_DRIVE_TYPE = ['ide']
    GUEST_SHARED_DRIVE_TYPE = ['ide']

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

.. code-block:: python

    DPDK_SOCKET_MEM = ['1024', '0']
    VSWITCHD_DPDK_ARGS = ['-c', '0x4', '-n', '4']
    VSWITCHD_DPDK_CONFIG = {
        'dpdk-init' : 'true',
        'dpdk-lcore-mask' : '0x4',
        'dpdk-socket-mem' : '1024,0',
    }

Note: Option ``VSWITCHD_DPDK_ARGS`` is used for vswitchd, which supports ``--dpdk``
parameter. In recent vswitchd versions, option ``VSWITCHD_DPDK_CONFIG`` will be
used to configure vswitchd via ``ovs-vsctl`` calls.


More information
^^^^^^^^^^^^^^^^

For more information and details refer to the rest of vSwitchPerfuser documentation.

