.. This work is licensed under a Creative Commons Attribution 4.0 International License.
.. http://creativecommons.org/licenses/by/4.0
.. (c) OPNFV, Intel Corporation, AT&T, Red Hat, Spirent, Ixia  and others.

.. OPNFV VSPERF Documentation master file.

======
VSPERF
======

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


****************************
VSPERF Developer Guide
****************************

.. toctree::
   :caption: Traffic Gen Integration, VSPERF Design, Test Design, Test Plan
   :maxdepth: 2
   :numbered: 2

   ./design/trafficgen_integration_guide.rst
   ./design/vswitchperf_design.rst

   ./requirements/vswitchperf_ltd.rst
   ./requirements/vswitchperf_ltp.rst

*****************************
VSPERF IETF Internet Draft
*****************************

.. toctree::
   :caption: vSwitch Internet Draft
   :maxdepth: 2
   :numbered: 

This IETF INternet Draft on `Benchmarking Virtual Switches in OPNFV <https://tools.ietf.org/html/draft-ietf-bmwg-vswitch-opnfv-01>`_ was developed by VSPERF contributors and is  maintained in the IETF repo. at https://tools.ietf.org/html/

********************************
VSPERF Scenarios and CI Results
********************************

.. toctree::
   :caption: VSPERF Scenarios & Results
   :maxdepth: 2
   :numbered: 

   ./results/scenario.rst
   ./results/results.rst
