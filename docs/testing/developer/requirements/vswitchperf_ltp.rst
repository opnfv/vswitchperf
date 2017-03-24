.. This work is licensed under a Creative Commons Attribution 4.0 International License.
.. http://creativecommons.org/licenses/by/4.0
.. (c) OPNFV, Intel Corporation, AT&T and others.

.. 3.1

*****************************
VSPERF LEVEL TEST PLAN (LTP)
*****************************

===============
Introduction
===============

The objective of the OPNFV project titled
**Characterize vSwitch Performance for Telco NFV Use Cases**, is to
evaluate the performance of virtual switches to identify its suitability for a
Telco Network Function Virtualization (NFV) environment. The intention of this
Level Test Plan (LTP) document is to specify the scope, approach, resources,
and schedule of the virtual switch performance benchmarking activities in
OPNFV. The test cases will be identified in a separate document called the
Level Test Design (LTD) document.

This document is currently in draft form.

.. 3.1.1


.. _doc-id:

Document identifier
=========================

The document id will be used to uniquely identify versions of the LTP. The
format for the document id will be: OPNFV\_vswitchperf\_LTP\_REL\_STATUS, where
by the status is one of: draft, reviewed, corrected or final. The document id
for this version of the LTP is: OPNFV\_vswitchperf\_LTP\_Colorado\_REVIEWED.

.. 3.1.2

.. _scope:

Scope
==========

The main purpose of this project is to specify a suite of
performance tests in order to objectively measure the current packet
transfer characteristics of a virtual switch in the NFVI. The intent of
the project is to facilitate the performance testing of any virtual switch.
Thus, a generic suite of tests shall be developed, with no hard dependencies to
a single implementation. In addition, the test case suite shall be
architecture independent.

The test cases developed in this project shall not form part of a
separate test framework, all of these tests may be inserted into the
Continuous Integration Test Framework and/or the Platform Functionality
Test Framework - if a vSwitch becomes a standard component of an OPNFV
release.

.. 3.1.3

References
===============

*  `RFC 1242 Benchmarking Terminology for Network Interconnection
   Devices <http://www.ietf.org/rfc/rfc1242.txt>`__
*  `RFC 2544 Benchmarking Methodology for Network Interconnect
   Devices <http://www.ietf.org/rfc/rfc2544.txt>`__
*  `RFC 2285 Benchmarking Terminology for LAN Switching
   Devices <http://www.ietf.org/rfc/rfc2285.txt>`__
*  `RFC 2889 Benchmarking Methodology for LAN Switching
   Devices <http://www.ietf.org/rfc/rfc2889.txt>`__
*  `RFC 3918 Methodology for IP Multicast
   Benchmarking <http://www.ietf.org/rfc/rfc3918.txt>`__
*  `RFC 4737 Packet Reordering
   Metrics <http://www.ietf.org/rfc/rfc4737.txt>`__
*  `RFC 5481 Packet Delay Variation Applicability
   Statement <http://www.ietf.org/rfc/rfc5481.txt>`__
*  `RFC 6201 Device Reset
   Characterization <http://tools.ietf.org/html/rfc6201>`__

.. 3.1.4

Level in the overall sequence
===============================
The level of testing conducted by vswitchperf in the overall testing sequence (among
all the testing projects in OPNFV) is the performance benchmarking of a
specific component (the vswitch) in the OPNFV platfrom. It's expected that this
testing will follow on from the functional and integration testing conducted by
other testing projects in OPNFV, namely Functest and Yardstick.

.. 3.1.5

Test classes and overall test conditions
=========================================
A benchmark is defined by the IETF as: A standardized test that serves as a
basis for performance evaluation and comparison. It's important to note that
benchmarks are not Functional tests. They do not provide PASS/FAIL criteria,
and most importantly ARE NOT performed on live networks, or performed with live
network traffic.

In order to determine the packet transfer characteristics of a virtual switch,
the benchmarking tests will be broken down into the following categories:

- **Throughput Tests** to measure the maximum forwarding rate (in
  frames per second or fps) and bit rate (in Mbps) for a constant load
  (as defined by `RFC1242 <https://www.rfc-editor.org/rfc/rfc1242.txt>`__)
  without traffic loss.
- **Packet and Frame Delay Tests** to measure average, min and max
  packet and frame delay for constant loads.
- **Stream Performance Tests** (TCP, UDP) to measure bulk data transfer
  performance, i.e. how fast systems can send and receive data through
  the virtual switch.
- **Request/Response Performance** Tests (TCP, UDP) the measure the
  transaction rate through the virtual switch.
- **Packet Delay Tests** to understand latency distribution for
  different packet sizes and over an extended test run to uncover
  outliers.
- **Scalability Tests** to understand how the virtual switch performs
  as the number of flows, active ports, complexity of the forwarding
  logic's configuration... it has to deal with increases.
- **Control Path and Datapath Coupling** Tests, to understand how
  closely coupled the datapath and the control path are as well as the
  effect of this coupling on the performance of the DUT.
- **CPU and Memory Consumption Tests** to understand the virtual
  switch’s footprint on the system, this includes:

  * CPU core utilization.
  * CPU cache utilization.
  * Memory footprint.
  * System bus (QPI, PCI, ..) utilization.
  * Memory lanes utilization.
  * CPU cycles consumed per packet.
  * Time To Establish Flows Tests.

- **Noisy Neighbour Tests**, to understand the effects of resource
  sharing on the performance of a virtual switch.

**Note:** some of the tests above can be conducted simultaneously where
the combined results would be insightful, for example Packet/Frame Delay
and Scalability.



.. 3.2

.. _details-of-LTP:

===================================
Details of the Level Test Plan
===================================

This section describes the following items:
* Test items and their identifiers (TestItems_)
* Test Traceability Matrix (TestMatrix_)
* Features to be tested (FeaturesToBeTested_)
* Features not to be tested (FeaturesNotToBeTested_)
* Approach (Approach_)
* Item pass/fail criteria (PassFailCriteria_)
* Suspension criteria and resumption requirements (SuspensionResumptionReqs_)

.. 3.2.1

.. _TestItems:

Test items and their identifiers
==================================
The test item/application vsperf is trying to test are virtual switches and in
particular their performance in an nfv environment. vsperf will first try to
measure the maximum achievable performance by a virtual switch and then it will
focus in on usecases that are as close to real life deployment scenarios as
possible.

.. 3.2.2

.. _TestMatrix:

Test Traceability Matrix
==========================
vswitchperf leverages the "3x3" matrix (introduced in
https://tools.ietf.org/html/draft-ietf-bmwg-virtual-net-02) to achieve test
traceability. The matrix was expanded to 3x4 to accommodate scale metrics when
displaying the coverage of many metrics/benchmarks). Test case covreage in the
LTD is tracked using the following catagories:


+---------------+-------------+------------+---------------+-------------+
|               |             |            |               |             |
|               |   SPEED     |  ACCURACY  |  RELIABILITY  |    SCALE    |
|               |             |            |               |             |
+---------------+-------------+------------+---------------+-------------+
|               |             |            |               |             |
|  Activation   |      X      |     X      |       X       |      X      |
|               |             |            |               |             |
+---------------+-------------+------------+---------------+-------------+
|               |             |            |               |             |
|  Operation    |      X      |      X     |       X       |      X      |
|               |             |            |               |             |
+---------------+-------------+------------+---------------+-------------+
|               |             |            |               |             |
| De-activation |             |            |               |             |
|               |             |            |               |             |
+---------------+-------------+------------+---------------+-------------+

X = denotes a test catagory that has 1 or more test cases defined.

.. 3.2.3

.. _FeaturesToBeTested:

Features to be tested
==========================

Characterizing virtual switches (i.e. Device Under Test (DUT) in this document)
includes measuring the following performance metrics:

- **Throughput** as defined by `RFC1242
  <https://www.rfc-editor.org/rfc/rfc1242.txt>`__: The maximum rate at which
  **none** of the offered frames are dropped by the DUT. The maximum frame
  rate and bit rate that can be transmitted by the DUT without any error
  should be recorded. Note there is an equivalent bit rate and a specific
  layer at which the payloads contribute to the bits. Errors and
  improperly formed frames or packets are dropped.
- **Packet delay** introduced by the DUT and its cumulative effect on
  E2E networks. Frame delay can be measured equivalently.
- **Packet delay variation**: measured from the perspective of the
  VNF/application. Packet delay variation is sometimes called "jitter".
  However, we will avoid the term "jitter" as the term holds different
  meaning to different groups of people. In this document we will
  simply use the term packet delay variation. The preferred form for this
  metric is the PDV form of delay variation defined in `RFC5481
  <https://www.rfc-editor.org/rfc/rfc5481.txt>`__. The most relevant
  measurement of PDV considers the delay variation of a single user flow,
  as this will be relevant to the size of end-system buffers to compensate
  for delay variation. The measurement system's ability to store the
  delays of individual packets in the flow of interest is a key factor
  that determines the specific measurement method. At the outset, it is
  ideal to view the complete PDV distribution. Systems that can capture
  and store packets and their delays have the freedom to calculate the
  reference minimum delay and to determine various quantiles of the PDV
  distribution accurately (in post-measurement processing routines).
  Systems without storage must apply algorithms to calculate delay and
  statistical measurements on the fly. For example, a system may store
  temporary estimates of the mimimum delay and the set of (100) packets
  with the longest delays during measurement (to calculate a high quantile,
  and update these sets with new values periodically.
  In some cases, a limited number of delay histogram bins will be
  available, and the bin limits will need to be set using results from
  repeated experiments. See section 8 of `RFC5481
  <https://www.rfc-editor.org/rfc/rfc5481.txt>`__.
- **Packet loss** (within a configured waiting time at the receiver): All
  packets sent to the DUT should be accounted for.
- **Burst behaviour**: measures the ability of the DUT to buffer packets.
- **Packet re-ordering**: measures the ability of the device under test to
  maintain sending order throughout transfer to the destination.
- **Packet correctness**: packets or Frames must be well-formed, in that
  they include all required fields, conform to length requirements, pass
  integrity checks, etc.
- **Availability and capacity** of the DUT i.e. when the DUT is fully “up”
  and connected, following measurements should be captured for
  DUT without any network packet load:

  - Includes average power consumption of the CPUs (in various power states) and
    system over specified period of time. Time period should not be less
    than 60 seconds.
  - Includes average per core CPU utilization over specified period of time.
    Time period should not be less than 60 seconds.
  - Includes the number of NIC interfaces supported.
  - Includes headroom of VM workload processing cores (i.e. available
    for applications).

.. 3.2.4

.. _FeaturesNotToBeTested:

Features not to be tested
==========================
vsperf doesn't intend to define or perform any functional tests. The aim is to
focus on performance.

.. 3.2.5

.. _Approach:

Approach
==============
The testing approach adoped by the vswitchperf project is black box testing,
meaning the test inputs can be generated and the outputs captured and
completely evaluated from the outside of the System Under Test. Some metrics
can be collected on the SUT, such as cpu or memory utilization if the
collection has no/minimal impact on benchmark.
This section will look at the deployment scenarios and the general methodology
used by vswitchperf. In addition, this section will also specify the details of
the Test Report that must be collected for each of the test cases.

.. 3.2.5.1

Deployment Scenarios
--------------------------
The following represents possible deployment test scenarios which can
help to determine the performance of both the virtual switch and the
datapaths to physical ports (to NICs) and to logical ports (to VNFs):

.. 3.2.5.1.1

.. _Phy2Phy:

Physical port → vSwitch → physical port
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
.. code-block:: console

                                                            _
       +--------------------------------------------------+  |
       |              +--------------------+              |  |
       |              |                    |              |  |
       |              |                    v              |  |  Host
       |   +--------------+            +--------------+   |  |
       |   |   phy port   |  vSwitch   |   phy port   |   |  |
       +---+--------------+------------+--------------+---+ _|
                  ^                           :
                  |                           |
                  :                           v
       +--------------------------------------------------+
       |                                                  |
       |                traffic generator                 |
       |                                                  |
       +--------------------------------------------------+

.. 3.2.5.1.2

.. _PVP:

Physical port → vSwitch → VNF → vSwitch → physical port
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
.. code-block:: console

                                                             _
       +---------------------------------------------------+  |
       |                                                   |  |
       |   +-------------------------------------------+   |  |
       |   |                 Application               |   |  |
       |   +-------------------------------------------+   |  |
       |       ^                                  :        |  |
       |       |                                  |        |  |  Guest
       |       :                                  v        |  |
       |   +---------------+           +---------------+   |  |
       |   | logical port 0|           | logical port 1|   |  |
       +---+---------------+-----------+---------------+---+ _|
               ^                                  :
               |                                  |
               :                                  v         _
       +---+---------------+----------+---------------+---+  |
       |   | logical port 0|          | logical port 1|   |  |
       |   +---------------+          +---------------+   |  |
       |       ^                                  :       |  |
       |       |                                  |       |  |  Host
       |       :                                  v       |  |
       |   +--------------+            +--------------+   |  |
       |   |   phy port   |  vSwitch   |   phy port   |   |  |
       +---+--------------+------------+--------------+---+ _|
                  ^                           :
                  |                           |
                  :                           v
       +--------------------------------------------------+
       |                                                  |
       |                traffic generator                 |
       |                                                  |
       +--------------------------------------------------+

.. 3.2.5.1.3

.. _PVVP:

Physical port → vSwitch → VNF → vSwitch → VNF → vSwitch → physical port
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: console

                                                       _
    +----------------------+  +----------------------+  |
    |   Guest 1            |  |   Guest 2            |  |
    |   +---------------+  |  |   +---------------+  |  |
    |   |  Application  |  |  |   |  Application  |  |  |
    |   +---------------+  |  |   +---------------+  |  |
    |       ^       |      |  |       ^       |      |  |
    |       |       v      |  |       |       v      |  |  Guests
    |   +---------------+  |  |   +---------------+  |  |
    |   | logical ports |  |  |   | logical ports |  |  |
    |   |   0       1   |  |  |   |   0       1   |  |  |
    +---+---------------+--+  +---+---------------+--+ _|
            ^       :                 ^       :
            |       |                 |       |
            :       v                 :       v        _
    +---+---------------+---------+---------------+--+  |
    |   |   0       1   |         |   3       4   |  |  |
    |   | logical ports |         | logical ports |  |  |
    |   +---------------+         +---------------+  |  |
    |       ^       |                 ^       |      |  |  Host
    |       |       L-----------------+       v      |  |
    |   +--------------+          +--------------+   |  |
    |   |   phy ports  | vSwitch  |   phy ports  |   |  |
    +---+--------------+----------+--------------+---+ _|
            ^       ^                 :       :
            |       |                 |       |
            :       :                 v       v
    +--------------------------------------------------+
    |                                                  |
    |                traffic generator                 |
    |                                                  |
    +--------------------------------------------------+

.. 3.2.5.1.4

Physical port → VNF → vSwitch → VNF → physical port
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: console

                                                        _
    +----------------------+  +----------------------+   |
    |   Guest 1            |  |   Guest 2            |   |
    |+-------------------+ |  | +-------------------+|   |
    ||     Application   | |  | |     Application   ||   |
    |+-------------------+ |  | +-------------------+|   |
    |       ^       |      |  |       ^       |      |   |  Guests
    |       |       v      |  |       |       v      |   |
    |+-------------------+ |  | +-------------------+|   |
    ||   logical ports   | |  | |   logical ports   ||   |
    ||  0              1 | |  | | 0              1  ||   |
    ++--------------------++  ++--------------------++  _|
        ^              :          ^              :
    (PCI passthrough)  |          |     (PCI passthrough)
        |              v          :              |      _
    +--------++------------+-+------------++---------+   |
    |   |    ||        0   | |    1       ||     |   |   |
    |   |    ||logical port| |logical port||     |   |   |
    |   |    |+------------+ +------------+|     |   |   |
    |   |    |     |                 ^     |     |   |   |
    |   |    |     L-----------------+     |     |   |   |
    |   |    |                             |     |   |   |  Host
    |   |    |           vSwitch           |     |   |   |
    |   |    +-----------------------------+     |   |   |
    |   |                                        |   |   |
    |   |                                        v   |   |
    | +--------------+              +--------------+ |   |
    | | phy port/VF  |              | phy port/VF  | |   |
    +-+--------------+--------------+--------------+-+  _|
        ^                                        :
        |                                        |
        :                                        v
    +--------------------------------------------------+
    |                                                  |
    |                traffic generator                 |
    |                                                  |
    +--------------------------------------------------+

.. 3.2.5.1.5

Physical port → vSwitch → VNF
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: console

                                                          _
    +---------------------------------------------------+  |
    |                                                   |  |
    |   +-------------------------------------------+   |  |
    |   |                 Application               |   |  |
    |   +-------------------------------------------+   |  |
    |       ^                                           |  |
    |       |                                           |  |  Guest
    |       :                                           |  |
    |   +---------------+                               |  |
    |   | logical port 0|                               |  |
    +---+---------------+-------------------------------+ _|
            ^
            |
            :                                            _
    +---+---------------+------------------------------+  |
    |   | logical port 0|                              |  |
    |   +---------------+                              |  |
    |       ^                                          |  |
    |       |                                          |  |  Host
    |       :                                          |  |
    |   +--------------+                               |  |
    |   |   phy port   |  vSwitch                      |  |
    +---+--------------+------------ -------------- ---+ _|
               ^
               |
               :
    +--------------------------------------------------+
    |                                                  |
    |                traffic generator                 |
    |                                                  |
    +--------------------------------------------------+

.. 3.2.5.1.6

VNF → vSwitch → physical port
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: console

                                                          _
    +---------------------------------------------------+  |
    |                                                   |  |
    |   +-------------------------------------------+   |  |
    |   |                 Application               |   |  |
    |   +-------------------------------------------+   |  |
    |                                          :        |  |
    |                                          |        |  |  Guest
    |                                          v        |  |
    |                               +---------------+   |  |
    |                               | logical port  |   |  |
    +-------------------------------+---------------+---+ _|
                                               :
                                               |
                                               v         _
    +------------------------------+---------------+---+  |
    |                              | logical port  |   |  |
    |                              +---------------+   |  |
    |                                          :       |  |
    |                                          |       |  |  Host
    |                                          v       |  |
    |                               +--------------+   |  |
    |                     vSwitch   |   phy port   |   |  |
    +-------------------------------+--------------+---+ _|
                                           :
                                           |
                                           v
    +--------------------------------------------------+
    |                                                  |
    |                traffic generator                 |
    |                                                  |
    +--------------------------------------------------+

.. 3.2.5.1.7

VNF → vSwitch → VNF → vSwitch
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: console

                                                             _
    +-------------------------+  +-------------------------+  |
    |   Guest 1               |  |   Guest 2               |  |
    |   +-----------------+   |  |   +-----------------+   |  |
    |   |   Application   |   |  |   |   Application   |   |  |
    |   +-----------------+   |  |   +-----------------+   |  |
    |                :        |  |       ^                 |  |
    |                |        |  |       |                 |  |  Guest
    |                v        |  |       :                 |  |
    |     +---------------+   |  |   +---------------+     |  |
    |     | logical port 0|   |  |   | logical port 0|     |  |
    +-----+---------------+---+  +---+---------------+-----+ _|
                    :                    ^
                    |                    |
                    v                    :                    _
    +----+---------------+------------+---------------+-----+  |
    |    |     port 0    |            |     port 1    |     |  |
    |    +---------------+            +---------------+     |  |
    |              :                    ^                   |  |
    |              |                    |                   |  |  Host
    |              +--------------------+                   |  |
    |                                                       |  |
    |                     vswitch                           |  |
    +-------------------------------------------------------+ _|

.. 3.2.5.1.8

HOST 1(Physical port → virtual switch → VNF → virtual switch → Physical port)
→ HOST 2(Physical port → virtual switch → VNF → virtual switch → Physical port)

HOST 1 (PVP) → HOST 2 (PVP)
~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: console

                                                       _
    +----------------------+  +----------------------+  |
    |   Guest 1            |  |   Guest 2            |  |
    |   +---------------+  |  |   +---------------+  |  |
    |   |  Application  |  |  |   |  Application  |  |  |
    |   +---------------+  |  |   +---------------+  |  |
    |       ^       |      |  |       ^       |      |  |
    |       |       v      |  |       |       v      |  |  Guests
    |   +---------------+  |  |   +---------------+  |  |
    |   | logical ports |  |  |   | logical ports |  |  |
    |   |   0       1   |  |  |   |   0       1   |  |  |
    +---+---------------+--+  +---+---------------+--+ _|
            ^       :                 ^       :
            |       |                 |       |
            :       v                 :       v        _
    +---+---------------+--+  +---+---------------+--+  |
    |   |   0       1   |  |  |   |   3       4   |  |  |
    |   | logical ports |  |  |   | logical ports |  |  |
    |   +---------------+  |  |   +---------------+  |  |
    |       ^       |      |  |       ^       |      |  |  Hosts
    |       |       v      |  |       |       v      |  |
    |   +--------------+   |  |   +--------------+   |  |
    |   |   phy ports  |   |  |   |   phy ports  |   |  |
    +---+--------------+---+  +---+--------------+---+ _|
            ^       :                 :       :
            |       +-----------------+       |
            :                                 v
    +--------------------------------------------------+
    |                                                  |
    |                traffic generator                 |
    |                                                  |
    +--------------------------------------------------+



**Note:** For tests where the traffic generator and/or measurement
receiver are implemented on VM and connected to the virtual switch
through vNIC, the issues of shared resources and interactions between
the measurement devices and the device under test must be considered.

**Note:** Some RFC 2889 tests require a full-mesh sending and receiving
pattern involving more than two ports. This possibility is illustrated in the
Physical port → vSwitch → VNF → vSwitch → VNF → vSwitch → physical port
diagram above (with 2 sending and 2 receiving ports, though all ports
could be used bi-directionally).

**Note:** When Deployment Scenarios are used in RFC 2889 address learning
or cache capacity testing, an additional port from the vSwitch must be
connected to the test device. This port is used to listen for flooded
frames.

.. 3.2.5.2

General Methodology:
--------------------------
To establish the baseline performance of the virtual switch, tests would
initially be run with a simple workload in the VNF (the recommended
simple workload VNF would be `DPDK <http://www.dpdk.org/>`__'s testpmd
application forwarding packets in a VM or vloop\_vnf a simple kernel
module that forwards traffic between two network interfaces inside the
virtualized environment while bypassing the networking stack).
Subsequently, the tests would also be executed with a real Telco
workload running in the VNF, which would exercise the virtual switch in
the context of higher level Telco NFV use cases, and prove that its
underlying characteristics and behaviour can be measured and validated.
Suitable real Telco workload VNFs are yet to be identified.

.. 3.2.5.2.1

.. _default-test-parameters:

Default Test Parameters
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The following list identifies the default parameters for suite of
tests:

-  Reference application: Simple forwarding or Open Source VNF.
-  Frame size (bytes): 64, 128, 256, 512, 1024, 1280, 1518, 2K, 4k OR
   Packet size based on use-case (e.g. RTP 64B, 256B) OR Mix of packet sizes as
   maintained by the Functest project <https://wiki.opnfv.org/traffic_profile_management>.
-  Reordering check: Tests should confirm that packets within a flow are
   not reordered.
-  Duplex: Unidirectional / Bidirectional. Default: Full duplex with
   traffic transmitting in both directions, as network traffic generally
   does not flow in a single direction. By default the data rate of
   transmitted traffic should be the same in both directions, please
   note that asymmetric traffic (e.g. downlink-heavy) tests will be
   mentioned explicitly for the relevant test cases.
-  Number of Flows: Default for non scalability tests is a single flow.
   For scalability tests the goal is to test with maximum supported
   flows but where possible will test up to 10 Million flows. Start with
   a single flow and scale up. By default flows should be added
   sequentially, tests that add flows simultaneously will explicitly
   call out their flow addition behaviour. Packets are generated across
   the flows uniformly with no burstiness. For multi-core tests should
   consider the number of packet flows based on vSwitch/VNF multi-thread
   implementation and behavior.

-  Traffic Types: UDP, SCTP, RTP, GTP and UDP traffic.
-  Deployment scenarios are:
-  Physical → virtual switch → physical.
-  Physical → virtual switch → VNF → virtual switch → physical.
-  Physical → virtual switch → VNF → virtual switch → VNF → virtual
   switch → physical.
-  Physical → VNF → virtual switch → VNF → physical.
-  Physical → virtual switch → VNF.
-  VNF → virtual switch → Physical.
-  VNF → virtual switch → VNF.

Tests MUST have these parameters unless otherwise stated. **Test cases
with non default parameters will be stated explicitly**.

**Note**: For throughput tests unless stated otherwise, test
configurations should ensure that traffic traverses the installed flows
through the virtual switch, i.e. flows are installed and have an appropriate
time out that doesn't expire before packet transmission starts.

.. 3.2.5.2.2

Flow Classification
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Virtual switches classify packets into flows by processing and matching
particular header fields in the packet/frame and/or the input port where
the packets/frames arrived. The vSwitch then carries out an action on
the group of packets that match the classification parameters. Thus a
flow is considered to be a sequence of packets that have a shared set of
header field values or have arrived on the same port and have the same
action applied to them. Performance results can vary based on the
parameters the vSwitch uses to match for a flow. The recommended flow
classification parameters for L3 vSwitch performance tests are: the
input port, the source IP address, the destination IP address and the
Ethernet protocol type field. It is essential to increase the flow
time-out time on a vSwitch before conducting any performance tests that
do not measure the flow set-up time. Normally the first packet of a
particular flow will install the flow in the vSwitch which adds an
additional latency, subsequent packets of the same flow are not subject
to this latency if the flow is already installed on the vSwitch.

.. 3.2.5.2.3

Test Priority
~~~~~~~~~~~~~~~~~~~~~

Tests will be assigned a priority in order to determine which tests
should be implemented immediately and which tests implementations
can be deferred.

Priority can be of following types: - Urgent: Must be implemented
immediately. - High: Must be implemented in the next release. - Medium:
May be implemented after the release. - Low: May or may not be
implemented at all.

.. 3.2.5.2.4

SUT Setup
~~~~~~~~~~~~~~~~~~

The SUT should be configured to its "default" state. The
SUT's configuration or set-up must not change between tests in any way
other than what is required to do the test. All supported protocols must
be configured and enabled for each test set up.

.. 3.2.5.2.5

Port Configuration
~~~~~~~~~~~~~~~~~~~~~~~~~~

The DUT should be configured with n ports where
n is a multiple of 2. Half of the ports on the DUT should be used as
ingress ports and the other half of the ports on the DUT should be used
as egress ports. Where a DUT has more than 2 ports, the ingress data
streams should be set-up so that they transmit packets to the egress
ports in sequence so that there is an even distribution of traffic
across ports. For example, if a DUT has 4 ports 0(ingress), 1(ingress),
2(egress) and 3(egress), the traffic stream directed at port 0 should
output a packet to port 2 followed by a packet to port 3. The traffic
stream directed at port 1 should also output a packet to port 2 followed
by a packet to port 3.

.. 3.2.5.2.6

Frame Formats
~~~~~~~~~~~~~~~~~~~~~

**Frame formats Layer 2 (data link layer) protocols**

-  Ethernet II

.. code-block:: console

     +---------------------------+-----------+
     | Ethernet Header | Payload | Check Sum |
     +-----------------+---------+-----------+
     |_________________|_________|___________|
           14 Bytes     46 - 1500   4 Bytes
                          Bytes


**Layer 3 (network layer) protocols**

-  IPv4

.. code-block:: console

     +-----------------+-----------+---------+-----------+
     | Ethernet Header | IP Header | Payload | Checksum  |
     +-----------------+-----------+---------+-----------+
     |_________________|___________|_________|___________|
           14 Bytes       20 bytes  26 - 1480   4 Bytes
                                      Bytes

-  IPv6

.. code-block:: console

     +-----------------+-----------+---------+-----------+
     | Ethernet Header | IP Header | Payload | Checksum  |
     +-----------------+-----------+---------+-----------+
     |_________________|___________|_________|___________|
           14 Bytes       40 bytes  26 - 1460   4 Bytes
                                      Bytes

**Layer 4 (transport layer) protocols**

  - TCP
  - UDP
  - SCTP

.. code-block:: console

     +-----------------+-----------+-----------------+---------+-----------+
     | Ethernet Header | IP Header | Layer 4 Header  | Payload | Checksum  |
     +-----------------+-----------+-----------------+---------+-----------+
     |_________________|___________|_________________|_________|___________|
           14 Bytes      40 bytes      20 Bytes       6 - 1460   4 Bytes
                                                       Bytes


**Layer 5 (application layer) protocols**

  - RTP
  - GTP

.. code-block:: console

     +-----------------+-----------+-----------------+---------+-----------+
     | Ethernet Header | IP Header | Layer 4 Header  | Payload | Checksum  |
     +-----------------+-----------+-----------------+---------+-----------+
     |_________________|___________|_________________|_________|___________|
           14 Bytes      20 bytes     20 Bytes        >= 6 Bytes   4 Bytes

.. 3.2.5.2.7

Packet Throughput
~~~~~~~~~~~~~~~~~~~~~~~~~
There is a difference between an Ethernet frame,
an IP packet, and a UDP datagram. In the seven-layer OSI model of
computer networking, packet refers to a data unit at layer 3 (network
layer). The correct term for a data unit at layer 2 (data link layer) is
a frame, and at layer 4 (transport layer) is a segment or datagram.

Important concepts related to 10GbE performance are frame rate and
throughput. The MAC bit rate of 10GbE, defined in the IEEE standard 802
.3ae, is 10 billion bits per second. Frame rate is based on the bit rate
and frame format definitions. Throughput, defined in IETF RFC 1242, is
the highest rate at which the system under test can forward the offered
load, without loss.

The frame rate for 10GbE is determined by a formula that divides the 10
billion bits per second by the preamble + frame length + inter-frame
gap.

The maximum frame rate is calculated using the minimum values of the
following parameters, as described in the IEEE 802 .3ae standard:

-  Preamble: 8 bytes \* 8 = 64 bits
-  Frame Length: 64 bytes (minimum) \* 8 = 512 bits
-  Inter-frame Gap: 12 bytes (minimum) \* 8 = 96 bits

Therefore, Maximum Frame Rate (64B Frames)
= MAC Transmit Bit Rate / (Preamble + Frame Length + Inter-frame Gap)
= 10,000,000,000 / (64 + 512 + 96)
= 10,000,000,000 / 672
= 14,880,952.38 frame per second (fps)

.. 3.2.5.3

RFCs for testing virtual switch performance
--------------------------------------------------

The starting point for defining the suite of tests for benchmarking the
performance of a virtual switch is to take existing RFCs and standards
that were designed to test their physical counterparts and adapting them
for testing virtual switches. The rationale behind this is to establish
a fair comparison between the performance of virtual and physical
switches. This section outlines the RFCs that are used by this
specification.

.. 3.2.5.3.1

RFC 1242 Benchmarking Terminology for Network Interconnection
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Devices RFC 1242 defines the terminology that is used in describing
performance benchmarking tests and their results. Definitions and
discussions covered include: Back-to-back, bridge, bridge/router,
constant load, data link frame size, frame loss rate, inter frame gap,
latency, and many more.

.. 3.2.5.3.2

RFC 2544 Benchmarking Methodology for Network Interconnect Devices
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
RFC 2544 outlines a benchmarking methodology for network Interconnect
Devices. The methodology results in performance metrics such as latency,
frame loss percentage, and maximum data throughput.

In this document network “throughput” (measured in millions of frames
per second) is based on RFC 2544, unless otherwise noted. Frame size
refers to Ethernet frames ranging from smallest frames of 64 bytes to
largest frames of 9K bytes.

Types of tests are:

1. Throughput test defines the maximum number of frames per second
   that can be transmitted without any error, or 0% loss ratio.
   In some Throughput tests (and those tests with long duration),
   evaluation of an additional frame loss ratio is suggested. The
   current ratio (10^-7 %) is based on understanding the typical
   user-to-user packet loss ratio needed for good application
   performance and recognizing that a single transfer through a
   vswitch must contribute a tiny fraction of user-to-user loss.
   Further, the ratio 10^-7 % also recognizes practical limitations
   when measuring loss ratio.

2. Latency test measures the time required for a frame to travel from
   the originating device through the network to the destination device.
   Please note that RFC2544 Latency measurement will be superseded with
   a measurement of average latency over all successfully transferred
   packets or frames.

3. Frame loss test measures the network’s
   response in overload conditions - a critical indicator of the
   network’s ability to support real-time applications in which a
   large amount of frame loss will rapidly degrade service quality.

4. Burst test assesses the buffering capability of a virtual switch. It
   measures the maximum number of frames received at full line rate
   before a frame is lost. In carrier Ethernet networks, this
   measurement validates the excess information rate (EIR) as defined in
   many SLAs.

5. System recovery to characterize speed of recovery from an overload
   condition.

6. Reset to characterize speed of recovery from device or software
   reset. This type of test has been updated by `RFC6201
   <https://www.rfc-editor.org/rfc/rfc6201.txt>`__ as such,
   the methodology defined by this specification will be that of RFC 6201.

Although not included in the defined RFC 2544 standard, another crucial
measurement in Ethernet networking is packet delay variation. The
definition set out by this specification comes from
`RFC5481 <https://www.rfc-editor.org/rfc/rfc5481.txt>`__.

.. 3.2.5.3.3

RFC 2285 Benchmarking Terminology for LAN Switching Devices
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
RFC 2285 defines the terminology that is used to describe the
terminology for benchmarking a LAN switching device. It extends RFC
1242 and defines: DUTs, SUTs, Traffic orientation and distribution,
bursts, loads, forwarding rates, etc.

.. 3.2.5.3.4

RFC 2889 Benchmarking Methodology for LAN Switching
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
RFC 2889 outlines a benchmarking methodology for LAN switching, it
extends RFC 2544. The outlined methodology gathers performance
metrics for forwarding, congestion control, latency, address handling
and finally filtering.

.. 3.2.5.3.5

RFC 3918 Methodology for IP Multicast Benchmarking
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
RFC 3918 outlines a methodology for IP Multicast benchmarking.

.. 3.2.5.3.6

RFC 4737 Packet Reordering Metrics
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
RFC 4737 describes metrics for identifying and counting re-ordered
packets within a stream, and metrics to measure the extent each
packet has been re-ordered.

.. 3.2.5.3.7

RFC 5481 Packet Delay Variation Applicability Statement
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
RFC 5481 defined two common, but different forms of delay variation
metrics, and compares the metrics over a range of networking
circumstances and tasks. The most suitable form for vSwitch
benchmarking is the "PDV" form.

.. 3.2.5.3.8

RFC 6201 Device Reset Characterization
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
RFC 6201 extends the methodology for characterizing the speed of
recovery of the DUT from device or software reset described in RFC
2544.

.. 3.2.6:

.. _PassFailCriteria:

Item pass/fail criteria
=========================

vswitchperf does not specify Pass/Fail criteria for the tests in terms of a
threshold, as benchmarks do not (and should not do this). The results/metrics
for a test are simply reported. If it had to be defined, a test is considered
to have passed if it succesfully completed and a relavent metric was
recorded/reported for the SUT.

.. 3.2.7:

.. _SuspensionResumptionReqs:

Suspension criteria and resumption requirements
================================================
In the case of a throughput test, a test should be suspended if a virtual
switch is failing to forward any traffic. A test should be restarted from a
clean state if the intention is to carry out the test again.

.. 3.2.8:

.. _TestDelierables:

Test deliverables
==================
Each test should produce a test report that details SUT information as well as
the test results. There are a number of parameters related to the system, DUT
and tests that can affect the repeatability of a test results and should be
recorded. In order to minimise the variation in the results of a test,
it is recommended that the test report includes the following information:

-  Hardware details including:

   -  Platform details.
   -  Processor details.
   -  Memory information (see below)
   -  Number of enabled cores.
   -  Number of cores used for the test.
   -  Number of physical NICs, as well as their details (manufacturer,
      versions, type and the PCI slot they are plugged into).
   -  NIC interrupt configuration.
   -  BIOS version, release date and any configurations that were
      modified.

-  Software details including:

   -  OS version (for host and VNF)
   -  Kernel version (for host and VNF)
   -  GRUB boot parameters (for host and VNF).
   -  Hypervisor details (Type and version).
   -  Selected vSwitch, version number or commit id used.
   -  vSwitch launch command line if it has been parameterised.
   -  Memory allocation to the vSwitch – which NUMA node it is using,
      and how many memory channels.
   -  Where the vswitch is built from source: compiler details including
      versions and the flags that were used to compile the vSwitch.
   -  DPDK or any other SW dependency version number or commit id used.
   -  Memory allocation to a VM - if it's from Hugpages/elsewhere.
   -  VM storage type: snapshot/independent persistent/independent
      non-persistent.
   -  Number of VMs.
   -  Number of Virtual NICs (vNICs), versions, type and driver.
   -  Number of virtual CPUs and their core affinity on the host.
   -  Number vNIC interrupt configuration.
   -  Thread affinitization for the applications (including the vSwitch
      itself) on the host.
   -  Details of Resource isolation, such as CPUs designated for
      Host/Kernel (isolcpu) and CPUs designated for specific processes
      (taskset).

-  Memory Details

   -  Total memory
   -  Type of memory
   -  Used memory
   -  Active memory
   -  Inactive memory
   -  Free memory
   -  Buffer memory
   -  Swap cache
   -  Total swap
   -  Used swap
   -  Free swap

-  Test duration.
-  Number of flows.
-  Traffic Information:

   -  Traffic type - UDP, TCP, IMIX / Other.
   -  Packet Sizes.

-  Deployment Scenario.

**Note**: Tests that require additional parameters to be recorded will
explicitly specify this.


.. 3.3:

.. _TestManagement:

Test management
=================
This section will detail the test activities that will be conducted by vsperf
as well as the infrastructure that will be used to complete the tests in OPNFV.

.. 3.3.1:

Planned activities and tasks; test progression
=================================================
A key consideration when conducting any sort of benchmark is trying to
ensure the consistency and repeatability of test results between runs.
When benchmarking the performance of a virtual switch there are many
factors that can affect the consistency of results. This section
describes these factors and the measures that can be taken to limit
their effects. In addition, this section will outline some system tests
to validate the platform and the VNF before conducting any vSwitch
benchmarking tests.

**System Isolation:**

When conducting a benchmarking test on any SUT, it is essential to limit
(and if reasonable, eliminate) any noise that may interfere with the
accuracy of the metrics collected by the test. This noise may be
introduced by other hardware or software (OS, other applications), and
can result in significantly varying performance metrics being collected
between consecutive runs of the same test. In the case of characterizing
the performance of a virtual switch, there are a number of configuration
parameters that can help increase the repeatability and stability of
test results, including:

-  OS/GRUB configuration:

   -  maxcpus = n where n >= 0; limits the kernel to using 'n'
      processors. Only use exactly what you need.
   -  isolcpus: Isolate CPUs from the general scheduler. Isolate all
      CPUs bar one which will be used by the OS.
   -  use taskset to affinitize the forwarding application and the VNFs
      onto isolated cores. VNFs and the vSwitch should be allocated
      their own cores, i.e. must not share the same cores. vCPUs for the
      VNF should be affinitized to individual cores also.
   -  Limit the amount of background applications that are running and
      set OS to boot to runlevel 3. Make sure to kill any unnecessary
      system processes/daemons.
   -  Only enable hardware that you need to use for your test – to
      ensure there are no other interrupts on the system.
   -  Configure NIC interrupts to only use the cores that are not
      allocated to any other process (VNF/vSwitch).

-  NUMA configuration: Any unused sockets in a multi-socket system
   should be disabled.
-  CPU pinning: The vSwitch and the VNF should each be affinitized to
   separate logical cores using a combination of maxcpus, isolcpus and
   taskset.
-  BIOS configuration: BIOS should be configured for performance where
   an explicit option exists, sleep states should be disabled, any
   virtualization optimization technologies should be enabled, and
   hyperthreading should also be enabled, turbo boost and overclocking
   should be disabled.

**System Validation:**

System validation is broken down into two sub-categories: Platform
validation and VNF validation. The validation test itself involves
verifying the forwarding capability and stability for the sub-system
under test. The rationale behind system validation is two fold. Firstly
to give a tester confidence in the stability of the platform or VNF that
is being tested; and secondly to provide base performance comparison
points to understand the overhead introduced by the virtual switch.

* Benchmark platform forwarding capability: This is an OPTIONAL test
  used to verify the platform and measure the base performance (maximum
  forwarding rate in fps and latency) that can be achieved by the
  platform without a vSwitch or a VNF. The following diagram outlines
  the set-up for benchmarking Platform forwarding capability:

  .. code-block:: console

                                                            __
       +--------------------------------------------------+   |
       |   +------------------------------------------+   |   |
       |   |                                          |   |   |
       |   |          l2fw or DPDK L2FWD app          |   |  Host
       |   |                                          |   |   |
       |   +------------------------------------------+   |   |
       |   |                 NIC                      |   |   |
       +---+------------------------------------------+---+ __|
                  ^                           :
                  |                           |
                  :                           v
       +--------------------------------------------------+
       |                                                  |
       |                traffic generator                 |
       |                                                  |
       +--------------------------------------------------+

* Benchmark VNF forwarding capability: This test is used to verify
  the VNF and measure the base performance (maximum forwarding rate in
  fps and latency) that can be achieved by the VNF without a vSwitch.
  The performance metrics collected by this test will serve as a key
  comparison point for NIC passthrough technologies and vSwitches. VNF
  in this context refers to the hypervisor and the VM. The following
  diagram outlines the set-up for benchmarking VNF forwarding
  capability:

  .. code-block:: console

                                                            __
       +--------------------------------------------------+   |
       |   +------------------------------------------+   |   |
       |   |                                          |   |   |
       |   |                 VNF                      |   |   |
       |   |                                          |   |   |
       |   +------------------------------------------+   |   |
       |   |          Passthrough/SR-IOV              |   |  Host
       |   +------------------------------------------+   |   |
       |   |                 NIC                      |   |   |
       +---+------------------------------------------+---+ __|
                  ^                           :
                  |                           |
                  :                           v
       +--------------------------------------------------+
       |                                                  |
       |                traffic generator                 |
       |                                                  |
       +--------------------------------------------------+


**Methodology to benchmark Platform/VNF forwarding capability**


The recommended methodology for the platform/VNF validation and
benchmark is: - Run `RFC2889 <https://www.rfc-editor.org/rfc/rfc2289.txt>`__
Maximum Forwarding Rate test, this test will produce maximum
forwarding rate and latency results that will serve as the
expected values. These expected values can be used in
subsequent steps or compared with in subsequent validation tests. -
Transmit bidirectional traffic at line rate/max forwarding rate
(whichever is higher) for at least 72 hours, measure throughput (fps)
and latency. - Note: Traffic should be bidirectional. - Establish a
baseline forwarding rate for what the platform can achieve. - Additional
validation: After the test has completed for 72 hours run bidirectional
traffic at the maximum forwarding rate once more to see if the system is
still functional and measure throughput (fps) and latency. Compare the
measure the new obtained values with the expected values.

**NOTE 1**: How the Platform is configured for its forwarding capability
test (BIOS settings, GRUB configuration, runlevel...) is how the
platform should be configured for every test after this

**NOTE 2**: How the VNF is configured for its forwarding capability test
(# of vCPUs, vNICs, Memory, affinitization…) is how it should be
configured for every test that uses a VNF after this.

**Methodology to benchmark the VNF to vSwitch to VNF deployment scenario**

vsperf has identified the following concerns when benchmarking the VNF to
vSwitch to VNF deployment scenario:

* The accuracy of the timing synchronization between VNFs/VMs.
* The clock accuracy of a VNF/VM if they were to be used as traffic generators.
* VNF traffic generator/receiver may be using resources of the system under
  test, causing at least three forms of workload to increase as the traffic
  load increases (generation, switching, receiving).

The recommendation from vsperf is that tests for this sceanario must
include an external HW traffic generator to act as the tester/traffic transmitter
and receiver. The perscribed methodology to benchmark this deployment scanrio with
an external tester involves the following three steps:

#. Determine the forwarding capability and latency through the virtual interface
connected to the VNF/VM.

.. Figure:: vm2vm_virtual_interface_benchmark.png

   Virtual interfaces performance benchmark

#. Determine the forwarding capability and latency through the VNF/hypervisor.

.. Figure:: vm2vm_hypervisor_benchmark.png

   Hypervisor performance benchmark

#. Determine the forwarding capability and latency for the VNF to vSwitch to VNF
   taking the information from the previous two steps into account.

.. Figure:: vm2vm_benchmark.png

   VNF to vSwitch to VNF performance benchmark

vsperf also identified an alternative configuration for the final step:

.. Figure:: vm2vm_alternative_benchmark.png

   VNF to vSwitch to VNF alternative performance benchmark

.. 3.3.2:

Environment/infrastructure
============================
VSPERF CI jobs are run using the OPNFV lab infrastructure as described by the
'Pharos Project <https://www.opnfv.org/community/projects/pharos>`_ .
A VSPERF POD is described here https://wiki.opnfv.org/display/pharos/VSPERF+in+Intel+Pharos+Lab+-+Pod+12

vsperf CI
---------
vsperf CI jobs are broken down into:

  * Daily job:

    * Runs everyday takes about 10 hours to complete.
    * TESTCASES_DAILY='phy2phy_tput back2back phy2phy_tput_mod_vlan
      phy2phy_scalability pvp_tput pvp_back2back pvvp_tput pvvp_back2back'.
    * TESTPARAM_DAILY='--test-params TRAFFICGEN_PKT_SIZES=(64,128,512,1024,1518)'.

  * Merge job:

    * Runs whenever patches are merged to master.
    * Runs a basic Sanity test.

  * Verify job:

    * Runs every time a patch is pushed to gerrit.
    * Builds documentation.

Scripts:
--------
There are 2 scripts that are part of VSPERFs CI:

  * build-vsperf.sh: Lives in the VSPERF repository in the ci/ directory and is
    used to run vsperf with the appropriate cli parameters.
  * vswitchperf.yml: YAML description of our jenkins job. lives in the RELENG
    repository.

More info on vsperf CI can be found here:
https://wiki.opnfv.org/display/vsperf/VSPERF+CI

.. 3.3.3:

Responsibilities and authority
===============================
The group responsible for managing, designing, preparing and executing the
tests listed in the LTD are the vsperf committers and contributors. The vsperf
committers and contributors should work with the relavent OPNFV projects to
ensure that the infrastructure is in place for testing vswitches, and that the
results are published to common end point (a results database).

