.. This work is licensed under a Creative Commons Attribution 4.0 International License.
.. http://creativecommons.org/licenses/by/4.0
.. (c) OPNFV, Intel Corporation, AT&T, Red Hat, Spirent, Ixia  and others.

.. OPNFV VSPERF Documentation master file.

**********************
VSPERF Developer Guide
**********************

============
Introduction
============

VSPERF is an OPNFV testing project.

VSPERF provides an automated test-framework and comprehensive test suite based on Industry
Test Specifications for measuring NFVI data-plane performance. The data-path includes switching technologies with
physical and virtual network interfaces. The VSPERF architecture is switch and traffic generator agnostic and test
cases can be easily customized. VSPERF was designed to be independent of OpenStack therefore OPNFV installer scenarios
are not required. VSPERF can source, configure and deploy the device-under-test using specified software versions and
network topology. VSPERF is used as a development tool for optimizing switching technologies, qualification of packet
processing functions and for evaluation of data-path performance.

The Euphrates release adds new features and improvements that will help advance high performance packet processing
on Telco NFV platforms. This includes new test cases, flexibility in customizing test-cases, new results display
options, improved tool resiliency, additional traffic generator support and VPP support.

VSPERF provides a framework where the entire NFV Industry can learn about NFVI data-plane performance and try-out
new techniques together. A new IETF benchmarking specification (RFC8204) is based on VSPERF work contributed since
2015. VSPERF is also contributing to development of ETSI NFV test specifications through the Test and Open Source
Working Group.

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

=============
IETF RFC 8204
=============

.. toctree::
   :caption: VSPERF contributions to Industry Specifications
   :maxdepth: 2
   :numbered:

The IETF Benchmarking Methodology Working Group (BMWG) was re-chartered in 2014 to include benchmarking for
Virtualized Network Functions (VNFs) and their infrastructure. A version of the VSPERF test specification was
summarized in an Internet Draft ... `Benchmarking Virtual Switches in OPNFV <https://tools.ietf.org/html/draft-ietf-bmwg-vswitch-opnfv-01>`_ and contributed to the BMWG. In June 2017 the Internet Engineering Steering Group of the IETF
approved the most recent version of the draft for publication as a new test specification (RFC 8204).

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
