.. This work is licensed under a Creative Commons Attribution 4.0 International License.
.. http://creativecommons.org/licenses/by/4.0
.. (c) OPNFV, Intel Corporation, AT&T and others.

OPNFV Brahmaputra Scenarios
===========================
Available Tests and aspects of scenarios:

===================== ===========================================================
   Framework Test                          Definition
===================== ===========================================================
phy2phy_tput          PacketLossRatio_ for Phy2Phy_
back2back             BackToBackFrames_ for Phy2Phy_
phy2phy_tput_mod_vlan PacketLossRatioFrameModification_ for Phy2Phy_
phy2phy_cont          Phy2Phy_ blast vswitch at x% TX rate and measure throughput
pvp_cont              PVP_ blast vswitch at x% TX rate and measure throughput
pvvp_cont             PVVP_ blast vswitch at x% TX rate and measure throughput
phy2phy_scalability   Scalability0PacketLoss_ for Phy2Phy_
pvp_tput              PacketLossRatio_ for PVP_
pvp_back2back         BackToBackFrames_ for PVP_
pvvp_tput             PacketLossRatio_ for PVVP_
pvvp_back2back        BackToBackFrames_ for PVVP_
phy2phy_cpu_load      CPU0PacketLoss_ for Phy2Phy_
phy2phy_mem_load      Same as CPU0PacketLoss_ but using a memory intensive app
===================== ===========================================================

Supported deployment scenarios:

* Phy2Phy_: Physical port -> vSwitch -> Physical port.
* PVP_: Physical port -> vSwitch -> VNF -> vSwitch -> Physical port.
* PVVP_: Physical port -> vSwitch -> VNF -> vSwitch -> VNF -> vSwitch ->
  Physical port.

Loopback applications in the Guest can be:

* `DPDK testpmd <http://dpdk.org/doc/guides/testpmd_app_ug/index.html>`_.
* Linux Bridge.
* `l2fwd
  <http://artifacts.opnfv.org/vswitchperf/docs/userguide/testusage.html#l2fwd-kernel-module>`_.

Supported traffic generators:

* Ixia: IxOS and IxNet.
* Spirent.
* Dummy.

.. _PacketLossRatio: http://artifacts.opnfv.org/vswitchperf/docs/requirements/vswitchperf_ltd.html#test-id-ltd-throughput-rfc2544-packetlossratio

.. _BackToBackFrames: http://artifacts.opnfv.org/vswitchperf/docs/requirements/vswitchperf_ltd.html#test-id-ltd-throughput-rfc2544-backtobackframes

.. _PacketLossRatioFrameModification: http://artifacts.opnfv.org/vswitchperf/docs/requirements/vswitchperf_ltd.html#test-id-ltd-throughput-rfc2544-packetlossratioframemodification

.. _Scalability0PacketLoss: http://artifacts.opnfv.org/vswitchperf/docs/requirements/vswitchperf_ltd.html#test-id-ltd-scalability-rfc2544-0packetloss

.. _CPU0PacketLoss: http://artifacts.opnfv.org/vswitchperf/docs/requirements/vswitchperf_ltd.html#test-id-ltd-cpu-rfc2544-0packetloss

.. _Phy2Phy : http://artifacts.opnfv.org/vswitchperf/docs/requirements/vswitchperf_ltd.html#physical-port-vswitch-physical-port

.. _PVP: http://artifacts.opnfv.org/vswitchperf/docs/requirements/vswitchperf_ltd.html#physical-port-vswitch-vnf-vswitch-physical-port

.. _PVVP: http://artifacts.opnfv.org/vswitchperf/docs/requirements/vswitchperf_ltd.html#physical-port-vswitch-vnf-vswitch-vnf-vswitch-physical-port

