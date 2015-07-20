#May 2015

This is the initial release of a re-designed version of the software based on
community feedback.  This initial release supports only the Phy2Phy deployment
scenario and the LTD.Throughput.RFC2544.PacketLossRatio test - both described
in the OPNFV vswitchperf 'CHARACTERIZE VSWITCH PERFORMANCE FOR TELCO NFV USE
CASES LEVEL TEST DESIGN'.  The intention is that more test cases will follow
once the community has digested the initial release.

## New

* Performance testing with continuous stream
* CentOS7 support
  * Verified on CentOS7
  * Install & Quickstart documentation

* Better support for mixing tests types with Deployment Scenarios
* Re-work based on community feedback of TOIT
  * Framework support for other vSwitches
  * Framework support for non-Ixia traffic generators
  * Framework support for different VNFs
* Python3
* Support for biDirectional functionality for ixnet interface

## Missing

* Report generation is currently disabled
* xmlunit output is  currently disabled
* VNF support.
