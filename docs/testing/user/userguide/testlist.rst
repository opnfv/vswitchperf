.. This work is licensed under a Creative Commons Attribution 4.0 International License.
.. http://creativecommons.org/licenses/by/4.0
.. (c) OPNFV, Intel Corporation, AT&T and others.

List of vswitchperf testcases
-----------------------------

Performance testcases
^^^^^^^^^^^^^^^^^^^^^

=============================  ====================================================================
Testcase Name                  Description
=============================  ====================================================================
phy2phy_tput                   LTD.Throughput.RFC2544.PacketLossRatio
phy2phy_forwarding             LTD.Forwarding.RFC2889.MaxForwardingRate
phy2phy_learning               LTD.AddrLearning.RFC2889.AddrLearningRate
phy2phy_caching                LTD.AddrCaching.RFC2889.AddrCachingCapacity
back2back                      LTD.Throughput.RFC2544.BackToBackFrames
phy2phy_tput_mod_vlan          LTD.Throughput.RFC2544.PacketLossRatioFrameModification
phy2phy_cont                   Phy2Phy Continuous Stream
pvp_cont                       PVP Continuous Stream
pvvp_cont                      PVVP Continuous Stream
pvpv_cont                      Two VMs in parallel with Continuous Stream
phy2phy_scalability            LTD.Scalability.Flows.RFC2544.0PacketLoss
pvp_tput                       LTD.Throughput.RFC2544.PacketLossRatio
pvp_back2back                  LTD.Throughput.RFC2544.BackToBackFrames
pvvp_tput                      LTD.Throughput.RFC2544.PacketLossRatio
pvvp_back2back                 LTD.Throughput.RFC2544.BackToBackFrames
phy2phy_cpu_load               LTD.CPU.RFC2544.0PacketLoss
phy2phy_mem_load               LTD.Memory.RFC2544.0PacketLoss
phy2phy_tput_vpp               VPP: LTD.Throughput.RFC2544.PacketLossRatio
phy2phy_cont_vpp               VPP: Phy2Phy Continuous Stream
phy2phy_back2back_vpp          VPP: LTD.Throughput.RFC2544.BackToBackFrames
pvp_tput_vpp                   VPP: LTD.Throughput.RFC2544.PacketLossRatio
pvp_cont_vpp                   VPP: PVP Continuous Stream
pvp_back2back_vpp              VPP: LTD.Throughput.RFC2544.BackToBackFrames
pvvp_tput_vpp                  VPP: LTD.Throughput.RFC2544.PacketLossRatio
pvvp_cont_vpp                  VPP: PVP Continuous Stream
pvvp_back2back_vpp             VPP: LTD.Throughput.RFC2544.BackToBackFrames
=============================  ====================================================================

List of performance testcases above can be obtained by execution of:

.. code-block:: bash

   $ ./vsperf --list


Integration testcases
^^^^^^^^^^^^^^^^^^^^^

====================================== ========================================================================================
Testcase Name                          Description
====================================== ========================================================================================
vswitch_vports_add_del_flow            vSwitch - configure switch with vports, add and delete flow
vswitch_add_del_flows                  vSwitch - add and delete flows
vswitch_p2p_tput                       vSwitch - configure switch and execute RFC2544 throughput test
vswitch_p2p_back2back                  vSwitch - configure switch and execute RFC2544 back2back test
vswitch_p2p_cont                       vSwitch - configure switch and execute RFC2544 continuous stream test
vswitch_pvp                            vSwitch - configure switch and one vnf
vswitch_vports_pvp                     vSwitch - configure switch with vports and one vnf
vswitch_pvp_tput                       vSwitch - configure switch, vnf and execute RFC2544 throughput test
vswitch_pvp_back2back                  vSwitch - configure switch, vnf and execute RFC2544 back2back test
vswitch_pvp_cont                       vSwitch - configure switch, vnf and execute RFC2544 continuous stream test
vswitch_pvp_all                        vSwitch - configure switch, vnf and execute all test types
vswitch_pvvp                           vSwitch - configure switch and two vnfs
vswitch_pvvp_tput                      vSwitch - configure switch, two chained vnfs and execute RFC2544 throughput test
vswitch_pvvp_back2back                 vSwitch - configure switch, two chained vnfs and execute RFC2544 back2back test
vswitch_pvvp_cont                      vSwitch - configure switch, two chained vnfs and execute RFC2544 continuous stream test
vswitch_pvvp_all                       vSwitch - configure switch, two chained vnfs and execute all test types
vswitch_p4vp                           Configure 4 chained vnfs using the pvvp4 deployment 
vswitch_p4vp_tput                      deployment pvvp4, execute RFC2544 throughput test
vswitch_p4vp_back2back                 deployment pvvp4, execute RFC2544 back2back test
vswitch_p4vp_cont                      deployment pvvp4, execute RFC2544 continuous stream test
vswitch_p4vp_all                       deployment pvvp4, execute RFC2544 throughput test
2pvp_udp_dest_flows                    RFC2544 Continuous TC with 2 Parallel VMs, flows on UDP Dest Port, deployment pvpv2
4pvp_udp_dest_flows                    RFC2544 Continuous TC with 4 Parallel VMs, flows on UDP Dest Port, deployment pvpv4
6pvp_udp_dest_flows                    RFC2544 Continuous TC with 6 Parallel VMs, flows on UDP Dest Port, deployment pvpv6
vhost_numa_awareness                   vSwitch DPDK - verify that PMD threads are served by the same NUMA slot as QEMU instances
ixnet_pvp_tput_1nic                    PVP Scenario with 1 port towards IXIA
vswitch_vports_add_del_connection_vpp  VPP: vSwitch - configure switch with vports, add and delete connection
p2p_l3_multi_IP_ovs                    OVS: P2P L3 multistream with unique flow for each IP stream
p2p_l3_multi_IP_mask_ovs               OVS: P2P L3 multistream with 1 flow for /8 net mask
pvp_l3_multi_IP_mask_ovs               OVS: PVP L3 multistream with 1 flow for /8 net mask
pvvp_l3_multi_IP_mask_ovs              OVS: PVVP L3 multistream with 1 flow for /8 net mask
p2p_l4_multi_PORT_ovs                  OVS: P2P L4 multistream with unique flow for each IP stream
p2p_l4_multi_PORT_mask_ovs             OVS: P2P L4 multistream with 1 flow for /8 net and port mask
pvp_l4_multi_PORT_mask_ovs             OVS: PVP L4 multistream flows for /8 net and port mask
pvvp_l4_multi_PORT_mask_ovs            OVS: PVVP L4 multistream with flows for /8 net and port mask
p2p_l3_multi_IP_arp_vpp                VPP: P2P L3 multistream with unique ARP entry for each IP stream
p2p_l3_multi_IP_mask_vpp               VPP: P2P L3 multistream with 1 route for /8 net mask
p2p_l3_multi_IP_routes_vpp             VPP: P2P L3 multistream with unique route for each IP stream
pvp_l3_multi_IP_mask_vpp               VPP: PVP L3 multistream with route for /8 netmask
pvvp_l3_multi_IP_mask_vpp              VPP: PVVP L3 multistream with route for /8 netmask
p2p_l4_multi_PORT_arp_vpp              VPP: P2P L4 multistream with unique ARP entry for each IP stream and port check
p2p_l4_multi_PORT_mask_vpp             VPP: P2P L4 multistream with 1 route for /8 net mask and port check
p2p_l4_multi_PORT_routes_vpp           VPP: P2P L4 multistream with unique route for each IP stream and port check
pvp_l4_multi_PORT_mask_vpp             VPP: PVP L4 multistream with route for /8 net and port mask
pvvp_l4_multi_PORT_mask_vpp            VPP: PVVP L4 multistream with route for /8 net and port mask
vxlan_multi_IP_mask_ovs                OVS: VxLAN L3 multistream
vxlan_multi_IP_arp_vpp                 VPP: VxLAN L3 multistream with unique ARP entry for each IP stream
vxlan_multi_IP_mask_vpp                VPP: VxLAN L3 multistream with 1 route for /8 netmask
====================================== ========================================================================================

List of integration testcases above can be obtained by execution of:

.. code-block:: bash

   $ ./vsperf --integration --list

OVS/DPDK Regression TestCases
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

These regression tests verify several DPDK features used internally by Open vSwitch. Tests
can be used for verification of performance and correct functionality of upcoming DPDK
and OVS releases and release candidates.

These tests are part of integration testcases and they must be executed with
``--integration`` CLI parameter.

Example of execution of all OVS/DPDK regression tests:

.. code-block:: bash

   $ ./vsperf --integration --tests ovsdpdk_

Testcases are defined in the file ``conf/integration/01b_dpdk_regression_tests.conf``. This file
contains a set of configuration options with prefix ``OVSDPDK_``. These parameters can be used
for customization of regression tests and they will override some of standard VSPERF configuration
options. It is recommended to check OVSDPDK configuration parameters and modify them in accordance
with VSPERF configuration.

At least following parameters should be examined. Their values shall ensure, that DPDK and
QEMU threads are pinned to cpu cores of the same NUMA slot, where tested NICs are connected.

.. code-block:: python

    _OVSDPDK_1st_PMD_CORE
    _OVSDPDK_2nd_PMD_CORE
    _OVSDPDK_GUEST_5_CORES

DPDK NIC Support
++++++++++++++++

A set of performance tests to verify support of DPDK accelerated network interface cards.
Testcases use standard physical to physical network scenario with several vSwitch and
traffic configurations, which includes one and two PMD threads, uni and bidirectional traffic
and RFC2544 Continuous or RFC2544 Throughput with 0% packet loss traffic types.

======================================== ======================================================================================
Testcase Name                            Description
======================================== ======================================================================================
ovsdpdk_nic_p2p_single_pmd_unidir_cont   P2P with single PMD in OVS and unidirectional traffic.
ovsdpdk_nic_p2p_single_pmd_bidir_cont    P2P with single PMD in OVS and bidirectional traffic.
ovsdpdk_nic_p2p_two_pmd_bidir_cont       P2P with two PMDs in OVS and bidirectional traffic.
ovsdpdk_nic_p2p_single_pmd_unidir_tput   P2P with single PMD in OVS and unidirectional traffic.
ovsdpdk_nic_p2p_single_pmd_bidir_tput    P2P with single PMD in OVS and bidirectional traffic.
ovsdpdk_nic_p2p_two_pmd_bidir_tput       P2P with two PMDs in OVS and bidirectional traffic.
======================================== ======================================================================================

DPDK Hotplug Support
++++++++++++++++++++

A set of functional tests to verify DPDK hotplug support. Tests verify, that it is possible
to use port, which was not bound to DPDK driver during vSwitch startup. There is also
a test which verifies a possibility to detach port from DPDK driver. However support
for manual detachment of a port from DPDK has been removed from recent OVS versions and
thus this testcase is expected to fail.

======================================== ======================================================================================
Testcase Name                            Description
======================================== ======================================================================================
ovsdpdk_hotplug_attach                   Ensure successful port-add after binding a device to igb_uio after
                                         ovs-vswitchd is launched.
ovsdpdk_hotplug_detach                   Same as ovsdpdk_hotplug_attach, but delete and detach the device
                                         after the hotplug. Note  Support of netdev-dpdk/detach has been
                                         removed from OVS, so testcase will fail with recent OVS/DPDK
                                         versions.
======================================== ======================================================================================

RX Checksum Support
+++++++++++++++++++

A set of functional tests for verification of RX checksum calculation for tunneled traffic.
Open vSwitch enables RX checksum offloading by default if NIC supports it. It is to note,
that it is not possible to disable or enable RX checksum offloading. In order to verify
correct RX checksum calculation in software, user has to execute these testcases
at NIC without HW offloading capabilities.

Testcases utilize existing overlay physical to physical (op2p) network deployment
implemented in vsperf. This deployment expects, that traffic generator sends unidirectional
tunneled traffic (e.g. vxlan) and Open vSwitch performs data decapsulation and sends them
back to the traffic generator via second port.

======================================== ======================================================================================
Testcase Name                            Description
======================================== ======================================================================================
ovsdpdk_checksum_l3                      Test verifies RX IP header checksum (offloading) validation for
                                         tunneling protocols.
ovsdpdk_checksum_l4                      Test verifies RX UDP header checksum (offloading) validation for
                                         tunneling protocols.
======================================== ======================================================================================

Flow Control Support
++++++++++++++++++++

A set of functional testcases for the validation of flow control support in Open vSwitch
with DPDK support. If flow control is enabled in both OVS and Traffic Generator,
the network endpoint (OVS or TGEN) is not able to process incoming data and
thus it detects a RX buffer overflow. It then sends an ethernet pause frame (as defined at 802.3x)
to the TX side. This mechanism will ensure, that the TX side will slow down traffic transmission
and thus no data is lost at RX side.

Introduced testcases use physical to physical scenario to forward data between
traffic generator ports. It is expected that the processing of small frames in OVS is slower
than line rate. It means that with flow control disabled, traffic generator will
report a frame loss. On the other hand with flow control enabled, there should be 0%
frame loss reported by traffic generator.

======================================== ======================================================================================
Testcase Name                            Description
======================================== ======================================================================================
ovsdpdk_flow_ctrl_rx                     Test the rx flow control functionality of DPDK PHY ports.
ovsdpdk_flow_ctrl_rx_dynamic             Change the rx flow control support at run time and ensure the system
                                         honored the changes.
======================================== ======================================================================================

Multiqueue Support
++++++++++++++++++

A set of functional testcases for validation of multiqueue support for both physical
and vHost User DPDK ports. Testcases utilize P2P and PVP network deployments and
native support of multiqueue configuration available in VSPERF.

======================================== ======================================================================================
Testcase Name                            Description
======================================== ======================================================================================
ovsdpdk_mq_p2p_rxqs                      Setup rxqs on NIC port.
ovsdpdk_mq_p2p_rxqs_same_core_affinity   Affinitize rxqs to the same core.
ovsdpdk_mq_p2p_rxqs_multi_core_affinity  Affinitize rxqs to separate cores.
ovsdpdk_mq_pvp_rxqs                      Setup rxqs on vhost user port.
ovsdpdk_mq_pvp_rxqs_linux_bridge         Confirm traffic received over vhost RXQs with Linux virtio device in
                                         guest.
ovsdpdk_mq_pvp_rxqs_testpmd              Confirm traffic received over vhost RXQs with DPDK device in guest.
======================================== ======================================================================================

Vhost User
++++++++++

A set of functional testcases for validation of vHost User Client and vHost User
Server modes in OVS.

**NOTE:** Vhost User Server mode is deprecated and it will be removed from OVS
in the future.

======================================== ======================================================================================
Testcase Name                            Description
======================================== ======================================================================================
ovsdpdk_vhostuser_client                 Test vhost-user client mode
ovsdpdk_vhostuser_client_reconnect       Test vhost-user client mode reconnect feature
ovsdpdk_vhostuser_server                 Test vhost-user server mode
ovsdpdk_vhostuser_sock_dir               Verify functionality of vhost-sock-dir flag
======================================== ======================================================================================

Virtual Devices Support
+++++++++++++++++++++++

A set of functional testcases for verification of correct functionality of virtual
device PMD drivers.

======================================== ======================================================================================
Testcase Name                            Description
======================================== ======================================================================================
ovsdpdk_vdev_add_null_pmd                Test addition of port using the null DPDK PMD driver.
ovsdpdk_vdev_del_null_pmd                Test deletion of port using the null DPDK PMD driver.
ovsdpdk_vdev_add_af_packet_pmd           Test addition of port using the af_packet DPDK PMD driver.
ovsdpdk_vdev_del_af_packet_pmd           Test deletion of port using the af_packet DPDK PMD driver.
======================================== ======================================================================================

NUMA Support
++++++++++++

A functional testcase for validation of NUMA awareness feature in OVS.

======================================== ======================================================================================
Testcase Name                            Description
======================================== ======================================================================================
ovsdpdk_numa                             Test vhost-user NUMA support. Vhostuser PMD threads should migrate to
                                         the same numa slot, where QEMU is executed.
======================================== ======================================================================================

Jumbo Frame Support
+++++++++++++++++++

A set of functional testcases for verification of jumbo frame support in OVS.
Testcases utilize P2P and PVP network deployments and native support of jumbo
frames available in VSPERF.

============================================ ==================================================================================
Testcase Name                                Description
============================================ ==================================================================================
ovsdpdk_jumbo_increase_mtu_phy_port_ovsdb    Ensure that the increased MTU for a DPDK physical port is updated in
                                             OVSDB.
ovsdpdk_jumbo_increase_mtu_vport_ovsdb       Ensure that the increased MTU for a DPDK vhost-user port is updated in
                                             OVSDB.
ovsdpdk_jumbo_reduce_mtu_phy_port_ovsdb      Ensure that the reduced MTU for a DPDK physical port is updated in
                                             OVSDB.
ovsdpdk_jumbo_reduce_mtu_vport_ovsdb         Ensure that the reduced MTU for a DPDK vhost-user port is updated in
                                             OVSDB.
ovsdpdk_jumbo_increase_mtu_phy_port_datapath Ensure that the MTU for a DPDK physical port is updated in the
                                             datapath itself when increased to a valid value.
ovsdpdk_jumbo_increase_mtu_vport_datapath    Ensure that the MTU for a DPDK vhost-user port is updated in the
                                             datapath itself when increased to a valid value.
ovsdpdk_jumbo_reduce_mtu_phy_port_datapath
                                             Ensure that the MTU for a DPDK physical port is updated in the
                                             datapath itself when decreased to a valid value.
ovsdpdk_jumbo_reduce_mtu_vport_datapath      Ensure that the MTU for a DPDK vhost-user port is updated in the
                                             datapath itself when decreased to a valid value.
ovsdpdk_jumbo_mtu_upper_bound_phy_port       Verify that the upper bound limit is enforced for OvS DPDK Phy ports.
ovsdpdk_jumbo_mtu_upper_bound_vport          Verify that the upper bound limit is enforced for OvS DPDK vhost-user
                                             ports.
ovsdpdk_jumbo_mtu_lower_bound_phy_port       Verify that the lower bound limit is enforced for OvS DPDK Phy ports.
ovsdpdk_jumbo_mtu_lower_bound_vport          Verify that the lower bound limit is enforced for OvS DPDK vhost-user
                                             ports.
ovsdpdk_jumbo_p2p                            Ensure that jumbo frames are received, processed and forwarded
                                             correctly by DPDK physical ports.
ovsdpdk_jumbo_pvp                            Ensure that jumbo frames are received, processed and forwarded
                                             correctly by DPDK vhost-user ports.
ovsdpdk_jumbo_p2p_upper_bound                Ensure that jumbo frames above the configured Rx port's MTU are not
                                             accepted
============================================ ==================================================================================

Rate Limiting
+++++++++++++

A set of functional testcases for validation of rate limiting support. This feature
allows to configure an ingress policing for both physical and vHost User DPDK
ports.

**NOTE:** Desired maximum rate is specified in kilo bits per second and it defines
the rate of payload only.

======================================== ======================================================================================
Testcase Name                            Description
======================================== ======================================================================================
ovsdpdk_rate_create_phy_port             Ensure a rate limiting interface can be created on a physical DPDK
                                         port.
ovsdpdk_rate_delete_phy_port             Ensure a rate limiting interface can be destroyed on a physical DPDK
                                         port.
ovsdpdk_rate_create_vport                Ensure a rate limiting interface can be created on a vhost-user port.
ovsdpdk_rate_delete_vport                Ensure a rate limiting interface can be destroyed on a vhost-user
                                         port.
ovsdpdk_rate_no_policing                 Ensure when a user attempts to create a rate limiting interface but
                                         is missing policing rate argument, no rate limitiner is created.
ovsdpdk_rate_no_burst                    Ensure when a user attempts to create a rate limiting interface but
                                         is missing policing burst argument, rate limitiner is created.
ovsdpdk_rate_p2p                         Ensure when a user creates a rate limiting physical interface that
                                         the traffic is limited to the specified policer rate in a p2p setup.
ovsdpdk_rate_pvp                         Ensure when a user creates a rate limiting vHost User interface that
                                         the traffic is limited to the specified policer rate in a pvp setup.
ovsdpdk_rate_p2p_multi_pkt_sizes         Ensure that rate limiting works for various frame sizes.
======================================== ======================================================================================

Quality of Service
++++++++++++++++++

A set of functional testcases for validation of QoS support. This feature
allows to configure an egress policing for both physical and vHost User DPDK
ports.

**NOTE:** Desired maximum rate is specified in bytes per second and it defines
the rate of payload only.

======================================== ======================================================================================
Testcase Name                            Description
======================================== ======================================================================================
ovsdpdk_qos_create_phy_port              Ensure a QoS policy can be created on a physical DPDK port
ovsdpdk_qos_delete_phy_port              Ensure an existing QoS policy can be destroyed on a physical DPDK
                                         port.
ovsdpdk_qos_create_vport                 Ensure a QoS policy can be created on a virtual vhost user port.
ovsdpdk_qos_delete_vport                 Ensure an existing QoS policy can be destroyed on a vhost user port.
ovsdpdk_qos_create_no_cir                Ensure that a QoS policy cannot be created if the egress policer cir
                                         argument is missing.
ovsdpdk_qos_create_no_cbs                Ensure that a QoS policy cannot be created if the egress policer cbs
                                         argument is missing.
ovsdpdk_qos_p2p                          In a p2p setup, ensure when a QoS egress policer is created that the
                                         traffic is limited to the specified rate.
ovsdpdk_qos_pvp                          In a pvp setup, ensure when a QoS egress policer is created that the
                                         traffic is limited to the specified rate.
======================================== ======================================================================================

Custom Statistics
+++++++++++++++++

A set of functional testcases for validation of Custom Statistics support by OVS.
This feature allows Custom Statistics to be accessed by VSPERF.

These testcases require DPDK v17.11, the latest Open vSwitch(v2.9.90)
and the IxNet traffic-generator.

======================================== ======================================================================================
ovsdpdk_custstat_check                   Test if custom statistics are supported.
ovsdpdk_custstat_rx_error                Test bad ethernet CRC counter 'rx_crc_errors' exposed by custom
                                         statistics.

======================================== ======================================================================================

T-Rex in VM TestCases
^^^^^^^^^^^^^^^^^^^^^

A set of functional testcases, which use T-Rex running in VM as a traffic generator.
These testcases require a VM image with T-Rex server installed. An example of such
image is a vloop-vnf image with T-Rex available for download at:

http://artifacts.opnfv.org/vswitchperf/vnf/vloop-vnf-ubuntu-16.04_trex_20180209.qcow2

This image can be used for both T-Rex VM and loopback VM in ``vm2vm`` testcases.

**NOTE:** The performance of T-Rex running inside the VM is lower if compared to T-Rex
execution on bare-metal. The user should perform a calibration of the VM maximum FPS
capability, to ensure this limitation is understood.

======================================== ======================================================================================
trex_vm_cont                             T-Rex VM - execute RFC2544 Continuous Stream from T-Rex VM and loop
                                         it back through Open vSwitch.
trex_vm_tput                             T-Rex VM - execute RFC2544 Throughput from T-Rex VM and loop it back
                                         through Open vSwitch.
trex_vm2vm_cont                          T-Rex VM2VM - execute RFC2544 Continuous Stream from T-Rex VM and
                                         loop it back through 2nd VM.
trex_vm2vm_tput                          T-Rex VM2VM - execute RFC2544 Throughput from T-Rex VM and loop it back
                                         through 2nd VM.

======================================== ======================================================================================
