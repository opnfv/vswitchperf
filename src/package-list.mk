# Upstream Package List
#
# Everything here is defined as its suggested default
# value, it can always be overriden when invoking Make

# dpdk section
# DPDK_URL ?= git://dpdk.org/dpdk
DPDK_URL ?= http://dpdk.org/git/dpdk
DPDK_TAG ?= v16.11

# OVS section
OVS_URL ?= https://github.com/openvswitch/ovs
OVS_TAG ?= 04de404e1bfa63706237aa78ee065d67538f8fe9

# QEMU section
QEMU_URL ?= https://github.com/qemu/qemu.git
QEMU_TAG ?= v2.5.0
