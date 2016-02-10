*****************************
Adding new testcase in VSPERF
*****************************

A Testcase in VSPERF is defined as encompassing following attributes.

+------------+------------+----------------------------------------------------+ 
| Attribute  | Value      | Description                                        |
+============+============+====================================================+ 
| Name       |            | A human-readable string identifying the test       |
+------------+------------+----------------------------------------------------+
|Traffic     | rfc2544    | One of the supported traffic types                 |     
|Type        | rfc2889 .. |                                                    |
+------------+------------+----------------------------------------------------+
|Deployment  | true|false | Specifies if generated traffic will be full-duplex |
|            |            | (true) or half-duplex (false)                      | 
+------------+------------+----------------------------------------------------+
|Frame       |vlan, ...   | One of the supported frame modifications: vlan,    |
|Mofication  |            | mpls, mac, dscp, ttl, ip_addr, ip_port             |
+------------+------------+----------------------------------------------------+
|Description |            | A human-readable string describing the test.       |
+------------+------------+----------------------------------------------------+
|MultiStream | 0-65535    | Defines number of flows simulated by traffic       |
|            |            | generator. Value 0 disables MultiStream feature.   |     
+------------+------------+----------------------------------------------------+
|Flow Type   |"port"|"IP" | Defines flows complexity. If it isn't specified,   |
|            |            | then "port" will be used. "port": Flow is defined  |
|            |            | by ingress ports "IP": Flow is defined by ingress  |
|            |            | ports and src & dst IP addresses.                  |
+------------+------------+----------------------------------------------------+
| iLoad      | 0-100      | Defines desired percentage of frame rate used      |
|            |            | during continuous stream tests. It is related to   |
|            |            | intended load from the traffic generator.          | 
+------------+------------+----------------------------------------------------+
| Load       | Dictionary | Configures background load for testcase execution  |
+------------+------------+----------------------------------------------------+
| load       | 0-100      | Defines target core utilization. That is, %ge of   |
|            |            | cores which should be utilized by load generator.  |
+------------+------------+----------------------------------------------------+
| Tool       |"stress"    | One of the supported load generators               |
+------------+------------+----------------------------------------------------+
| reserved   | 0-100      | Defines number of cores reserved for vsperf        |
+------------+------------+----------------------------------------------------+
|pattern     | c*m*i*     |stress/stress-ng specific; Number of 'c', 'm' & 'i' |
|            |            |defines ratio between cpu, mem and io workers. EX:  |
|            |            |"cccmmi" => ratio among workers types will be 3:2:1 |
|            |            |So in case that 12 stress instances should be used  |
|            |            |then 6-cpu, 4-mem and 2-io workers will be executed |
+------------+------------+----------------------------------------------------+
|load_memory |0-100       |Defines %-ge of the system memory, which should be  |
|            |            |be utilized by memory workers.  if not specified    |
|            |            |then default stress(-ng) value will be used.        |
+------------+------------+----------------------------------------------------+
|options     |            |Additional CLI-opts to be passed to load generator  |
+------------+------------+----------------------------------------------------+
|Test        |FrameMod or |                                                    |
|Modifier    | others     |                                                    |
+------------+------------+----------------------------------------------------+
|Dependency  |TestCaseName| The Dependency of the current case on other        |
|            | or  None   | test case                                          |
+------------+------------+----------------------------------------------------+

The process of adding a new testcase could mean one of these two:

1. Creating a testcase with Different configuration using existing supported values. This case is straight forward, and involves modifying the configurable parameters. You will have new testcase, with the given configuration. The configuration file can be found in: ``$HOME/conf/01_testcases.conf``. In this article ``$HOME`` refers to - ``path_where_vswitchperf_code_resides/vswitchperf``.

2. Creating a testcase by adding new supported values for any of the testcase attributes. For example, Traffic type, Deployment Scenarios, Frame Modification, Tool for workload generation, etc. In this article, we will consider the attribute Traffic Type for describing the process in detail.

Adding additional traffic-type
==============================
As a case-study, consider you are new traffic generator vendor by name ``Super``, and consider you want to support RFC2889 traffic type. The complete process of adding a new testcase in this scenario can be explained in following steps:

1. Implementation of Traffic Generator:
---------------------------------------
- Configuration parameters: ``TRAFFICGEN_DIR: $HOME/tools/pkt_gen/`` ``TRAFFICGEN: Super``
- Create a new trafficgen folder in ``$HOME/tools/pkt_gen`` and assign it to ``TRAFFICGEN`` parameter. In case where you want to consider existing folders , for ex Ixia or Spirent's testcenter, (if you represent these organizations) this step is not required. Consider you create a folder named ``Super`` for your Super traffic-generator.
- Create a class that inherits from ``trafficgen.ITrafficGenerator`` class. Ex: Create a file ``SuperTraffic.py`` and add ``class SuperTraffic(trafficgen.ITrafficGenerator)``. Again,If you are modifying the file existing folder, just update it to support new traffic generation functions. 
- Implement Traffic generation functions - add function to the class that will generate actual traffic. Note that these functions will be called from the traffic controller. For example, in Class ``SuperTraffic``, implement functions : ``send/connect/disconnect``, appropriately.

2. Writing Custom Traffic Controller:
-------------------------------------
The next step is to write custom traffic controller for the ``Super`` traffic generator. 

- A new traffic-controller class has to that Inherit from ``ITrafficController`` class defined in ``$HOME/core/traffic_controller.py`` and from ``IResults`` class defined in ``$HOME/core/results/results.py``. ``ITrafficController`` sets up and controls the traffic generator for a particular scenario, whereas ``IResults`` focus on gathering results.
- Ensure that you name the classes and files appropriately. In this case, the class name would be ``class TrafficControllerRFC2889(ITrafficController, IResults)`` and the file name would be ``traffic_controller_rfc2889.py``. Place the file in ``$HOME/core/``. 
- Implement the necessary functions of the parent classes. From the parent `` ItrafficController`` class implement ``send_traffic``, ``send_traffic_async``, and ``stop_traffic``. Whereas, from the parent ``IResults`` class ``print_results`` and ``get_results``. Add additional functions appropriately to the class. These functions actually call the functions in the new written traffic generator.

3. Update Component Factory:
----------------------------
Update the file ``$HOME/core/component_factory.py`` with the following changes. 

- Add appropriate import: in this case, it would be ``from core.traffic_controller_rfc2889 import TrafficControllerRFC2889``
- In ``create_traffic`` function, make necessary changes. Check for the type, if it is rfc2889, and return ``TrafficControllerRFC2889(trafficgen_class)`` object

4. Configurations Required:
---------------------------
Finally, the configuration specific changes that are required are: (Note: The configuration folder where the below files reside is ``$HOME/conf/``)

- In File: `03_traffic.conf`, Specify the `TRAFFICGEN` parameter. In this case, it would be `super`. In addition, specify parameters required for your custom traffic generator. That is you may end up creating bunch of `TRAFFICGEN_SUPER_*` parameters that are required for your traffic generation process.
- In File: 01_testcase.conf, under Performance_tests[], add your custom test case:

For example:

| "Name": "phy2phy_2889"
| "Traffic Type": "rfc2889"
| "Deployment": "p2p",
| "biDirectional": "True",
| "Description": " RFC 2889 Test by Super"


Run the new testcase:
=====================


We have two options to run our new test case. In either case, ensure you have right configurations in ``01_testcase.conf``. The first option is to run only your testcase. For this, we can run vsperf with ``--exact_test_name`` as a input argument, and give the name that is provided in the ``01_testcase.conf``. The second option is to run your testcase along with other testcase. For this, run vsperf without the ``--exact_test_name`` argument.
