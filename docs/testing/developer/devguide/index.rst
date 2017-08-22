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

VSPERF provides an automated test-framework and comprehensive test suite based on
industry standards for measuring data-plane performance of Telco NFV switching
technologies as well as physical and virtual network interfaces (NFVI). The VSPERF
architecture is switch and traffic generator agnostic and provides full control of
software component versions and configurations as well as test-case customization.

The Danube release of VSPERF includes improvements in documentation and capabilities.
This includes additional test-cases such as RFC 5481 Latency test and RFC-2889
address-learning-rate test. Hardware traffic generator support is now provided for
Spirent and Xena in addition to Ixia. The Moongen software traffic generator is also
now fully supported. VSPERF can be used in a variety of modes for configuration and
setup of the network and/or for control of the test-generator and test execution.

* Wiki: https://wiki.opnfv.org/characterize_vswitch_performance_for_telco_nfv_use_cases
* Repository: https://git.opnfv.org/vswitchperf
* Artifacts: https://artifacts.opnfv.org/vswitchperf.html
* Continuous Integration status: https://build.opnfv.org/ci/view/vswitchperf/

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

The VSPERF test specification was summarized in a 23 page Internet Draft ... `Benchmarking Virtual Switches in OPNFV
<https://tools.ietf.org/html/draft-ietf-bmwg-vswitch-opnfv-01>`_
 which was contributed to the IETF Benchmarking Methodology Working Group (BMWG). The BMWG was re-chartered in 2014
to include benchmarking for Virtualized Network Functions (VNFs) and their infrastructure. The Internet Engineering
Steering Group of the IETF has approved the most recent version for publication as RFC 8204.

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
