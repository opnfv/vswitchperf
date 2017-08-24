.. This work is licensed under a Creative Commons Attribution 4.0 International License.
.. http://creativecommons.org/licenses/by/4.0
.. (c) OPNFV, Intel Corporation, AT&T and others.

.. _trafficgen-installation:

===========================
'vsperf' Traffic Gen Guide
===========================

Overview
--------

VSPERF supports the following traffic generators:

  * Dummy_ (DEFAULT)
  * Ixia_
  * `Spirent TestCenter`_
  * `Xena Networks`_
  * MoonGen_
  * Trex_

To see the list of traffic gens from the cli:

.. code-block:: console

    $ ./vsperf --list-trafficgens

This guide provides the details of how to install
and configure the various traffic generators.

Background Information
----------------------
The traffic default configuration can be found in **conf/03_traffic.conf**,
and is configured as follows:

.. code-block:: console

    TRAFFIC = {
        'traffic_type' : 'rfc2544_throughput',
        'frame_rate' : 100,
        'bidir' : 'True',  # will be passed as string in title format to tgen
        'multistream' : 0,
        'stream_type' : 'L4',
        'pre_installed_flows' : 'No',           # used by vswitch implementation
        'flow_type' : 'port',                   # used by vswitch implementation

        'l2': {
            'framesize': 64,
            'srcmac': '00:00:00:00:00:00',
            'dstmac': '00:00:00:00:00:00',
        },
        'l3': {
            'enabled': True,
            'proto': 'udp',
            'srcip': '1.1.1.1',
            'dstip': '90.90.90.90',
        },
        'l4': {
            'enabled': True,
            'srcport': 3000,
            'dstport': 3001,
        },
        'vlan': {
            'enabled': False,
            'id': 0,
            'priority': 0,
            'cfi': 0,
        },
    }

The framesize parameter can be overridden from the configuration
files by adding the following to your custom configuration file
``10_custom.conf``:

.. code-block:: console

    TRAFFICGEN_PKT_SIZES = (64, 128,)

OR from the commandline:

.. code-block:: console

    $ ./vsperf --test-params "TRAFFICGEN_PKT_SIZES=(x,y)" $TESTNAME

You can also modify the traffic transmission duration and the number
of tests run by the traffic generator by extending the example
commandline above to:

.. code-block:: console

    $ ./vsperf --test-params "TRAFFICGEN_PKT_SIZES=(x,y);TRAFFICGEN_DURATION=10;" \
                             "TRAFFICGEN_RFC2544_TESTS=1" $TESTNAME

.. _trafficgen-dummy:

Dummy
-----

The Dummy traffic generator can be used to test VSPERF installation or
to demonstrate VSPERF functionality at DUT without connection
to a real traffic generator.

You could also use the Dummy generator in case, that your external
traffic generator is not supported by VSPERF. In such case you could
use VSPERF to setup your test scenario and then transmit the traffic.
After the transmission is completed you could specify values for all
collected metrics and VSPERF will use them to generate final reports.

Setup
~~~~~

To select the Dummy generator please add the following to your
custom configuration file ``10_custom.conf``.

.. code-block:: console

     TRAFFICGEN = 'Dummy'

OR run ``vsperf`` with the ``--trafficgen`` argument

.. code-block:: console

    $ ./vsperf --trafficgen Dummy $TESTNAME

Where $TESTNAME is the name of the vsperf test you would like to run.
This will setup the vSwitch and the VNF (if one is part of your test)
print the traffic configuration and prompt you to transmit traffic
when the setup is complete.

.. code-block:: console

    Please send 'continuous' traffic with the following stream config:
    30mS, 90mpps, multistream False
    and the following flow config:
    {
        "flow_type": "port",
        "l3": {
            "enabled": True,
            "srcip": "1.1.1.1",
            "proto": "udp",
            "dstip": "90.90.90.90"
        },
        "traffic_type": "rfc2544_continuous",
        "multistream": 0,
        "bidir": "True",
        "vlan": {
            "cfi": 0,
            "priority": 0,
            "id": 0,
            "enabled": False
        },
        "l4": {
            "enabled": True,
            "srcport": 3000,
            "dstport": 3001,
        },
        "frame_rate": 90,
        "l2": {
            "dstmac": "00:00:00:00:00:00",
            "srcmac": "00:00:00:00:00:00",
            "framesize": 64
        }
    }
    What was the result for 'frames tx'?

When your traffic generator has completed traffic transmission and provided
the results please input these at the VSPERF prompt. VSPERF will try
to verify the input:

.. code-block:: console

    Is '$input_value' correct?

Please answer with y OR n.

VSPERF will ask you to provide a value for every of collected metrics. The list
of metrics can be found at traffic-type-metrics_.
Finally vsperf will print out the results for your test and generate the
appropriate logs and report files.

.. _traffic-type-metrics:

Metrics collected for supported traffic types
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Below you could find a list of metrics collected by VSPERF for each of supported
traffic types.

RFC2544 Throughput and Continuous:

  * frames tx
  * frames rx
  * min latency
  * max latency
  * avg latency
  * frameloss

RFC2544 Back2back:

  * b2b frames
  * b2b frame loss %

Dummy result pre-configuration
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

In case of a Dummy traffic generator it is possible to pre-configure the test
results. This is useful for creation of demo testcases, which do not require
a real traffic generator. Such testcase can be run by any user and it will still
generate all reports and result files.

Result values can be specified within ``TRAFFICGEN_DUMMY_RESULTS`` dictionary,
where every of collected metrics must be properly defined. Please check the list
of traffic-type-metrics_.

Dictionary with dummy results can be passed by CLI argument ``--test-params``
or specified in ``Parameters`` section of testcase definition.

Example of testcase execution with dummy results defined by CLI argument:

.. code-block:: console

    $ ./vsperf back2back --trafficgen Dummy --test-params \
      "TRAFFICGEN_DUMMY_RESULTS={'b2b frames':'3000','b2b frame loss %':'0.0'}"

Example of testcase definition with pre-configured dummy results:

.. code-block:: python

    {
        "Name": "back2back",
        "Traffic Type": "rfc2544_back2back",
        "Deployment": "p2p",
        "biDirectional": "True",
        "Description": "LTD.Throughput.RFC2544.BackToBackFrames",
        "Parameters" : {
            'TRAFFICGEN_DUMMY_RESULTS' : {'b2b frames':'3000','b2b frame loss %':'0.0'}
        },
    },

**NOTE:** Pre-configured results for the Dummy traffic generator will be used only
in case, that the Dummy traffic generator is used. Otherwise the option
``TRAFFICGEN_DUMMY_RESULTS`` will be ignored.

.. _Ixia:

Ixia
----

VSPERF can use both IxNetwork and IxExplorer TCL servers to control Ixia chassis.
However usage of IxNetwork TCL server is a preferred option. Following sections
will describe installation and configuration of IxNetwork components used by VSPERF.

Installation
~~~~~~~~~~~~

On the system under the test you need to install IxNetworkTclClient$(VER\_NUM)Linux.bin.tgz.

On the IXIA client software system you need to install IxNetwork TCL server. After its
installation you should configure it as follows:

    1. Find the IxNetwork TCL server app (start -> All Programs -> IXIA ->
       IxNetwork -> IxNetwork\_$(VER\_NUM) -> IxNetwork TCL Server)
    2. Right click on IxNetwork TCL Server, select properties - Under shortcut tab in
       the Target dialogue box make sure there is the argument "-tclport xxxx"
       where xxxx is your port number (take note of this port number as you will
       need it for the 10\_custom.conf file).

       .. image:: TCLServerProperties.png

    3. Hit Ok and start the TCL server application

VSPERF configuration
~~~~~~~~~~~~~~~~~~~~

There are several configuration options specific to the IxNetwork traffic generator
from IXIA. It is essential to set them correctly, before the VSPERF is executed
for the first time.

Detailed description of options follows:

 * ``TRAFFICGEN_IXNET_MACHINE`` - IP address of server, where IxNetwork TCL Server is running
 * ``TRAFFICGEN_IXNET_PORT`` - PORT, where IxNetwork TCL Server is accepting connections from
   TCL clients
 * ``TRAFFICGEN_IXNET_USER`` - username, which will be used during communication with IxNetwork
   TCL Server and IXIA chassis
 * ``TRAFFICGEN_IXIA_HOST`` - IP address of IXIA traffic generator chassis
 * ``TRAFFICGEN_IXIA_CARD`` - identification of card with dedicated ports at IXIA chassis
 * ``TRAFFICGEN_IXIA_PORT1`` - identification of the first dedicated port at ``TRAFFICGEN_IXIA_CARD``
   at IXIA chassis; VSPERF uses two separated ports for traffic generation. In case of
   unidirectional traffic, it is essential to correctly connect 1st IXIA port to the 1st NIC
   at DUT, i.e. to the first PCI handle from ``WHITELIST_NICS`` list. Otherwise traffic may not
   be able to pass through the vSwitch.
   **NOTE**: In case that ``TRAFFICGEN_IXIA_PORT1`` and ``TRAFFICGEN_IXIA_PORT2`` are set to the
   same value, then VSPERF will assume, that there is only one port connection between IXIA
   and DUT. In this case it must be ensured, that chosen IXIA port is physically connected to the
   first NIC from ``WHITELIST_NICS`` list.
 * ``TRAFFICGEN_IXIA_PORT2`` - identification of the second dedicated port at ``TRAFFICGEN_IXIA_CARD``
   at IXIA chassis; VSPERF uses two separated ports for traffic generation. In case of
   unidirectional traffic, it is essential to correctly connect 2nd IXIA port to the 2nd NIC
   at DUT, i.e. to the second PCI handle from ``WHITELIST_NICS`` list. Otherwise traffic may not
   be able to pass through the vSwitch.
   **NOTE**: In case that ``TRAFFICGEN_IXIA_PORT1`` and ``TRAFFICGEN_IXIA_PORT2`` are set to the
   same value, then VSPERF will assume, that there is only one port connection between IXIA
   and DUT. In this case it must be ensured, that chosen IXIA port is physically connected to the
   first NIC from ``WHITELIST_NICS`` list.
 * ``TRAFFICGEN_IXNET_LIB_PATH`` - path to the DUT specific installation of IxNetwork TCL API
 * ``TRAFFICGEN_IXNET_TCL_SCRIPT`` - name of the TCL script, which VSPERF will use for
   communication with IXIA TCL server
 * ``TRAFFICGEN_IXNET_TESTER_RESULT_DIR`` - folder accessible from IxNetwork TCL server,
   where test results are stored, e.g. ``c:/ixia_results``; see test-results-share_
 * ``TRAFFICGEN_IXNET_DUT_RESULT_DIR`` - directory accessible from the DUT, where test
   results from IxNetwork TCL server are stored, e.g. ``/mnt/ixia_results``; see
   test-results-share_

.. _test-results-share:

Test results share
~~~~~~~~~~~~~~~~~~

VSPERF is not able to retrieve test results via TCL API directly. Instead, all test
results are stored at IxNetwork TCL server. Results are stored at folder defined by
``TRAFFICGEN_IXNET_TESTER_RESULT_DIR`` configuration parameter. Content of this
folder must be shared (e.g. via samba protocol) between TCL Server and DUT, where
VSPERF is executed. VSPERF expects, that test results will be available at directory
configured by ``TRAFFICGEN_IXNET_DUT_RESULT_DIR`` configuration parameter.

Example of sharing configuration:

 * Create a new folder at IxNetwork TCL server machine, e.g. ``c:\ixia_results``
 * Modify sharing options of ``ixia_results`` folder to share it with everybody
 * Create a new directory at DUT, where shared directory with results
   will be mounted, e.g. ``/mnt/ixia_results``
 * Update your custom VSPERF configuration file as follows:

   .. code-block:: python

       TRAFFICGEN_IXNET_TESTER_RESULT_DIR = 'c:/ixia_results'
       TRAFFICGEN_IXNET_DUT_RESULT_DIR = '/mnt/ixia_results'

   **NOTE:** It is essential to use slashes '/' also in path
   configured by ``TRAFFICGEN_IXNET_TESTER_RESULT_DIR`` parameter.
 * Install cifs-utils package.

   e.g. at rpm based Linux distribution:

   .. code-block:: console

       yum install cifs-utils

 * Mount shared directory, so VSPERF can access test results.

   e.g. by adding new record into ``/etc/fstab``

   .. code-block:: console

       mount -t cifs //_TCL_SERVER_IP_OR_FQDN_/ixia_results /mnt/ixia_results
             -o file_mode=0777,dir_mode=0777,nounix

It is recommended to verify, that any new file inserted into ``c:/ixia_results`` folder
is visible at DUT inside ``/mnt/ixia_results`` directory.

.. _`Spirent TestCenter`:

Spirent Setup
-------------

Spirent installation files and instructions are available on the
Spirent support website at:

http://support.spirent.com

Select a version of Spirent TestCenter software to utilize. This example
will use Spirent TestCenter v4.57 as an example. Substitute the appropriate
version in place of 'v4.57' in the examples, below.

On the CentOS 7 System
~~~~~~~~~~~~~~~~~~~~~~

Download and install the following:

Spirent TestCenter Application, v4.57 for 64-bit Linux Client

Spirent Virtual Deployment Service (VDS)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Spirent VDS is required for both TestCenter hardware and virtual
chassis in the vsperf environment. For installation, select the version
that matches the Spirent TestCenter Application version. For v4.57,
the matching VDS version is 1.0.55. Download either the ova (VMware)
or qcow2 (QEMU) image and create a VM with it. Initialize the VM
according to Spirent installation instructions.

Using Spirent TestCenter Virtual (STCv)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

STCv is available in both ova (VMware) and qcow2 (QEMU) formats. For
VMware, download:

Spirent TestCenter Virtual Machine for VMware, v4.57 for Hypervisor - VMware ESX.ESXi

Virtual test port performance is affected by the hypervisor configuration. For
best practice results in deploying STCv, the following is suggested:

- Create a single VM with two test ports rather than two VMs with one port each
- Set STCv in DPDK mode
- Give STCv 2*n + 1 cores, where n = the number of ports. For vsperf, cores = 5.
- Turning off hyperthreading and pinning these cores will improve performance
- Give STCv 2 GB of RAM

To get the highest performance and accuracy, Spirent TestCenter hardware is
recommended. vsperf can run with either stype test ports.

Using STC REST Client
~~~~~~~~~~~~~~~~~~~~~
The stcrestclient package provides the stchttp.py ReST API wrapper module.
This allows simple function calls, nearly identical to those provided by
StcPython.py, to be used to access TestCenter server sessions via the
STC ReST API. Basic ReST functionality is provided by the resthttp module,
and may be used for writing ReST clients independent of STC.

- Project page: <https://github.com/Spirent/py-stcrestclient>
- Package download: <http://pypi.python.org/pypi/stcrestclient>

To use REST interface, follow the instructions in the Project page to
install the package. Once installed, the scripts named with 'rest' keyword
can be used. For example: testcenter-rfc2544-rest.py can be used to run
RFC 2544 tests using the REST interface.

Configuration:
~~~~~~~~~~~~~~

1. The Labserver and license server addresses. These parameters applies to
   all the tests, and are mandatory for all tests.

.. code-block:: console

    TRAFFICGEN_STC_LAB_SERVER_ADDR = " "
    TRAFFICGEN_STC_LICENSE_SERVER_ADDR = " "
    TRAFFICGEN_STC_PYTHON2_PATH = " "
    TRAFFICGEN_STC_TESTCENTER_PATH = " "
    TRAFFICGEN_STC_TEST_SESSION_NAME = " "
    TRAFFICGEN_STC_CSV_RESULTS_FILE_PREFIX = " "

2. For RFC2544 tests, the following parameters are mandatory

.. code-block:: console

    TRAFFICGEN_STC_EAST_CHASSIS_ADDR = " "
    TRAFFICGEN_STC_EAST_SLOT_NUM = " "
    TRAFFICGEN_STC_EAST_PORT_NUM = " "
    TRAFFICGEN_STC_EAST_INTF_ADDR = " "
    TRAFFICGEN_STC_EAST_INTF_GATEWAY_ADDR = " "
    TRAFFICGEN_STC_WEST_CHASSIS_ADDR = ""
    TRAFFICGEN_STC_WEST_SLOT_NUM = " "
    TRAFFICGEN_STC_WEST_PORT_NUM = " "
    TRAFFICGEN_STC_WEST_INTF_ADDR = " "
    TRAFFICGEN_STC_WEST_INTF_GATEWAY_ADDR = " "
    TRAFFICGEN_STC_RFC2544_TPUT_TEST_FILE_NAME

3. RFC2889 tests: Currently, the forwarding, address-caching, and
   address-learning-rate tests of RFC2889 are supported.
   The testcenter-rfc2889-rest.py script implements the rfc2889 tests.
   The configuration for RFC2889 involves test-case definition, and parameter
   definition, as described below. New results-constants, as shown below, are
   added to support these tests.

Example of testcase definition for RFC2889 tests:

.. code-block:: python

    {
        "Name": "phy2phy_forwarding",
        "Deployment": "p2p",
        "Description": "LTD.Forwarding.RFC2889.MaxForwardingRate",
        "Parameters" : {
            "TRAFFIC" : {
                "traffic_type" : "rfc2889_forwarding",
            },
        },
    }

For RFC2889 tests, specifying the locations for the monitoring ports is mandatory.
Necessary parameters are:

.. code-block:: console

    TRAFFICGEN_STC_RFC2889_TEST_FILE_NAME
    TRAFFICGEN_STC_EAST_CHASSIS_ADDR = " "
    TRAFFICGEN_STC_EAST_SLOT_NUM = " "
    TRAFFICGEN_STC_EAST_PORT_NUM = " "
    TRAFFICGEN_STC_EAST_INTF_ADDR = " "
    TRAFFICGEN_STC_EAST_INTF_GATEWAY_ADDR = " "
    TRAFFICGEN_STC_WEST_CHASSIS_ADDR = ""
    TRAFFICGEN_STC_WEST_SLOT_NUM = " "
    TRAFFICGEN_STC_WEST_PORT_NUM = " "
    TRAFFICGEN_STC_WEST_INTF_ADDR = " "
    TRAFFICGEN_STC_WEST_INTF_GATEWAY_ADDR = " "
    TRAFFICGEN_STC_VERBOSE = "True"
    TRAFFICGEN_STC_RFC2889_LOCATIONS="//10.1.1.1/1/1,//10.1.1.1/2/2"

Other Configurations are :

.. code-block:: console

    TRAFFICGEN_STC_RFC2889_MIN_LR = 1488
    TRAFFICGEN_STC_RFC2889_MAX_LR = 14880
    TRAFFICGEN_STC_RFC2889_MIN_ADDRS = 1000
    TRAFFICGEN_STC_RFC2889_MAX_ADDRS = 65536
    TRAFFICGEN_STC_RFC2889_AC_LR = 1000

The first 2 values are for address-learning test where as other 3 values are
for the Address caching capacity test. LR: Learning Rate. AC: Address Caching.
Maximum value for address is 16777216. Whereas, maximum for LR is 4294967295.

Results for RFC2889 Tests: Forwarding tests outputs following values:

.. code-block:: console

    TX_RATE_FPS : "Transmission Rate in Frames/sec"
    THROUGHPUT_RX_FPS: "Received Throughput Frames/sec"
    TX_RATE_MBPS : " Transmission rate in MBPS"
    THROUGHPUT_RX_MBPS: "Received Throughput in MBPS"
    TX_RATE_PERCENT: "Transmission Rate in Percentage"
    FRAME_LOSS_PERCENT: "Frame loss in Percentage"
    FORWARDING_RATE_FPS: " Maximum Forwarding Rate in FPS"


Whereas, the address caching test outputs following values,

.. code-block:: console

    CACHING_CAPACITY_ADDRS = 'Number of address it can cache'
    ADDR_LEARNED_PERCENT = 'Percentage of address successfully learned'

and address learning test outputs just a single value:

.. code-block:: console

    OPTIMAL_LEARNING_RATE_FPS = 'Optimal learning rate in fps'

Note that 'FORWARDING_RATE_FPS', 'CACHING_CAPACITY_ADDRS',
'ADDR_LEARNED_PERCENT' and 'OPTIMAL_LEARNING_RATE_FPS' are the new
result-constants added to support RFC2889 tests.

.. _`Xena Networks`:

Xena Networks
-------------

Installation
~~~~~~~~~~~~

Xena Networks traffic generator requires specific files and packages to be
installed. It is assumed the user has access to the Xena2544.exe file which
must be placed in VSPerf installation location under the tools/pkt_gen/xena
folder. Contact Xena Networks for the latest version of this file. The user
can also visit www.xenanetworks/downloads to obtain the file with a valid
support contract.

**Note** VSPerf has been fully tested with version v2.43 of Xena2544.exe

To execute the Xena2544.exe file under Linux distributions the mono-complete
package must be installed. To install this package follow the instructions
below. Further information can be obtained from
http://www.mono-project.com/docs/getting-started/install/linux/

.. code-block:: console

    rpm --import "http://keyserver.ubuntu.com/pks/lookup?op=get&search=0x3FA7E0328081BFF6A14DA29AA6A19B38D3D831EF"
    yum-config-manager --add-repo http://download.mono-project.com/repo/centos/
    yum -y install mono-complete

To prevent gpg errors on future yum installation of packages the mono-project
repo should be disabled once installed.

.. code-block:: console

    yum-config-manager --disable download.mono-project.com_repo_centos_

Configuration
~~~~~~~~~~~~~

Connection information for your Xena Chassis must be supplied inside the
``10_custom.conf`` or ``03_custom.conf`` file. The following parameters must be
set to allow for proper connections to the chassis.

.. code-block:: console

    TRAFFICGEN_XENA_IP = ''
    TRAFFICGEN_XENA_PORT1 = ''
    TRAFFICGEN_XENA_PORT2 = ''
    TRAFFICGEN_XENA_USER = ''
    TRAFFICGEN_XENA_PASSWORD = ''
    TRAFFICGEN_XENA_MODULE1 = ''
    TRAFFICGEN_XENA_MODULE2 = ''

RFC2544 Throughput Testing
~~~~~~~~~~~~~~~~~~~~~~~~~~

Xena traffic generator testing for rfc2544 throughput can be modified for
different behaviors if needed. The default options for the following are
optimized for best results.

.. code-block:: console

    TRAFFICGEN_XENA_2544_TPUT_INIT_VALUE = '10.0'
    TRAFFICGEN_XENA_2544_TPUT_MIN_VALUE = '0.1'
    TRAFFICGEN_XENA_2544_TPUT_MAX_VALUE = '100.0'
    TRAFFICGEN_XENA_2544_TPUT_VALUE_RESOLUTION = '0.5'
    TRAFFICGEN_XENA_2544_TPUT_USEPASS_THRESHHOLD = 'false'
    TRAFFICGEN_XENA_2544_TPUT_PASS_THRESHHOLD = '0.0'

Each value modifies the behavior of rfc 2544 throughput testing. Refer to your
Xena documentation to understand the behavior changes in modifying these
values.

Xena RFC2544 testing inside VSPerf also includes a final verification option.
This option allows for a faster binary search with a longer final verification
of the binary search result. This feature can be enabled in the configuration
files as well as the length of the final verification in seconds.

..code-block:: python

    TRAFFICGEN_XENA_RFC2544_VERIFY = False
    TRAFFICGEN_XENA_RFC2544_VERIFY_DURATION = 120

If the final verification does not pass the test with the lossrate specified
it will continue the binary search from its previous point. If the smart search
option is enabled the search will continue by taking the current pass rate minus
the minimum and divided by 2. The maximum is set to the last pass rate minus the
threshold value set.

For example if the settings are as follows

..code-block:: python

    TRAFFICGEN_XENA_RFC2544_BINARY_RESTART_SMART_SEARCH = True
    TRAFFICGEN_XENA_2544_TPUT_MIN_VALUE = '0.5'
    TRAFFICGEN_XENA_2544_TPUT_VALUE_RESOLUTION = '0.5'

and the verification attempt was 64.5, smart search would take 64.5 - 0.5 / 2.
This would continue the search at 32 but still have a maximum possible value of
64.

If smart is not enabled it will just resume at the last pass rate minus the
threshold value.

Continuous Traffic Testing
~~~~~~~~~~~~~~~~~~~~~~~~~~

Xena continuous traffic by default does a 3 second learning preemption to allow
the DUT to receive learning packets before a continuous test is performed. If
a custom test case requires this learning be disabled, you can disable the option
or modify the length of the learning by modifying the following settings.

.. code-block:: console

    TRAFFICGEN_XENA_CONT_PORT_LEARNING_ENABLED = False
    TRAFFICGEN_XENA_CONT_PORT_LEARNING_DURATION = 3

MoonGen
-------

Installation
~~~~~~~~~~~~

MoonGen architecture overview and general installation instructions
can be found here:

https://github.com/emmericp/MoonGen

* Note:  Today, MoonGen with VSPERF only supports 10Gbps line speeds.

For VSPERF use, MoonGen should be cloned from here (as opposed to the
previously mentioned GitHub):

git clone https://github.com/atheurer/lua-trafficgen

and use the master branch:

git checkout master

VSPERF uses a particular Lua script with the MoonGen project:

trafficgen.lua

Follow MoonGen set up and execution instructions here:

https://github.com/atheurer/lua-trafficgen/blob/master/README.md

Note one will need to set up ssh login to not use passwords between the server
running MoonGen and the device under test (running the VSPERF test
infrastructure).  This is because VSPERF on one server uses 'ssh' to
configure and run MoonGen upon the other server.

One can set up this ssh access by doing the following on both servers:

.. code-block:: console

    ssh-keygen -b 2048 -t rsa
    ssh-copy-id <other server>

Configuration
~~~~~~~~~~~~~

Connection information for MoonGen must be supplied inside the
``10_custom.conf`` or ``03_custom.conf`` file. The following parameters must be
set to allow for proper connections to the host with MoonGen.

.. code-block:: console

    TRAFFICGEN_MOONGEN_HOST_IP_ADDR = ""
    TRAFFICGEN_MOONGEN_USER = ""
    TRAFFICGEN_MOONGEN_BASE_DIR = ""
    TRAFFICGEN_MOONGEN_PORTS = ""
    TRAFFICGEN_MOONGEN_LINE_SPEED_GBPS = ""

Trex
----

Installation
~~~~~~~~~~~~

Trex architecture overview and general installation instructions
can be found here:

https://trex-tgn.cisco.com/trex/doc/trex_stateless.html

You can directly download from GitHub:

.. code-block:: console

    git clone https://github.com/cisco-system-traffic-generator/trex-core

and use the master branch:

.. code-block:: console

    git checkout master

or Trex latest realease you can download from here:

.. code-block:: console

    wget --no-cache http://trex-tgn.cisco.com/trex/release/latest

After download, Trex repo has to be built:

.. code-block:: console

   cd trex-core/linux_dpdk
   ./b configure   (run only once)
   ./b build

Next step is to create a minimum configuration file. It can be created by script ``dpdk_setup_ports.py``.
The script with parameter ``-i`` will run in interactive mode and it will create file ``/etc/trex_cfg.yaml``.

.. code-block:: console

   cd trex-core/scripts
   sudo ./dpdk_setup_ports.py -i

Or example of configuration file can be found at location below, but it must be updated manually:

.. code-block:: console

   cp trex-core/scripts/cfg/simple_cfg /etc/trex_cfg.yaml

For additional information about configuration file see official documentation (chapter 3.1.2):

https://trex-tgn.cisco.com/trex/doc/trex_manual.html#_creating_minimum_configuration_file

After compilation and configuration it is possible to run trex server in stateless mode.
It is neccesary for proper connection between Trex server and VSPERF.

.. code-block:: console

   cd trex-core/scripts/
   ./t-rex-64 -i

For additional information about Trex stateless mode see Trex stateless documentation:

https://trex-tgn.cisco.com/trex/doc/trex_stateless.html

**NOTE:** One will need to set up ssh login to not use passwords between the server
running Trex and the device under test (running the VSPERF test
infrastructure). This is because VSPERF on one server uses 'ssh' to
configure and run Trex upon the other server.

One can set up this ssh access by doing the following on both servers:

.. code-block:: console

    ssh-keygen -b 2048 -t rsa
    ssh-copy-id <other server>
    

Configuration
~~~~~~~~~~~~~

Connection information for Trex must be supplied inside the custom configuration
file. The following parameters must be set to allow for proper connections to the host with Trex.
Example of this configuration is in conf/03_traffic.conf or conf/10_custom.conf.

.. code-block:: console

    TRAFFICGEN_TREX_HOST_IP_ADDR = ''
    TRAFFICGEN_TREX_USER = ''
    TRAFFICGEN_TREX_BASE_DIR = ''

TRAFFICGEN_TREX_USER has to have sudo permission and passwordless access.
TRAFFICGEN_TREX_BASE_DIR is the place, where is stored 't-rex-64' file.
