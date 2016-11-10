.. This work is licensed under a Creative Commons Attribution 4.0 International License.
.. http://creativecommons.org/licenses/by/4.0
.. (c) OPNFV, Intel Corporation, AT&T and others.

Execution of vswitchperf testcases by Yardstick
-----------------------------------------------

General
^^^^^^^

Yardstick is a generic framework for a test execution, which is used for
validation of installation of OPNFV platform. In the future, Yardstick will
support two options of vswitchperf testcase execution:

- plugin mode, which will execute native vswitchperf testcases; Tests will
  be executed natively by vsperf, and test results will be processed and
  reported by yardstick.
- traffic generator mode, which will run vswitchperf in **trafficgen**
  mode only; Yardstick framework will be used to launch VNFs and to configure
  flows to ensure, that traffic is properly routed. This mode will allow to
  test OVS performance in real world scenarios.

In Colorado release only the traffic generator mode is supported.

Yardstick Installation
^^^^^^^^^^^^^^^^^^^^^^

In order to run Yardstick testcases, you will need to prepare your test
environment. Please follow the `installation instructions
<http://artifacts.opnfv.org/yardstick/docs/user_guides_framework/index.html>`__
to install the yardstick.

Please note, that yardstick uses OpenStack for execution of testcases.
OpenStack must be installed with Heat and Neutron services. Otherwise
vswitchperf testcases cannot be executed.

VM image with vswitchperf
^^^^^^^^^^^^^^^^^^^^^^^^^

A special VM image is required for execution of vswitchperf specific testcases
by yardstick. It is possible to use a sample VM image available at OPNFV
artifactory or to build customized image.

Sample VM image with vswitchperf
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Sample VM image is available at vswitchperf section of OPNFV artifactory
for free download:

.. code-block:: console

    $ wget http://artifacts.opnfv.org/vswitchperf/vnf/vsperf-yardstick-image.qcow2

This image can be used for execution of sample testcases with dummy traffic
generator.

**NOTE:** Traffic generators might require an installation of client software.
This software is not included in the sample image and must be installed by user.

**NOTE:** This image will be updated only in case, that new features related
to yardstick integration will be added to the vswitchperf.

Preparation of custom VM image
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

In general, any Linux distribution supported by vswitchperf can be used as
a base image for vswitchperf. One of the possibilities is to modify vloop-vnf
image, which can be downloaded from `<http://artifacts.opnfv.org/vswitchperf.html/>`__.

.. code-block:: console

    $ wget http://artifacts.opnfv.org/vswitchperf/vnf/vloop-vnf-ubuntu-14.04_20160823.qcow2

Please follow the `installation instructions
<http://artifacts.opnfv.org/vswitchperf/docs/configguide/installation.html>`__ to
install vswitchperf inside vloop-vnf image. As vswitchperf will be run in
trafficgen mode, it is possible to skip installation and compilation of OVS,
QEMU and DPDK to keep image size smaller.

In case, that selected traffic generator requires installation of additional
client software, please follow appropriate documentation. For example in case
of IXIA, you would need to install IxOS and IxNetowrk TCL API.

VM image usage
~~~~~~~~~~~~~~

Image with vswitchperf must be uploaded into the glance service and
vswitchperf specific flavor configured, e.g.:

.. code-block:: console

    $ glance --os-username admin --os-image-api-version 1 image-create --name \
      vsperf --is-public true --disk-format qcow2 --container-format bare --file \
      vsperf-yardstick-image.qcow2

    $ nova --os-username admin flavor-create vsperf-flavor 100 2048 25 1

Testcase execution
^^^^^^^^^^^^^^^^^^

After installation, yardstick is available as python package within yardstick
specific virtual environment. It means, that yardstick environment must be
enabled before the test execution, e.g.:

.. code-block:: console

   source ~/yardstick_venv/bin/activate


Next step is configuration of OpenStack environment, e.g. in case of devstack:

.. code-block:: console

   source /opt/openstack/devstack/openrc
   export EXTERNAL_NETWORK=public

Vswitchperf testcases executable by yardstick are located at vswitchperf
repository inside ``yardstick/tests`` directory. Example of their download
and execution follows:

.. code-block:: console

   git clone https://gerrit.opnfv.org/gerrit/vswitchperf
   cd vswitchperf

   yardstick -d task start yardstick/tests/rfc2544_throughput_dummy.yaml

**NOTE:** Optional argument ``-d`` shows debug output.

Testcase customization
^^^^^^^^^^^^^^^^^^^^^^

Yardstick testcases are described by YAML files. vswitchperf specific testcases
are part of the vswitchperf repository and their yaml files can be found at
``yardstick/tests`` directory. For detailed description of yaml file structure,
please see yardstick documentation and testcase samples. Only vswitchperf specific
parts will be discussed here.

Example of yaml file:

.. code-block:: yaml

    ...
    scenarios:
    -
      type: Vsperf
      options:
        testname: 'p2p_rfc2544_throughput'
        traffic_type: 'rfc2544'
        frame_size '64'
        bidirectional: 'True'
        iload: 100
        trafficgen_port1: 'eth1'
        trafficgen_port2: 'eth3'
        external_bridge: 'br-ex'
        test_params: 'TRAFFICGEN_DURATION=30;'
        conf_file: '~/vsperf-yardstick.conf'

      host: vsperf.demo

      runner:
        type: Sequence
        scenario_option_name: frame_size
        sequence:
        - 64
        - 128
        - 512
        - 1024
        - 1518
      sla:
        metrics: 'throughput_rx_fps'
        throughput_rx_fps: 500000
        action: monitor

    context:
    ...

Section option
~~~~~~~~~~~~~~

Section **option** defines details of vswitchperf test scenario. Lot of options
are identical to the vswitchperf parameters passed through ``--test-params``
argument. Following options are supported:

- **traffic_type** - specifies the type of traffic executed by traffic generator;
  valid values are "rfc2544", "continuous" and "back2back"; Default: 'rfc2544'
- **frame_size** - a packet size for which test should be executed;
  Multiple packet sizes can be tested by modification of Sequence runner
  section inside YAML definition. Default: '64'
- **bidirectional** - specifies if traffic will be uni (False) or bi-directional
  (True); Default: False
- **iload** - specifies frame rate; Default: 100
- **multistream** - specifies the number of simulated streams; Default: 0 (i.e.
  multistream feature is disabled)
- **stream_type** - specifies network layer used for multistream simulation
  the valid values are "L4", "L3" and "L2"; Default: 'L4'
- **conf_file** - sets path to the vswitchperf configuration file, which will be
  uploaded to VM; Default: '~/vsperf-yardstick.conf'
- **setup_script** - sets path to the setup script, which will be executed
  during setup and teardown phases
- **trafficgen_port1** - specifies device name of 1st interface connected to
  the trafficgen
- **trafficgen_port2** - specifies device name of 2nd interface connected to
  the trafficgen
- **external_bridge** - specifies name of external bridge configured in OVS;
  Default: 'br-ex'
- **test_params** - specifies a string with a list of vsperf configuration
  parameters, which will be passed to the ``--test-params`` CLI argument;
  Parameters should be stated in the form of ``param=value`` and separated
  by a semicolon. Please check VSPERF documentation for details about
  available configuration parameters and their data types.
  In case that both **test_params** and **conf_file** are specified,
  then values from **test_params** will override values defined
  in the configuration file.

In case that **trafficgen_port1** and/or **trafficgen_port2** are defined, then
these interfaces will be inserted into the **external_bridge** of OVS. It is
expected, that OVS runs at the same node, where the testcase is executed. In case
of more complex OpenStack installation or a need of additional OVS configuration,
**setup_script** can be used.

Note: It is essential to specify a configuration for selected traffic generator.
In case, that standalone testcase is created, then traffic generator can be
selected and configured directly in YAML file by **test_params**. On the other
hand, if multiple testcases should be executed with the same traffic generator
settings, then a customized configuration file should be prepared and its name
passed by **conf_file** option.

Section runner
~~~~~~~~~~~~~~

Yardstick supports several `runner types
<http://artifacts.opnfv.org/yardstick/docs/userguide/architecture.html#runner-types>`__.
In case of vswitchperf specific TCs, **Sequence** runner type can be used to
execute the testcase for given list of frame sizes.


Section sla
~~~~~~~~~~~

In case that sla section is not defined, then testcase will be always
considered as successful. On the other hand, it is possible to define a set of
test metrics and their minimal values to evaluate test success. Any numeric
value, reported by vswitchperf inside CSV result file, can be used.
Multiple metrics can be defined as a coma separated list of items. Minimal
value must be set separately for each metric.

e.g.:

.. code-block:: yaml

      sla:
          metrics: 'throughput_rx_fps,throughput_rx_mbps'
          throughput_rx_fps: 500000
          throughput_rx_mbps: 1000

In case that any of defined metrics will be lower than defined value, then
testcase will be marked as failed. Based on ``action`` policy, yardstick
will either stop test execution (value ``assert``) or it will run next test
(value ``monitor``).
