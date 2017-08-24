.. This work is licensed under a Creative Commons Attribution 4.0 International License.
.. http://creativecommons.org/licenses/by/4.0
.. (c) OPNFV, Intel Corporation, AT&T and others.

OPNFV Test Results
=========================
VSPERF CI jobs are run daily and sample results can be found at
https://wiki.opnfv.org/display/vsperf/Vsperf+Results

Testcase names shown in the dashboard are combination of orignal testcase
name from VSPERF framework and indication of used vswitch.

    Example:

    Testcase ``phy2phy_tput`` is executed for three vSwitch types: ``OvsDpdkVhost``,
    ``OvsVanilla`` and ``VppDpdkVhost``. In this case, following testcase names
    will be used in the dashboard: ``phy2phy_tput_ovsdpdkvhost``,
    ``phy2phy_tput_ovsvanilla`` and ``phy2phy_tput_vppdpdkvhost``.

In case of RFC2544 Throughput test, the recorded metric is FPS (frames per
second). For RFC2544 Back2Back test, the recorded metric is back-to-back
value (number of frames).

The loopback application in the VNF used for PVP and PVVP scenarios was DPDK
testpmd.

Guest interface types are ``vhost-user`` for ``OvsDpdkVhost`` and ``VppDpdkVhost``
and ``virtio-net`` for ``OvsVanilla``.
