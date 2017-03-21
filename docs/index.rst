.. This work is licensed under a Creative Commons Attribution 4.0 International License.
.. http://creativecommons.org/licenses/by/4.0
.. (c) OPNFV, Intel Corporation, AT&T, Red Hat, Spirent, Ixia  and others.

.. OPNFV VSPERF Documentation master file.

======
VSPERF
======

VSPERF is an OPNFV testing project.

VSPERF provides a configurable and automated test-framework with test cases based on
industry standard network benchmarks applicable to NFVI. This includes the network
tolpology with physical and virtual network interfaces as well as the switching
technology. The VSPERF architecture was designed to be switch and traffic generator
agnostic and provides control of NFVI software components, switch configurations and
test-case customization.

The Danube release of VSPERF includes improvements in documentation and capabilities.
This includes additional test-cases such as RFC 5481 (latency tests) and RFC-2889
(address-learning-rate test). Hardware traffic generator support is now provided for
Spirent and Xena in addition to Ixia. The Moongen software traffic generator is also
now supported. VSPERF can be used in a variety of modes for configuration and
setup of the network and/or for control of the traffic-generator and test execution.

* Wiki: https://wiki.opnfv.org/characterize_vswitch_performance_for_telco_nfv_use_cases
* Repository: https://git.opnfv.org/vswitchperf
* Artifacts: https://artifacts.opnfv.org/vswitchperf.html
* Continuous Integration status: https://build.opnfv.org/ci/view/vswitchperf/

******************************
VSPERF User Guides
******************************

.. toctree::
   :caption: VSPERF User Guide
   :maxdepth: 5
   :numbered: 5

   ./testing/user/configguide/installation.rst
   ./testing/user/configguide/upgrade.rst
   ./testing/user/configguide/trafficgen.rst

   ./testing/user/userguide/testusage.rst
   ./testing/user/userguide/teststeps.rst
   ./testing/user/userguide/integration.rst
   Yardstick integration <./testing/user/userguide/yardstick.rst>


****************************
VSPERF Developer Guides
****************************

.. toctree::
   :caption: VSPERF Developer Guide
   :maxdepth: 5
   :numbered: 5

   ./testing/developer/design/trafficgen_integration_guide.rst
   ./testing/developer/design/vswitchperf_design.rst

   ./testing/developer/requirements/vswitchperf_ltd.rst
   ./testing/developer/requirements/vswitchperf_ltp.rst
   IETF Internet Draft: Benchmarking Virtual Switches in OPNFV <./requirements/ietf_draft/>


******************************
VSPERF Results
******************************

.. toctree::
   :caption: VSPERF Scenarios and Test Cases
   :maxdepth: 3
   :numbered: 3

   ./testing/developer/results/scenario.rst
   ./testing/developer/results/results.rst

Indices
=======
* :ref:`search`
