#CHARACTERIZE VSWITCH PERFORMANCE FOR TELCO NFV USE CASES LEVEL TEST DESIGN

##Table of Contents

- [1. Introduction](#Introduction)
  - [1.1. Document identifier](#DocId)
  - [1.2. Scope](#Scope)
 - [1.3. References](#References)

- [2. Details of the Level Test Design](#DetailsOfTheLevelTestDesign)
  - [2.1. Features to be tested](#FeaturesToBeTested)
  - [2.2. Approach](#Approach)
  - [2.3. Test identification](#TestIdentification)
    - [2.3.1 Throughput tests](#ThroughputTests)
    - [2.3.2 Packet Delay Tests](#PacketDelayTests)
    - [2.3.3 Scalability Tests](#ScalabilityTests)
    - [2.3.4 CPU and Memory Consumption Tests](#CPUTests)
    - [2.3.5 Coupling Between the Control Path and The Datapath Tests](#CPDPTests)
    - [2.3.6 Time to Establish Flows Tests](#FlowLatencyTests)
    - [2.3.7 Noisy Neighbour Tests](#NoisyNeighbourTests)
    - [2.3.8 Overlay Tests](#OverlayTests)
    - [2.3.9 Summary Test List](#SummaryList)
  - [2.4. Feature pass/fail criteria](#PassFail)
  - [2.5. Test deliverables](#TestDeliverables)

- [3. General](#General)
  - [3.1. Glossary](#Glossary)
  - [3.2. Document change procedures and history](#History)
  - [3.3. Contributors](#Contributors)

<br/>

---
<a name="Introduction"></a>
##1. Introduction
  The objective of the OPNFV project titled **“Characterize vSwitch Performance for Telco NFV Use Cases”**, is to evaluate a virtual switch to identify its suitability for a Telco Network Function Virtualization (NFV) environment. The intention of this Level Test Design (LTD) document is to specify the set of tests to carry out in order to objectively measure the current characteristics of a virtual switch in the Network Function Virtualization Infrastructure (NFVI) as well as the test pass criteria. The detailed test cases will be defined in [Section 2](#DetailsOfTheLevelTestDesign), preceded by the [Document identifier](#DocId) and the [Scope](#Scope).

 This document is currently in draft form.

  <a name="DocId"></a>
  ###1.1. Document identifier
  The document id will be used to uniquely identify versions of the LTD. The format for the document id will be: OPNFV\_vswitchperf\_LTD\_ver\_NUM\_MONTH\_YEAR\_STATUS, where by the status is one of: draft, reviewed, corrected or final. The document id for this version of the LTD is: OPNFV\_vswitchperf\_LTD\_ver\_1.6\_Jan\_15\_DRAFT.

  <a name="Scope"></a>
  ###1.2. Scope
  The main purpose of this project is to specify a suite of performance tests in order to objectively measure the current packet transfer characteristics of a virtual switch in the NFVI. The intent of the project is to facilitate testing of any virtual switch. Thus, a generic suite of tests shall be developed, with no hard dependencies to a single implementation. In addition, the test case suite shall be architecture independent.

  The test cases developed in this project shall not form part of a separate test framework, all of these tests may be inserted into the Continuous Integration Test Framework and/or the Platform Functionality Test Framework - if a vSwitch becomes a standard component of an OPNFV release.

  <a name="References"></a>
  ###1.3. References

  - [RFC 1242 Benchmarking Terminology for Network Interconnection Devices](http://www.ietf.org/rfc/rfc1242.txt)
  - [RFC 2544 Benchmarking Methodology for Network Interconnect Devices](http://www.ietf.org/rfc/rfc2544.txt)
  - [RFC 2885 Benchmarking Terminology for LAN Switching Devices](http://www.ietf.org/rfc/rfc2885.txt)
  - [RFC 2889 Benchmarking Methodology for LAN Switching Devices](http://www.ietf.org/rfc/rfc2889.txt)
  - [RFC 3918 Methodology for IP Multicast Benchmarking](http://www.ietf.org/rfc/rfc3918.txt)
  - [RFC 4737 Packet Reordering Metrics](http://www.ietf.org/rfc/rfc4737.txt)
  - [RFC 5481 Packet Delay Variation Applicability Statement](http://www.ietf.org/rfc/rfc5481.txt)

<br/>
  <a name="FeaturesToBeTested"></a>
  ###2.1. Features to be tested
  Characterizing virtual switches (i.e. Device Under Test (DUT) in this document) includes measuring the following performance metrics:
   - Throughput as defined by [RFC1242]: The maximum rate at which none of the offered frames are dropped by the DUT. The maximum frame rate and bit rate that can be transmitted by the DUT without any error should be recorded. Note there is an equivalent bit rate and a specific layer at which the payloads contribute to the bits. Errors and improperly formed frames or packets are dropped.
   - Packet delay introduced by the DUT and its cumulative effect on E2E networks. Frame delay can be measured equivalently.
   - Packet delay variation: measured from the perspective of the VNF/application. Packet delay variation is sometimes called "jitter". However, we will avoid the term "jitter" as the term holds different meaning to different groups of people. In this document we will simply use the term packet delay variation. The preferred form for this metric is the PDV form of delay variation defined in [RFC5481].
   - Packet loss (within a configured waiting time at the receiver): All packets sent to the DUT should be accounted for.
   - Burst behaviour: measures the ability of the DUT to buffer packets.
   - Packet re-ordering: measures the ability of the device under test to maintain sending order throughout transfer to the destination.
   - Packet correctness Packets or Frames must be well-formed, in that they include all required fields, conform to length requirements, pass integrity checks, etc.
   - Availability and capacity of the DUT i.e. when the DUT is fully “up” and connected:
     - Includes power consumption of the CPU (in various power states) and system.
     - Includes CPU utilization.
     - Includes # NIC interfaces supported.
     - Includes headroom of VM workload processing cores (i.e. available for applications).

[RFC1242]:(http://www.ietf.org/rfc/rfc1242.txt)
[RFC5481]:(http://www.ietf.org/rfc/rfc5482.txt)