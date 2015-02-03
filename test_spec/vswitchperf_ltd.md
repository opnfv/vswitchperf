#CHARACTERIZE VSWITCH PERFORMANCE FOR TELCO NFV USE CASES LEVEL TEST DESIGN

##Table of Contents

 [1. Introduction](#Introduction)

 &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;[1.1. Document identifier](#DocId)

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;[1.2. Scope](#Scope)

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;[1.3. References](#References)

[2.	Details of the Level Test Design](#DetailsOfTheLevelTestDesign)

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;[2.1. Features to be tested](#FeaturesToBeTested)

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;[2.2. Approach](#Approach)

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;[2.3. Test identification](#TestIdentification)

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;[2.3.1 Throughput tests](#ThroughputTests)

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;[2.3.2 Packet Delay Tests](#PacketDelayTests)

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;[2.3.3 Scalability Tests](#ScalabilityTests)

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;[2.3.4 CPU and Memory Consumption Tests](#CPUTests)

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;[2.3.5 Coupling Between the Control Path and The Datapath Tests](#CPDPTests)

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;[2.3.6 Time to Establish Flows Tests](#FlowLatencyTests)

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;[2.3.7 Noisy Neighbour Tests](#NoisyNeighbourTests)

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;[2.3.8 Overlay Tests](#OverlayTests)

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;[2.3.9 Summary Test List](#SummaryList)

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;[2.4. Feature pass/fail criteria](#PassFail)

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;[2.5. Test deliverables](#TestDeliverables)

[3. General](#General)

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;[3.1. Glossary](#Glossary)

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;[3.2. Document change procedures and history](#History)

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;[3.3. Contributors](#Contributors)

<br/>

---
<a name="Introduction"></a>
##1. Introduction ##
  The objective of the OPNFV project titled **“Characterise vSwitch Performance for Telco NFV Use Cases”**, is to evaluate a virtual switch to identify its suitability for a Telco Network Function Virtualization (NFV) environment. The intention of this Level Test Design (LTD) document is to specify the set of tests to carry out in order to objectively measure the current characteristics of a virtual switch in the Network Function Virtualization Infrastructure (NFVI) as well as the test pass criteria. The detailed test cases will be defined in [Section 2](#DetailsOfTheLevelTestDesign), preceded by the [Document identifier](#DocId) and the [Scope](#Scope).

 This document is currently in draft form.

  <a name="DocId"></a>
  ###1.1. Document identifier
  The document id will be used to uniquely identify versions of the LTD. The format for the document id will be: OPNFV\_vswitchperf\_LTD\_ver\_NUM\_MONTH\_YEAR\_STATUS, where by the status is one of: draft, reviewed, corrected or final. The document id for this version of the LTD is: OPNFV\_vswitchperf\_LTD\_ver\_1.6\_Jan\_15\_DRAFT.

  <a name="Scope"></a>
  ###1.2. Scope
  The main purpose of this project is to specify a suite of performance tests in order to objectively measure the current Telco characteristics of a virtual switch in the NFVI. The intent of the project is to facilitate testing of any virtual switch. Thus, a generic suite of tests shall be developed, with no hard dependencies to a single implementation. In addition, the test case suite shall be architecture independent.

  The test cases developed in this project shall not form part of a separate test framework, all of these tests may be inserted into the Continuous Integration Test Framework and/or the Platform Functionality Test Framework - if a vSwitch becomes a standard component of an OPNFV release.

  <a name="References"></a>
  ###1.3. References

  - RFC 2544 Benchmarking Methodology for Network Interconnect Devices
  - RFC 2885 Benchmarking Terminology for LAN Switching Devices
  - RFC 2889 Benchmarking Methodology for LAN Switching Devices
  - RFC 3918 Methodology for IP Multicast Benchmarking
  - RFC 4737 Packet Reordering Metrics
  - RFC 5481 Packet Delay Variation Applicability Statement

<br/>
  <a name="FeaturesToBeTested"></a>
  ###2.1. Features to be tested
  Characterizing virtual switches (i.e. Device Under Test (DUT) in this document) includes measuring the following performance parameters:
   - Throughput: maximum frame rate and bit rate that can be transmitted without any error (multiple flows).
   - Packet delay introduced by the node and its cumulative effect on E2E networks.
   - Packet delay variation: measured from the perspective of the VNF/application. Packet delay variation is sometimes called "jitter". However, we will avoid the term "jitter" as the term holds different meaning to different groups of people. In this document we will simply use the term packet delay variation.
   - Packet loss: Within the node all packets should be accounted for.
   - Burst behaviour: measures the ability of the DUT to buffer packets.
   - Packet re-ordering.
   - Packet correctness.
   - Availability and capacity of the DUT i.e. when the DUT is fully “up” and connected:
    - Includes power consumption of the CPU (in various power states) and system.
    - Includes CPU utilization.
    - Includes # NIC interfaces supported.
    - Includes headroom of VM workload processing cores (i.e. available for applications).

<a name="Approach"></a>
 ###2.2. Approach
 In order to determine the Telco NFV characteristics of a virtual switch, the tests will be broken down into the following categories:

  - Throughput Tests to measure the forwarding rate and bit rate without traffic loss as well as average latency for different packet sizes.
  - Stream Performance Tests (TCP, UDP) to measure bulk data transfer performance, i.e. how fast systems can send and receive data through the switch.
  - Request/Response Performance Tests (TCP, UDP) the measure the transaction rate through the switch.
 - Packet delay tests to understand latency distribution for different packet sizes and over an extended test run to uncover outliers.
  - Scalability Tests to understand how the virtual switch performs as the number of flows it has to deal with increases.
  - Control Path and Datapath Coupling Tests.
  - CPU and Memory Consumption Tests to understand the virtual switch’s footprint on the system, this includes:
   - CPU utilization
   - Cache utilization
   - Memory footprint
  - Time To Establish Flows Tests.
  - Noisy Neighbour tests.

The following represents possible deployments which can help to determine the performance of both the virtual switch and the datapath into the VNF:

  - Physical port  → virtual switch → physical port.

<pre><code>
                                                         __
    +--------------------------------------------------+   |
    |              +--------------------+              |   |
    |              |                    |              |   |
    |              |                    v              |   |  Host
    |   +--------------+            +--------------+   |   |
    |   |   phy port   |  vSwitch   |   phy port   |   |   |
    +---+--------------+------------+--------------+---+ __|
               ^                           :
               |                           |
               :                           v
    +--------------------------------------------------+
    |                                                  |
    |                traffic generator                 |
    |                                                  |
    +--------------------------------------------------+
</code></pre>

  - Physical port → virtual switch → VNF → virtual switch → physical port.

<pre><code>
                                                          __
    +---------------------------------------------------+   |
    |                                                   |   |
    |   +-------------------------------------------+   |   |
    |   |                 Application               |   |   |
    |   +-------------------------------------------+   |   |
    |       ^                                  :        |   |
    |       |                                  |        |   |  Guest
    |       :                                  v        |   |
    |   +---------------+           +---------------+   |   |
    |   | logical port 0|           | logical port 1|   |   |
    +---+---------------+-----------+---------------+---+ __|
            ^                                  :
            |                                  |
            :                                  v         __
    +---+---------------+----------+---------------+---+   |
    |   | logical port 0|          | logical port 1|   |   |
    |   +---------------+          +---------------+   |   |
    |       ^                                  :       |   |
    |       |                                  |       |   |  Host
    |       :                                  v       |   |
    |   +--------------+            +--------------+   |   |
    |   |   phy port   |  vSwitch   |   phy port   |   |   |
    +---+--------------+------------+--------------+---+ __|
               ^                           :
               |                           |
               :                           v
    +--------------------------------------------------+
    |                                                  |
    |                traffic generator                 |
    |                                                  |
    +--------------------------------------------------+
</code></pre>

  - Physical port → virtual switch → VNF → virtual switch → VNF → virtual switch → physical port.

<pre><code>
                                                                                                                 __
    +---------------------------------------------------+   +---------------------------------------------------+  |
    |   Guest 1                                         |   |   Guest 2                                         |  |
    |   +-------------------------------------------+   |   |   +-------------------------------------------+   |  |
    |   |                 Application               |   |   |   |                 Application               |   |  |
    |   +-------------------------------------------+   |   |   +-------------------------------------------+   |  |
    |       ^                                  :        |   |       ^                                  :        |  |
    |       |                                  |        |   |       |                                  |        |  |  Guest
    |       :                                  v        |   |       :                                  v        |  |
    |   +---------------+           +---------------+   |   |   +---------------+           +---------------+   |  |
    |   | logical port 0|           | logical port 1|   |   |   | logical port 0|           | logical port 1|   |  |
    +---+---------------+-----------+---------------+---+   +---+---------------+-----------+---------------+---+__|
            ^                                  :                    ^                                  :
            |                                  |                    |                                  |
            :                                  v                    :                                  v         __
    +---+---------------+----------+---------------+------------+---------------+-----------+---------------+---+  |
    |   |     port 0    |          |     port 1    |            |     port 2    |           |     port 3    |   |  |
    |   +---------------+          +---------------+            +---------------+           +---------------+   |  |
    |       ^                                  :                    ^                                  :        |  |
    |       |                                  |                    |                                  |        |  |  Host
    |       :                                  +--------------------+                                  v        |  |
    |   +--------------+                                                                    +--------------+    |  |
    |   |   phy port   |                               vswitch                              |   phy port   |    |  |
    +---+--------------+--------------------------------------------------------------------+--------------+----+__|
               ^                                                                                    :
               |                                                                                    |
               :                                                                                    v
    +-----------------------------------------------------------------------------------------------------------+
    |                                                                                                           |
    |                                              traffic generator                                            |
    |                                                                                                           |
    +-----------------------------------------------------------------------------------------------------------+
</code></pre>

  - Physical port → virtual switch → VNF.

<pre><code>
                                                          __
    +---------------------------------------------------+   |
    |                                                   |   |
    |   +-------------------------------------------+   |   |
    |   |                 Application               |   |   |
    |   +-------------------------------------------+   |   |
    |       ^                                           |   |
    |       |                                           |   |  Guest
    |       :                                           |   |
    |   +---------------+                               |   |
    |   | logical port 0|                               |   |
    +---+---------------+-------------------------------+ __|
            ^                                  
            |                                  
            :                                            __
    +---+---------------+------------------------------+   |
    |   | logical port 0|                              |   |
    |   +---------------+                              |   |
    |       ^                                          |   |
    |       |                                          |   |  Host
    |       :                                          |   |
    |   +--------------+                               |   |
    |   |   phy port   |  vSwitch                      |   |
    +---+--------------+------------ -------------- ---+ __|
               ^                          
               |                           
               :                           
    +--------------------------------------------------+
    |                                                  |
    |                traffic generator                 |
    |                                                  |
    +--------------------------------------------------+
</code></pre>

  - VNF → virtual switch → physical port.

<pre><code>
                                                          __
    +---------------------------------------------------+   |
    |                                                   |   |
    |   +-------------------------------------------+   |   |
    |   |                 Application               |   |   |
    |   +-------------------------------------------+   |   |
    |                                          :        |   |
    |                                          |        |   |  Guest
    |                                          v        |   |
    |                               +---------------+   |   |
    |                               | logical port  |   |   |
    +-------------------------------+---------------+---+ __|
                                               :
                                               |
                                               v         __
    +------------------------------+---------------+---+   |
    |                              | logical port  |   |   |
    |                              +---------------+   |   |
    |                                          :       |   |
    |                                          |       |   |  Host
    |                                          v       |   |
    |                               +--------------+   |   |
    |                     vSwitch   |   phy port   |   |   |
    +-------------------------------+--------------+---+ __|
                                           :
                                           |
                                           v
    +--------------------------------------------------+
    |                                                  |
    |                traffic generator                 |
    |                                                  |
    +--------------------------------------------------+
</code></pre>

  - virtual switch → VNF → virtual switch.

<pre><code>
                                                                                                                 __
    +---------------------------------------------------+   +---------------------------------------------------+  |
    |   Guest 1                                         |   |   Guest 2                                         |  |
    |   +-------------------------------------------+   |   |   +-------------------------------------------+   |  |
    |   |                 Application               |   |   |   |                 Application               |   |  |
    |   +-------------------------------------------+   |   |   +-------------------------------------------+   |  |
    |                                          :        |   |       ^                                           |  |
    |                                          |        |   |       |                                           |  |  Guest
    |                                          v        |   |       :                                           |  |
    |                               +---------------+   |   |   +---------------+                               |  |
    |                               | logical port 0|   |   |   | logical port 0|                               |  |
    +-------------------------------+---------------+---+   +---+---------------+-------------------------------+__|
                                               :                    ^                                   
                                               |                    |                                   
                                               v                    :                                            __
    +------------------------------+---------------+------------+---------------+-------------------------------+  |
    |                              |     port 0    |            |     port 1    |                               |  |
    |                              +---------------+            +---------------+                               |  |
    |                                          :                    ^                                           |  |
    |                                          |                    |                                           |  |  Host
    |                                          +--------------------+                                           |  |
    |                                                                                                           |  |
    |                                                  vswitch                                                  |  |
    +-----------------------------------------------------------------------------------------------------------+__|
    </code></pre>

 ####General Methodology:

  To establish the baseline performance of the virtual switch, tests would initially be run with a simple workload in the VNF (this could be a simple forwarding application). Subsequently, the tests would also be executed with a real Telco workload running in the VNF, which would exercise the virtual switch in the context of higher level Telco NFV use cases, and prove that its underlying characteristics and behaviour can be measured and validated.

 Potential Telco VNF candidates that could be utilised in a subsequent testing phase might be:

  - EPC Network Functions, MME, SGW, PGW (vEPC)
  - Virtual BRAS (vBRAS)
 <a name="DefaultParams"></a>
 #####Default Test Parameters:
 The following list identifies the default parameters for suite of tests:

 - Reference application: Simple forwarding or Open Source VNF.
 - Frame size (bytes): 64, 128, 256, 512, 1024, 1280, 1518, 2K, 4k OR Packet size based on use-case (e.g. RTP 64B, 256B).
 - Reordering check: Yes, tests should confirm that packets within a flow are not reordered.
 - Duplex: Unidirectional / Bidirectional. Default: Full duplex with traffic transmitting in both directions, as network traffic generally does not flow in a single direction. The data rate of transmitted traffic should be the same in both directions.
 - Number of Flows: Default for non scalability tests is a single flow. For scalability tests the goal is to test with max supported flows but where possible will test up to 10 Million flows. Start with a single flow and scale up. Packets are generated across the flows uniformly with no burstiness.
 - Traffic Types: TCP, SCTP, RTP, GTP and UDP traffic.
 - Deployment scenarios:
      - Physical → virtual switch → physical.
      - Physical → virtual switch → VNF → virtual switch → physical.
      - Physical → virtual switch → VNF → virtual switch → VNF → virtual switch → physical.
      - Physical → virtual switch → VNF.
      - VNF → virtual switch → Physical.
      - VNF → virtual switch → VNF.

 Tests MUST have these parameters unless otherwise stated. **Test cases with non default parameters will be stated explicitly**.

 **Note**: For throughput tests unless stated otherwise, test configurations should ensure that traffic traverses the fastpath through the switch, i.e. flows are installed and have an appropriate time out that doesn't expire before packet transmission starts.

 #####Test Priority
  Tests will be assigned a priority in order to determine which tests should be implemented immediately and which tests implementations can be deferred.

 Priority can be of following types:

 - Urgent: Must be implemented immediately.
 - High: Must be implemented in the next release.
 - Medium: May be implemented after the release.
 - Low: May or may not be implemented at all.

 #####DUT Setup
 The DUT should be configured to it's "default" state. The DUT's configuration or setup must not change between tests in any way other than what is required to do the test. All supported protocols must be configured and enabled for each test set up.

 #####Port Configuration
 The DUT should be configured with n ports where n is a multiple of 2. Half of the ports on the DUT should be used as ingress ports and the other half of the ports on the DUT should be used as egress ports. Where a DUT has more than 2 ports, the ingress data streams should be set-up so that they transmit packets to the egress ports in sequence so that there is an even distribution of traffic across ports. For example, if a DUT has 4 ports 0(ingress), 1(ingress), 2(egress) and 3(egress), the traffic stream directed at port 0 should output a packet to port 2 followed by a packet to port 3. The traffic stream directed at port 1 should also output a packet to port 2 followed by a packet to port 3.

 #####Frame formats
 Layer 2 (data link layer) protocols:

 -  Ethernet II

 <pre><code>

  +-----------------------------+-----------------------------------------------------------------------+---------+
  |       Ethernet Header       |                                Payload                                |Check Sum|
  +-----------------------------+-----------------------------------------------------------------------+---------+
   |___________________________| |_____________________________________________________________________| |_______|
              14 Bytes                                       46 - 1500 Bytes                              4 Bytes

 </code></pre>

 Layer 3 (network layer) protocols:

 - IPv4

 <pre><code>

  +-----------------------------+-------------------------------------+---------------------------------+---------+
  |       Ethernet Header       |              IP Header              |             Payload             |Check Sum|
  +-----------------------------+-------------------------------------+---------------------------------+---------+
   |___________________________| |___________________________________| |_______________________________| |_______|
              14 Bytes                         20 Bytes                         26 - 1480 Bytes           4 Bytes

 </code></pre>

 Layer 4 (transport layer) protocols:

 - TCP
 - UDP
 - SCTP

 <pre><code>

  +-----------------------------+-------------------------------------+-----------------+---------------+---------+
  |       Ethernet Header       |              IP Header              | Layer 4 Header  |    Payload    |Check Sum|
  +-----------------------------+-------------------------------------+-----------------+---------------+---------+
   |___________________________| |___________________________________| |_______________| |_____________| |_______|
              14 Bytes                         20 Bytes                    20 Bytes       6 - 1460 Bytes  4 Bytes

 </code></pre>

 Layer 5 (application layer) protocols:

 - RTP
 - GTP

 <pre><code>

  +-----------------------------+-------------------------------------+-----------------+---------------+---------+
  |       Ethernet Header       |              IP Header              | Layer 4 Header  |    Payload    |Check Sum|
  +-----------------------------+-------------------------------------+-----------------+---------------+---------+
   |___________________________| |___________________________________| |_______________| |_____________| |_______|
              14 Bytes                         20 Bytes                    20 Bytes        Min 6 Bytes    4 Bytes

 </code></pre>

 #####Packet Throughput
 There is a difference between an Ethernet frame, an IP packet, and a UDP datagram. In the seven-layer OSI model of computer networking, packet refers to a data unit at layer 3 (network layer). The correct term for a data unit at layer 2 (data link layer) is a frame, and at layer 4 (transport layer) is a segment or datagram.

 Important concepts related to 10GbE performance are frame rate and throughput. The MAC bit rate of 10GbE, defined in the IEEE standard 802 .3ae, is 10 billion bits per second. Frame rate is based on the bit rate and frame format definitions. Throughput, defined in IETF RFC 1242, is the highest rate at which the system under test can forward the offered load, without loss.

 The frame rate for 10GbE is determined by a formula that divides the 10 billion bits per second by the preamble + frame length + inter-frame gap.

 The maximum frame rate is calculated using the minimum values of the following parameters, as described in the IEEE 802 .3ae standard:

 - Preamble: 8 bytes * 8 = 64 bits
 -  Frame Length: 64 bytes (minimum) * 8 = 512 bits
 -  Inter-frame Gap: 12 bytes (minimum) * 8 = 96 bits

 Therefore, Maximum Frame Rate (64B Frames)

 = MAC Transmit Bit Rate / (Preamble + Frame Length + Inter-frame Gap)

 = 10,000,000,000 / (64 + 512 + 96)

 = 10,000,000,000 / 672

 = 14,880,952.38 frame per second (fps)

 #####RFC 2544 Benchmarking Methodology for Network Interconnect Devices
 RFC 2544 is an Internet Engineering Task Force (IETF) RFC that outlines a benchmarking methodology for network Interconnect Devices. The methodology results in performance metrics such as latency, frame loss percentage, and maximum data throughput.

 In this document network “throughput” (measured in millions of frames per second) is based on RFC 2544, unless otherwise noted. Frame size refers to Ethernet frames ranging from smallest frames of 64 bytes to largest frames of 1518 bytes.

 Types of tests are:

 1.	Throughput test defines the maximum number of frames per second that can be transmitted without any error.
 2.	Latency test measures the time required for a frame to travel from the originating device through the network to the destination device.
 3.	Frame loss test measures the network’s response in overload conditions - a critical indicator of the network’s ability to support real-time applications in which a large amount of frame loss will rapidly degrade service quality.
 4.	Burst test assesses the buffering capability of a switch. It measures the maximum number of frames received at full line rate before a frame is lost. In carrier Ethernet networks, this measurement validates the excess information rate (EIR) as defined in many SLAs.
 5.	System recovery to characterize speed of recovery from an overload condition
 6.	Reset to characterize speed of recovery from device or software reset

 Although not included in the defined RFC 2544 standard, another crucial measurement in Ethernet networking is packet delay variation.

 #####RFC 3918 Methodology for IP Multicast Benchmarking
 RFC 3918 is an IETF RFC that outlines a methodology for IP Multicast benchmarking

 #####RFC 2889 Benchmarking Methodology for LAN Switching
 RFC 2889 is an IETF RFC that outlines a benchmarking methodology for LAN switching, it extends RFC 2544. The outlined methodology gathers performance metrics for forwarding, congestion control, latency, address handling and finally filtering.

 #####RFC 4737 Packet Reordering Metrics
 
 ##### RFC 5481 Packet Delay Variation Applicability Statement