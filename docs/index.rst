.. This work is licensed under a Creative Commons Attribution 4.0 International License.
.. http://creativecommons.org/licenses/by/4.0
.. (c) OPNFV, Intel Corporation, AT&T and others.

.. OPNFV VSPERF Documentation master file.

======
VSPERF
======
VSPERF is an OPNFV testing project.

VSPERF will develop a generic and architecture agnostic vSwitch testing
framework and associated tests, that will serve as a basis for validating the
suitability of different vSwitch implementations in a Telco NFV deployment
environment. The output of this project will be utilized by the OPNFV
Performance and Test group and its associated projects, as part of OPNFV
Platform and VNF level testing and validation.

* Project Wiki: https://wiki.opnfv.org/characterize_vswitch_performance_for_telco_nfv_use_cases
* Project Repository: https://git.opnfv.org/vswitchperf
* Project Artifacts: https://artifacts.opnfv.org/vswitchperf.html
* Continuous Integration https://build.opnfv.org/ci/view/vswitchperf/

******************************
VSPERF Installation Guide
******************************

.. toctree::
   :caption: VSPERF Installation Guide
   :maxdepth: 3
   :numbered: 3

   ./configguide/installation.rst
   ./configguide/upgrade.rst
   ./configguide/trafficgen.rst

******************************
VSPERF User Guide
******************************

.. toctree::
   :caption: VSPERF User Guide
   :maxdepth: 3
   :numbered: 3

   ./userguide/testusage.rst
   ./userguide/teststeps.rst
   ./userguide/integration.rst
   Yardstick integration <./userguide/yardstick.rst>

**************
VSPERF Design
**************

.. toctree::
   :caption: VSPERF Design
   :maxdepth: 3
   :numbered: 3

   ./design/vswitchperf_design.rst
   ./design/trafficgen_integration_guide.rst

*******************
VSPERF Requirements
*******************

.. toctree::
   :caption: VSPERF Requirements
   :maxdepth: 3
   :numbered: 3

   ./requirements/vswitchperf_ltp.rst
   ./requirements/vswitchperf_ltd.rst

.. toctree::
   :titlesonly:
   :maxdepth: 3

   ./release/NEWS.rst

**************
VSPERF Results
**************

.. toctree::
   :maxdepth: 3

   ./results/scenario.rst
   ./results/results.rst

Indices
=======
* :ref:`search`
