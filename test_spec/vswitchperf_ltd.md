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
