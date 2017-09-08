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
vswitch_p4vp                           Just configure 4 chained vnfs
vswitch_p4vp_tput                      4 chained vnfs, execute RFC2544 throughput test
vswitch_p4vp_back2back                 4 chained vnfs, execute RFC2544 back2back test
vswitch_p4vp_cont                      4 chained vnfs, execute RFC2544 continuous stream test
vswitch_p4vp_all                       4 chained vnfs, execute RFC2544 throughput test
2pvp_udp_dest_flows                    RFC2544 Continuous TC with 2 Parallel VMs, flows on UDP Dest Port
4pvp_udp_dest_flows                    RFC2544 Continuous TC with 4 Parallel VMs, flows on UDP Dest Port
6pvp_udp_dest_flows                    RFC2544 Continuous TC with 6 Parallel VMs, flows on UDP Dest Port
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
