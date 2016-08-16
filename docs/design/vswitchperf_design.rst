.. This work is licensed under a Creative Commons Attribution 4.0 International License.
.. http://creativecommons.org/licenses/by/4.0
.. (c) OPNFV, Intel Corporation, AT&T and others.

======================
VSPERF Design Document
======================

Intended Audience
=================

This document is intended to aid those who want to modify the vsperf code. Or
to extend it - for example to add support for new traffic generators,
deployment scenarios and so on.

Usage
=====

Example Connectivity to DUT
---------------------------

Establish connectivity to the VSPERF DUT Linux host, such as the DUT in Pod 3,
by following the steps in `Testbed POD3
<https://wiki.opnfv.org/get_started/pod_3_-_characterize_vswitch_performance>`__

The steps cover booking the DUT and establishing the VSPERF environment.

Example Command Lines
---------------------

List all the cli options:

.. code-block:: console

   $ ./vsperf -h

Run all tests that have ``tput`` in their name - ``phy2phy_tput``, ``pvp_tput`` etc.:

.. code-block:: console

   $ ./vsperf --tests 'tput'

As above but override default configuration with settings in '10_custom.conf'.
This is useful as modifying configuration directly in the configuration files
in ``conf/NN_*.py`` shows up as changes under git source control:

.. code-block:: console

   $ ./vsperf --conf-file=<path_to_custom_conf>/10_custom.conf --tests 'tput'

Override specific test parameters. Useful for shortening the duration of tests
for development purposes:

.. code-block:: console

   $ ./vsperf --test-params 'duration=10;rfc2544_tests=1;pkt_sizes=64' --tests 'pvp_tput'

Typical Test Sequence
=====================

This is a typical flow of control for a test.

.. image:: vsperf.png


Configuration
=============

The conf package contains the configuration files (``*.conf``) for all system
components, it also provides a ``settings`` object that exposes all of these
settings.

Settings are not passed from component to component. Rather they are available
globally to all components once they import the conf package.

.. code-block:: python

   from conf import settings
   ...
   log_file = settings.getValue('LOG_FILE_DEFAULT')

Settings files (``*.conf``) are valid python code so can be set to complex
types such as lists and dictionaries as well as scalar types:

.. code-block:: python

   first_packet_size = settings.getValue('PACKET_SIZE_LIST')[0]

Configuration Procedure and Precedence
--------------------------------------

Configuration files follow a strict naming convention that allows them to be
processed in a specific order. All the .conf files are named ``NN_name.conf``,
where NN is a decimal number. The files are processed in order from 00_name.conf
to 99_name.conf so that if the name setting is given in both a lower and higher
numbered conf file then the higher numbered file is the effective setting as it
is processed after the setting in the lower numbered file.

The values in the file specified by ``--conf-file`` takes precedence over all
the other configuration files and does not have to follow the naming
convention.

Configuration of GUEST options
------------------------------

VSPERF is able to setup scenarios involving a large number of VMs.
All configuration options related to a particular VM instance are defined as
lists and prefixed with ``GUEST_`` label. It is essential, that there is enough
items in all ``GUEST_`` options to cover all VM instances involved in the test.
In case there is not enough items, then VSPERF will use the first item of
particular ``GUEST_`` option to expand the list to required length. First option
can contain macros starting with ``#`` to generate VM specific values. These
macros can be used only for options of ``list`` or ``str`` types with ``GUEST_``
prefix. There are several examples in ``04_vnf.conf``.

Multiple macros can be used inside one configuration option definition, but macros
cannot be used inside other macros. The only exception is macro ``#VMINDEX``, which
is expanded first and thus it can be used inside other macros.

Following macros are supported:

  * ``#VMINDEX`` - it is replaced by index of VM being executed; This macro
    is expanded first, so it can be used inside other macros.

    Example:

    .. code-block:: python

       GUEST_SHARE_DIR = ['/tmp/qemu#VMINDEX_share']

  * ``#MAC(mac_address[, step])`` - it will iterate given ``mac_address``
    with optional ``step``. In case that step is not defined, then it is set to 1.
    It means, that first VM will use the value of ``mac_address``, second VM
    value of ``mac_address`` increased by ``step``, etc.

    Example:

    .. code-block:: python

       GUEST_NICS = [[{'mac' : '#MAC(00:00:00:00:00:01,2)'}]]

  * ``#IP(ip_address[, step])`` - it will iterate given ``ip_address``
    with optional ``step``. In case that step is not defined, then it is set to 1.
    It means, that first VM will use the value of ``ip_address``, second VM
    value of ``ip_address`` increased by ``step``, etc.

    Example:

    .. code-block:: python

       GUEST_BRIDGE_IP = ['#IP(1.1.1.5)/16']

  * ``#EVAL(expression)`` - it will evaluate given ``expression`` as python code;
    Only simple expressions should be used. Call of the functions is not supported.

    Example:

    .. code-block:: python

       GUEST_CORE_BINDING = [('#EVAL(6+2*#VMINDEX)', '#EVAL(7+2*#VMINDEX)')]

Other Configuration
-------------------

``conf.settings`` also loads configuration from the command line and from the environment.

PXP Deployment
==============

Every testcase uses one of the supported deployment scenarios to setup vSwitch.
The controller responsible for given scenario configures flows to route
traffic among physical interfaces connected to the traffic generator and virtual
machines. VSPERF supports several deployments including PXP deployment, which can
setup various scenarios with multiple VMs.

It is implemented by VswitchControllerPXP class, which can execute given number
of VMs in serial or parallel configuration. Every VM can be configured with
just one or even number of interfaces. In case that VM has more than 2 interfaces,
then traffic is properly routed among interfaces pairs. It is also possible to
define different number of interfaces for each VM to better simulate real
scenarios.

The number of VMs involved in the test and the type of their connection is defined
by deployment name as follows:

  * ``pvvp[number]`` - configures scenario with VMs connected in serial with
    optional ``number`` of VMs. In case that ``number`` is not specified, then
    2 VMs will be used.
  * ``pvpv[number]`` - configures scenario with VMs connected in parallel with
    optional ``number`` of VMs. In case that ``number`` is not specified, then
    2 VMs will be used. Multistream feature is used to route traffic to particular
    VMs (or NIC pairs of every VM). It means, that VSPERF will enable multistream
    feaure and sets the number of streams to the number of VMs and their NIC
    pairs. Traffic will be dispatched based on Stream Type, i.e. by UDP port,
    IP address or MAC address.

PXP deployment is backward compatible with PVP deployment, where ``pvp`` is
an alias for ``pvvp1`` and it executes just one VM.

The number of interfaces used by VMs is defined by configuration option
``GUEST_NICS_NR``. In case that more than one pair of interfaces is defined
for VM, then:

    * for ``pvvp`` (serial) scenario every NIC pair is connected in serial
      before connection to next VM is created
    * for ``pvpv`` (parallel) scenario every NIC pair is directly connected
      to the physical ports and unique traffic stream is assigned to it

Examples:

    * Deployment ``pvvp10`` will start 10 VMs and connects them in series
    * Deployment ``pvpv4`` will start 4 VMs and connects them in parallel
    * Deployment ``pvpv1`` and GUEST_NICS_NR = [4] will start 1 VM with
      4 interfaces and every NIC pair is directly connected to the
      physical ports
    * Deployment ``pvvp`` and GUEST_NICS_NR = [2, 4] will start 2 VMs;
      1st VM will have 2 interfaces and 2nd VM 4 interfaces. These interfaces
      will be connected in serial, i.e. traffic will flow as follows:
      PHY1 -> VM1_1 -> VM1_2 -> VM2_1 -> VM2_2 -> VM2_3 -> VM2_4 -> PHY2

Note: In case that only 1 or more than 2 NICs are configured for VM,
then ``testpmd`` should be used as forwarding application inside the VM.
As it is able to forward traffic between multiple VM NIC pairs.

Note: In case of ``linux_bridge``, all NICs are connected to the same
bridge inside the VM.

VM, vSwitch, Traffic Generator Independence
===========================================

VSPERF supports different vSwithes, Traffic Generators, VNFs
and Forwarding Applications by using standard object-oriented polymorphism:

  * Support for vSwitches is implemented by a class inheriting from IVSwitch.
  * Support for Traffic Generators is implemented by a class inheriting from
    ITrafficGenerator.
  * Support for VNF is implemented by a class inheriting from IVNF.
  * Support for Forwarding Applications is implemented by a class inheriting
    from IPktFwd.

By dealing only with the abstract interfaces the core framework can support
many implementations of different vSwitches, Traffic Generators, VNFs
and Forwarding Applications.

IVSwitch
--------

.. code-block:: python

    class IVSwitch:
      start(self)
      stop(self)
      add_switch(switch_name)
      del_switch(switch_name)
      add_phy_port(switch_name)
      add_vport(switch_name)
      get_ports(switch_name)
      del_port(switch_name, port_name)
      add_flow(switch_name, flow)
      del_flow(switch_name, flow=None)

ITrafficGenerator
-----------------

.. code-block:: python

    class ITrafficGenerator:
      connect()
      disconnect()

      send_burst_traffic(traffic, numpkts, time, framerate)

      send_cont_traffic(traffic, time, framerate)
      start_cont_traffic(traffic, time, framerate)
      stop_cont_traffic(self):

      send_rfc2544_throughput(traffic, tests, duration, lossrate)
      start_rfc2544_throughput(traffic, tests, duration, lossrate)
      wait_rfc2544_throughput(self)

      send_rfc2544_back2back(traffic, tests, duration, lossrate)
      start_rfc2544_back2back(traffic, , tests, duration, lossrate)
      wait_rfc2544_back2back()

Note ``send_xxx()`` blocks whereas ``start_xxx()`` does not and must be followed by a subsequent call to ``wait_xxx()``.

IVnf
----

.. code-block:: python

    class IVnf:
      start(memory, cpus,
            monitor_path, shared_path_host,
            shared_path_guest, guest_prompt)
      stop()
      execute(command)
      wait(guest_prompt)
      execute_and_wait (command)

IPktFwd
--------

  .. code-block:: python

    class IPktFwd:
        start()
        stop()


Controllers
-----------

Controllers are used in conjunction with abstract interfaces as way
of decoupling the control of vSwtiches, VNFs, TrafficGenerators
and Forwarding Applications from other components.

The controlled classes provide basic primitive operations. The Controllers
sequence and co-ordinate these primitive operation in to useful actions. For
instance the vswitch_controller_p2p can be used to bring any vSwitch (that
implements the primitives defined in IVSwitch) into the configuration required
by the Phy-to-Phy  Deployment Scenario.

In order to support a new vSwitch only a new implementation of IVSwitch needs
be created for the new vSwitch to be capable of fulfilling all the Deployment
Scenarios provided for by existing or future vSwitch Controllers.

Similarly if a new Deployment Scenario is required it only needs to be written
once as a new vSwitch Controller and it will immediately be capable of
controlling all existing and future vSwitches in to that Deployment Scenario.

Similarly the Traffic Controllers can be used to co-ordinate basic operations
provided by implementers of ITrafficGenerator to provide useful tests. Though
traffic generators generally already implement full test cases i.e. they both
generate suitable traffic and analyse returned traffic in order to implement a
test which has typically been predefined in an RFC document. However the
Traffic Controller class allows for the possibility of further enhancement -
such as iterating over tests for various packet sizes or creating new tests.

Traffic Controller's Role
-------------------------

.. image:: traffic_controller.png


Loader & Component Factory
--------------------------

The working of the Loader package (which is responsible for *finding* arbitrary
classes based on configuration data) and the Component Factory which is
responsible for *choosing* the correct class for a particular situation - e.g.
Deployment Scenario can be seen in this diagram.

.. image:: factory_and_loader.png

Routing Tables
==============

Vsperf uses a standard set of routing tables in order to allow tests to easily
mix and match Deployment Scenarios (PVP, P2P topology), Tuple Matching and
Frame Modification requirements.

.. code-block:: console

      +--------------+
      |              |
      | Table 0      |  table#0 - Match table. Flows designed to force 5 & 10
      |              |  tuple matches go here.
      |              |
      +--------------+
             |
             |
             v
      +--------------+  table#1 - Routing table. Flow entries to forward
      |              |  packets between ports goes here.
      | Table 1      |  The chosen port is communicated to subsequent tables by
      |              |  setting the metadata value to the egress port number.
      |              |  Generally this table is set-up by by the
      +--------------+  vSwitchController.
             |
             |
             v
      +--------------+  table#2 - Frame modification table. Frame modification
      |              |  flow rules are isolated in this table so that they can
      | Table 2      |  be turned on or off without affecting the routing or
      |              |  tuple-matching flow rules. This allows the frame
      |              |  modification and tuple matching required by the tests
      |              |  in the VSWITCH PERFORMANCE FOR TELCO NFV test
      +--------------+  specification to be independent of the Deployment
             |          Scenario set up by the vSwitchController.
             |
             v
      +--------------+
      |              |
      | Table 3      |  table#3 - Egress table. Egress packets on the ports
      |              |  setup in Table 1.
      +--------------+


