.. This work is licensed under a Creative Commons Attribution 4.0 International License.
.. http://creativecommons.org/licenses/by/4.0
.. (c) OPNFV, Intel Corporation, AT&T and others.

OPNFV Euphrates Release
=======================

* Improvement of stepdriven testcases
* Support for graph plotting from vsperf results
* Support for vHost User client mode in OVS and VPP
* Support for DPDK 17.02
* Support for dpdk driver NIC binding by drivectl tool
* Several bugfixes and small improvements

* vSwitches

  * Support for VPP virtual switch
  * OVS: Support for jumbo frames

* Traffic Generators:

  * Support for Trex traffic generator
  * Support for huge number of streams
  * Ixia: L3, L4 or vlan headers can be turned off/on, support of 1 NIC connection
    between DUT and Ixia, bugfixing
  * MoonGen: fix multistream support
  * Xena: option for final verification, JSON refactoring, support for xena
    pairs topology and port removal options, bugfixes

* Guest specific:

  * Support for additional QEMU cpu features
  * Support for pinning of vCPU threads

* Integration tests:

  * New VPP related testcases
  * New multistream testcases focused on L3 and L4 performance of OVS and VPP

OPNFV Danube Release
====================

* Support for testpmd as a vswitch for PVP scenario with vHost User
* Traffic type naming harmonized with RFC2544
* Support for step driven performance testcases
* Scripts with licenses not compatible with Apache 2.0 were isolated
  in 3rd_party directory
* Several bugfixes, CI script and documentation updates
* Installation scripts:

  * Support for Ubuntu 16.04 LTS and 16.10
  * Support for RHEL7.3
  * Support for CentOS7.3
  * Support for openSUSE Leap 42.2

* Traffic Generators:

  * Spirent Testcenter: Support for RFC2889 tests
  * Xena: bugfixes and improvements of RFC2544 continuous accuracy
  * MoonGen: bugfixes, code clean up and update of usage instructions
  * Dummy: Support for preconfigured test results
  * Ixia: bugfixes

* Integration tests:

  * New tests for multi VM scenarios
  * New test for numa vHost awareness feature

* Configuration changes:

  * Support for OVS, DPDK or QEMU installed from binary packages
  * Support for modification of any configuration parameter or traffic
    detail via CLI option --test-params or via "Parameters" section
    of testcase definition

* Guest specific:

  * Support for multi VM scenarios with VM connected in serial or in parallel
  * Support for VM with 1, 2, 4, 6... network interfaces
  * Support for driver binding option
  * Support for flexible testpmd configuration
  * Support for configurable merge-buffers
  * Support for configurable drive options
  * Support for multi-queue with non testpmd options by Vanilla OVS
  * Support for multi-queue with OVS 2.5.0 or less
  * Remove support for vHost Cuse

OPNFV Colorado Release
======================

* Support for DPDK v16.07
* Support for yardstick testing framework
* Support for stp/rstp configuration
* Support for veth ports and network namespaces
* Support for multi-queue usage by testpmd loopback app
* Support for reporting of test execution length
* Support for MoonGen traffic generator.
* Support for OVS version 2.5 + DPDK 2.2.
* Support for DPDK v16.04
* Support for Xena traffic generator.
* Support for Red Hat Enterprise Linux
* Support for mode of operation (trafficgen, trafficgen-off)
* Support for Integration tests for OVS with DPDK including:

  * Physical ports.
  * Virtual ports (vhost user and vhost cuse).
  * Flow addition and removal tests.
  * Overlay (VXLAN, GRE and NVGRE) encapsulation and decapsulation tests.

* Supporting configuration of OVS with DPDK through the OVS DB as well as the
  legacy commandline arguments.
* Support for VM loopback (SR-IOV) benchmarking.
* Support for platform baseline benchmarking without a vswitch using testpmd.
* Support for Spirent Test Center REST APIs.

OPNFV Brahmaputra Release
=========================

Supports both OVS and OVS with DPDK.

Available tests:

* phy2phy_tput:     LTD.Throughput.RFC2544.PacketLossRatio
* back2back:        LTD.Throughput.RFC2544.BackToBackFrames
* phy2phy_tput_mod_vlan:LTD.Throughput.RFC2544.PacketLossRatioFrameModification
* phy2phy_cont:     Phy2Phy Continuous Stream
* pvp_cont:         PVP Continuous Stream
* pvvp_cont:        PVVP Continuous Stream
* phy2phy_scalability:LTD.Scalability.RFC2544.0PacketLoss
* pvp_tput:         LTD.Throughput.RFC2544.PacketLossRatio
* pvp_back2back:    LTD.Throughput.RFC2544.BackToBackFrames
* pvvp_tput:        LTD.Throughput.RFC2544.PacketLossRatio
* pvvp_back2back:   LTD.Throughput.RFC2544.BackToBackFrames
* phy2phy_cpu_load: LTD.CPU.RFC2544.0PacketLoss
* phy2phy_mem_load: LTD.Memory.RFC2544.0PacketLoss

Supported deployment scenarios:

* Physical port -> vSwitch -> Physical port.
* Physical port -> vSwitch -> VNF -> vSwitch -> Physical port.
* Physical port -> vSwitch -> VNF -> vSwitch -> VNF -> vSwitch -> Physical port.

Loopback applications in the Guest can be:

* DPDK testpmd.
* Linux Bridge.
* l2fwd Kernel Module.

Supported traffic generators:

* Ixia: IxOS and IxNet.
* Spirent.
* Dummy.

Release Data
~~~~~~~~~~~~

+--------------------------------------+--------------------------------------+
| **Project**                          | vswitchperf                          |
|                                      |                                      |
+--------------------------------------+--------------------------------------+
| **Repo/tag**                         | brahmaputra.1.0                      |
|                                      |                                      |
+--------------------------------------+--------------------------------------+
| **Release designation**              | Brahmaputra base release             |
|                                      |                                      |
+--------------------------------------+--------------------------------------+
| **Release date**                     | February 26 2016                     |
|                                      |                                      |
+--------------------------------------+--------------------------------------+
| **Purpose of the delivery**          | Brahmaputra base release             |
|                                      |                                      |
+--------------------------------------+--------------------------------------+

November 2015
==============

- Support of opnfv_test_dashboard

October 2015
==============

- Support of PVP and PVVP deployment scenarios using Vanilla OVS

September 2015
==============

- Implementation of system statistics based upon pidstat command line tool.
- Support of PVVP deployment scenario using vhost-cuse and vhost user access
  methods

August 2015
===========

- Backport and enhancement of reporting
- PVP deployment scenario testing using vhost-cuse as guest access method
- Implementation of LTD.Scalability.RFC2544.0PacketLoss testcase
- Support for background load generation with command line tools like stress
  and stress-ng

July 2015
=========

- PVP deployment scenario testing using vhost-user as guest access method
  - Verified on CentOS7 and Fedora 20
  - Requires QEMU 2.2.0 and DPDK 2.0

May 2015
========

This is the initial release of a re-designed version of the software
based on community feedback. This initial release supports only the
Phy2Phy deployment scenario and the
LTD.Throughput.RFC2544.PacketLossRatio test - both described in the
OPNFV vswitchperf 'CHARACTERIZE VSWITCH PERFORMANCE FOR TELCO NFV USE
CASES LEVEL TEST DESIGN'. The intention is that more test cases will
follow once the community has digested the initial release.

-  Performance testing with continuous stream
-  Vanilla OVS support added.

   -  Support for non-DPDK OVS build.
   -  Build and installation support through Makefile will be added via
      next patch(Currently it is possible to manually build ovs and
      setting it in vsperf configuration files).
   -  PvP scenario is not yet implemented.

-  CentOS7 support
-  Verified on CentOS7
-  Install & Quickstart documentation

-  Better support for mixing tests types with Deployment Scenarios
-  Re-work based on community feedback of TOIT
-  Framework support for other vSwitches
-  Framework support for non-Ixia traffic generators
-  Framework support for different VNFs
-  Python3
-  Support for biDirectional functionality for ixnet interface
