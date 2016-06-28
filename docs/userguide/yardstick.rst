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
  be executed the same way as today, but test results will be processed and
  reported by yardstick.
- execution of yardstick testcases, which will run vswitchperf in traffic
  generator mode only; Yardstick framework will be used to launch VNFs
  and to configure flows to ensure, that traffic is properly routed.
  This mode will allow to test OVS performance in real world scenarios.

In Colorado release only the second option is supported.

Yardstick Installation
^^^^^^^^^^^^^^^^^^^^^^

In order to run Yardstick testcases, you will need to prepare your test
environment. Please follow the `installation instructions
<http://artifacts.opnfv.org/yardstick/brahmaputra/docs/user_guides_framework/index.html>`__
to install the yardstick.

Please note, that yardstick uses OpenStack for execution of testcases.
OpenStack must be installed with Heat and Neutron services. Otherwise
vswitchperf testcases cannot be executed.

Vswitchperf VM image preparation
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

In general, any Linux distribution supported by vswitchperf can be used as
a base image for vswitchperf. One of the possibilities is to modify vloop-vnf
image, which can be downloaded from `<http://artifacts.opnfv.org/>`__.

.. code-block:: console

    $ wget http://artifacts.opnfv.org/vswitchperf/vloop-vnf-ubuntu-14.04_20151216.qcow2

Please follow the `installation instructions
<http://artifacts.opnfv.org/vswitchperf/docs/configguide/installation.html>`__ to
install vswitchperf inside vloop-vnf image. As vswitchperf will be run in
trafficgen mode, it is possible to skip installation and compilation of OVS,
QEMU and DPDK to keep image size smaller.

In case, that selected traffic generator requires installation of additional
client software, please follow appropriate documentation. For example in case
of IXIA, you would need to install IxOS and IxNetowrk TCL API.

Final image with vswitchperf must be uploaded into the glance service and
vswitchperf specific flavor configured, e.g.:

.. code-block:: console

    $ glance --os-username admin --os-image-api-version 1 image-create --name
      vsperf --is-public true --disk-format qcow2 --container-format bare --file
      image.qcow2

    $ nova --os-username admin flavor-create vsperf-flavor 100 2048 25 1

Testcase customization
^^^^^^^^^^^^^^^^^^^^^^

Yardstick testcases are described by YAML files. vswitchperf specific testcases
are part of the vswitchperf repository and their yaml files can be found at
``yardstick/tests`` directory. For detailed description of yaml file sctructure,
please see yardstick documentation and testcase samples. Only vswitchperf specific
parts will be discussed here.

Example of yaml file:

.. code-block:: yaml

    ...
    scenarios:
    -
      type: Vsperf
      options:
        testname: 'rfc2544_p2p_tput'
        traffic_type: 'rfc2544'
        pkt_sizes: '64'
        bidirectional: 'True'
        iload: 100
        duration: 30
        trafficgen_port1: 'eth1'
        trafficgen_port2: 'eth3'
        external_bridge: 'br-ex'
        conf-file: '~/vsperf-yardstick.conf'

      host: vsperf.demo

      runner:
        type: Sequence
        scenario_option_name: pkt_sizes
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
- **pkt_sizes** - a packet size for which test should be executed;
  Multiple packet sizes can be tested by modification of Sequence runner
  section inside YAML definition. Default: '64'
- **duration** - sets duration for which traffic will be generated; Default: 30
- **bidirectional** - specifies if traffic will be uni (False) or bi-directional
  (True); Default: False
- **iload** - specifies frame rate; Default: 100
- **rfc2544_trials** - specifies the number of trials performed for each packet
  size
- **multistream** - specifies the number of simulated streams; Default: 0 (i.e.
  multistream feature is disabled)
- **stream_type** - specifies network layer used for multistream simulation
  the valid values are "L4", "L3" and "L2"; Default: 'L4'
- **conf-file** - sets path to the vswitchperf configuration file, which will be
  uploaded to VM; Default: '~/vsperf-yardstick.conf'
- **setup-script** - sets path to the setup script, which will be executed
  during setup and teardown phases
- **trafficgen_port1** - specifies device name of 1st interface connected to
  the trafficgen
- **trafficgen_port2** - specifies device name of 2nd interface connected to
  the trafficgen
- **external_bridge** - specifies name of external bridge configured in OVS;
  Default: 'br-ex'

In case that **trafficgen_port1** and/or **trafficgen_port2** are defined, then
these interfaces will be inserted into the **external_bridge** of OVS. It is
expected, that OVS runs at the same node, where the testcase is executed. In case
of more complex OpenStack installation or a need of additional OVS configuration,
**setup-script** can be used.

Note: It is essential to prepare customized configuration file for the vsperf
and to specify its name by **conf-file** option. Config file must specify, which
traffic generator will be used and configure traffic generator specific options.

Section runner
~~~~~~~~~~~~~~

Yardstick supports several `runner types
<http://artifacts.opnfv.org/yardstick/brahmaputra/docs/userguide/architecture.html#runner-types>`__.
In case of vswitchperf specific TCs, **Sequence** runner type can be used to
execute the testcase for given list of packet sizes.


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

Testcase execution
^^^^^^^^^^^^^^^^^^

After installation, yardstick is available as python package within yardstick
specific virtual environment. It means, that before test execution yardstick
environment must be enabled, e.g.:

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

   yardstick -d task start yardstick/tests/p2p_cont.yaml

Note: Option argument ``-d`` shows debug output.
