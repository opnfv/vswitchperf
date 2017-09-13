.. This work is licensed under a Creative Commons Attribution 4.0 International License.
.. http://creativecommons.org/licenses/by/4.0
.. (c) OPNFV, Intel Corporation, AT&T, Red Hat, Spirent, Ixia  and others.

.. OPNFV VSPERF Documentation master file.

****************************
OPNFV VSPERF Developer Guide
****************************

============
Introduction
============

VSPERF is an OPNFV testing project.

VSPERF is a mature project that provides an automated test-framework and comprehensive test suite based on Industry
Standards for measuring NFVI data-plane performance which includes switching technologies with physical and virtual
network interfaces. The VSPERF architecture is switch and traffic generator agnostic and test cases can be customized. 
The vSwitch and other software component versions and configurations as well as the network topology are controlled by 
VSPERF independently of OpenStack. VSPERF is used as a development tool for optimizing switching technologies, 
qualification of packet processing components, as well as for evaluation of the data-path in Telco NFV platforms.

The Euphrates release brings new features and improvements that will help advance high performance packet processing 
on Telco NFV platforms. This includes new test cases, flexibility in customizing test-cases, new results display 
options, improved tool resiliency, additional traffic generator support and VPP support. VSPERF provides a framework 
where the entire NFV Industry can learn about NFVI data-plane performance and try-out new techniques together.  

A new IETF benchmarking specification RFC8204 has recently been approved based on VSPERF work contributed since 2015. 
VSPERF is also contributing to development of ETSI NFV test specificatios.

* Wiki: https://wiki.opnfv.org/characterize_vswitch_performance_for_telco_nfv_use_cases
* Repository: https://git.opnfv.org/vswitchperf
* Artifacts: https://artifacts.opnfv.org/vswitchperf.html
* Continuous Integration: https://build.opnfv.org/ci/view/vswitchperf/

=============
Design Guides
=============

.. toctree::
   :caption: Traffic Gen Integration, VSPERF Design, Test Design, Test Plan
   :maxdepth: 2
   :numbered:

   ./design/trafficgen_integration_guide.rst
   ./design/vswitchperf_design.rst

   ./requirements/vswitchperf_ltd.rst
   ./requirements/vswitchperf_ltp.rst

====================
VSPERF IETF RFC 8204
====================

.. toctree::
   :caption: vSwitch Internet Draft
   :maxdepth: 2
   :numbered:

The IETF BMWG was re-chartered in 2014 to include benchmarking for Virtualized Network Functions (VNFs) and their
infrastructure. The VSPERF test specification was summarized in an Internet Draft ...
`Benchmarking Virtual Switches in OPNFV <https://tools.ietf.org/html/draft-ietf-bmwg-vswitch-opnfv-01>`_
which was contributed to the IETF Benchmarking Methodology Working Group (BMWG). The Internet Engineering
Steering Group of the IETF has approved the most recent version of the draft for publication as RFC 8204.

====================
VSPERF CI Test Cases
====================

.. toctree::
   :caption: VSPERF Scenarios & Results
   :maxdepth: 2
   :numbered:

CI Test cases run daily on the VSPERF Pharos POD for master and stable branches.

   ./results/scenario.rst
   ./results/results.rst
