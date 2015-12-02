===========
VSPERF NEWS
===========

October 2015
==============
New
---
- Support of PVP and PVVP deployment scenarios using Vanilla OVS

September 2015
==============
New
---
- Implementation of system statistics based upon pidstat command line tool.
- Support of PVVP deployment scenario using bhost-cuse and vhost user access
  methods

August 2015
===========
New
---
- Backport and enhancement of reporting
- PVP deployment scenario testing using vhost-cuse as guest access method
- Implementation of LTD.Scalability.RFC2544.0PacketLoss testcase
- Support for background load generation with command line tools like stress
  and stress-ng

July 2015
=========
New
---
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

New
---

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

Missing
-------

-  xmlunit output is currently disabled
