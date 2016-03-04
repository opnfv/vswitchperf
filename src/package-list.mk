# Upstream Package List
#
# Everything here is defined as its suggested default
# value, it can always be overriden when invoking Make

# dpdk section
# DPDK_URL ?= git://dpdk.org/dpdk
DPDK_URL ?= http://dpdk.org/git/dpdk
DPDK_TAG ?= v2.2.0

# OVS section
OVS_URL ?= https://github.com/openvswitch/ovs
#OVS_TAG ?= v2.5.0
OVS_TAG ?= f3ea2ad27fd076735fdb78286980749bb12fe1ce

# QEMU section
QEMU_URL ?= https://github.com/qemu/qemu.git
QEMU_TAG ?= v2.3.0
