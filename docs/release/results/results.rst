.. This work is licensed under a Creative Commons Attribution 4.0 International License.
.. http://creativecommons.org/licenses/by/4.0
.. (c) OPNFV, Intel Corporation, AT&T and others.

OPNFV Brahmaputra Results
=========================
The vsperf CI jobs that were used to obtain the
results can be found at https://wiki.opnfv.org/wiki/vsperf_results.

The following table maps the results in the test dashboard to the appropriate
test case in the VSPERF Framework and specifies the metric the vertical/Y axis
is plotting. **Please note**, the presence of dpdk within a test name signifies
that the vswitch under test was OVS with DPDK, while its absence indicates that
the vswitch under test was stock OVS.

===================== ===================== ================== ===============
   Dashboard Test        Framework Test          Metric        Guest Interface
===================== ===================== ================== ===============
tput_ovsdpdk          phy2phy_tput          Throughput (FPS)   N/A
tput_ovs              phy2phy_tput          Throughput (FPS)   N/A
b2b_ovsdpdk           back2back             Back-to-back value N/A
b2b_ovs               back2back             Back-to-back value N/A
tput_mod_vlan_ovs     phy2phy_tput_mod_vlan Throughput (FPS)   N/A
tput_mod_vlan_ovsdpdk phy2phy_tput_mod_vlan Throughput (FPS)   N/A
scalability_ovs       phy2phy_scalability   Throughput (FPS)   N/A
scalability_ovsdpdk   phy2phy_scalability   Throughput (FPS)   N/A
pvp_tput_ovsdpdkuser  pvp_tput              Throughput (FPS)   vhost-user
pvp_tput_ovsvirtio    pvp_tput              Throughput (FPS)   virtio-net
pvp_b2b_ovsdpdkuser   pvp_back2back         Back-to-back value vhost-user
pvp_b2b_ovsvirtio     pvp_back2back         Back-to-back value virtio-net
pvvp_tput_ovsdpdkuser pvvp_tput             Throughput (FPS)   vhost-user
pvvp_tput_ovsvirtio   pvvp_tput             Throughput (FPS)   virtio-net
pvvp_b2b_ovsdpdkuser  pvvp_back2back        Throughput (FPS)   vhost-user
pvvp_b2b_ovsvirtio    pvvp_back2back        Throughput (FPS)   virtio-net
===================== ===================== ================== ===============

The loopback application in the VNF used for PVP and PVVP scenarios was DPDK
testpmd.
