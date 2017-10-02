.. This work is licensed under a Creative Commons Attribution 4.0 International License.
.. http://creativecommons.org/licenses/by/4.0
.. (c) OPNFV, Intel Corporation, AT&T and others.

VSPERF Test Scenarios
=====================

Predefined Tests run with CI:

===================== ===========================================================
   Test                          Definition
===================== ===========================================================
phy2phy_tput          :ref:`PacketLossRatio <PacketLossRatio>` for :ref:`Phy2Phy <Phy2Phy>`
back2back             :ref:`BackToBackFrames <BackToBackFrames>` for :ref:`Phy2Phy <Phy2Phy>`
phy2phy_tput_mod_vlan :ref:`PacketLossRatioFrameModification <PacketLossRatioFrameModification>` for :ref:`Phy2Phy <Phy2Phy>`
phy2phy_cont          :ref:`Phy2Phy <Phy2Phy>` blast vswitch at x% TX rate and measure throughput
pvp_cont              :ref:`PVP <PVP>` blast vswitch at x% TX rate and measure throughput
pvvp_cont             :ref:`PVVP <PVVP>` blast vswitch at x% TX rate and measure throughput
phy2phy_scalability   :ref:`Scalability0PacketLoss <Scalability0PacketLoss>` for :ref:`Phy2Phy <Phy2Phy>`
pvp_tput              :ref:`PacketLossRatio <PacketLossRatio>` for :ref:`PVP <PVP>`
pvp_back2back         :ref:`BackToBackFrames <BackToBackFrames>` for :ref:`PVP <PVP>`
pvvp_tput             :ref:`PacketLossRatio <PacketLossRatio>` for :ref:`PVVP <PVVP>`
pvvp_back2back        :ref:`BackToBackFrames <BackToBackFrames>` for :ref:`PVVP <PVVP>`
phy2phy_cpu_load      :ref:`CPU0PacketLoss <CPU0PacketLoss>` for :ref:`Phy2Phy <Phy2Phy>`
phy2phy_mem_load      Same as :ref:`CPU0PacketLoss <CPU0PacketLoss>` but using a memory intensive app
# Is this up to date? needs comment....
===================== ===========================================================

Deployment topologies:

* :ref:`Phy2Phy <Phy2Phy>`: Physical port -> vSwitch -> Physical port.
* :ref:`PVP <PVP>`: Physical port -> vSwitch -> VNF -> vSwitch -> Physical port.
* :ref:`PVVP <PVVP>`: Physical port -> vSwitch -> VNF -> vSwitch -> VNF -> vSwitch ->
  Physical port.

Loopback applications in the Guest:

* `DPDK testpmd <http://dpdk.org/doc/guides/testpmd_app_ug/index.html>`_.
* Linux Bridge.
* :ref:`l2fwd-module`

Supported traffic generators:

* Spirent Testcenter
* Ixia: IxOS and IxNet.
* Xena
* MoonGen
* Dummy
* T-Rex
