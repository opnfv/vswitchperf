# Upstream Package List
#
# Everything here is defined as its suggested default
# value, it can always be overriden when invoking Make

# dpdk section
# DPDK_URL ?= git://dpdk.org/dpdk
DPDK_URL ?= http://dpdk.org/git/dpdk
DPDK_TAG ?= v16.07

# OVS section
OVS_URL ?= https://github.com/openvswitch/ovs
#The Tag below is for OVS v2.5.0 with backwards compatibility support for Qemu
#versions < 2.5.
OVS_TAG ?= master

# QEMU section
QEMU_URL ?= https://github.com/qemu/qemu.git
QEMU_TAG ?= v2.5.0
