# Copyright (c) 2016-2017 Intel corporation.
#
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Apache License, Version 2.0
# which accompanies this distribution, and is available at
# http://www.apache.org/licenses/LICENSE-2.0
#
# Upstream Package List
#
# Everything here is defined as its suggested default
# value, it can always be overriden when invoking Make

# dpdk section
# DPDK_URL ?= git://dpdk.org/dpdk
DPDK_URL ?= http://dpdk.org/git/dpdk
DPDK_TAG ?= v18.11-rc2

# OVS section
OVS_URL ?= https://github.com/openvswitch/ovs
OVS_TAG ?= v2.12.0

# VPP section
VPP_URL ?= https://git.fd.io/vpp
VPP_TAG ?= v19.08.1

# QEMU section
QEMU_URL ?= https://github.com/qemu/qemu.git
QEMU_TAG ?= v3.1.1

# TREX section
TREX_URL ?= https://github.com/cisco-system-traffic-generator/trex-core.git
TREX_TAG ?= v2.38
