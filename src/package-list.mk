# Upstream Package List
#
# Everything here is defined as its suggested default
# value, it can always be overriden when invoking Make

# dpdk section
DPDK_URL ?= http://dpdk.org/git/dpdk
#..c5fc has fix for array index oob in eal memory
DPDK_TAG ?= d307f7957c9da6dee264ab7c9b349871c5a4c5fc

# OVS section
OVS_URL ?= https://github.com/openvswitch/ovs
#OVS_TAG ?= da79ce2b71dd879e7f20fdddc715568f6a74185a 
OVS_TAG ?= master 
