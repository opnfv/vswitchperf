# Top Makefile to build upstream packages.
#

# Copyright 2015 OPNFV
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

#
# Contributors:
#   Aihua Li, Huawei Technologies.

SUBBUILDS = src_vanilla
.PHONY: vhost subbuilds $(SUBBUILDS)

all clean distclean: vhost subbuilds

subbuilds: $(SUBBUILDS)
$(SUBBUILDS): vhost
	$(AT)mkdir -p ../$@/mk
	$(AT)cp -rf mk/* ../$@/mk
	$(AT)cp -rf package-list.mk ../$@/
	$(AT)cp Makefile.$@ ../$@/Makefile
	$(AT)$(MAKE) -C ../$@ $(MAKECMDGOALS)

vhost:
export VHOST_USER
include mk/master.mk
SUBDIRS =
SUBDIRS += l2fwd
SUBDIRS += dpdk
SUBDIRS += ovs
SUBDIRS += qemu
SUBDIRS += vpp
SUBDIRS += trex
ovs: dpdk
WITH_LINUX =
VHOST_USER = y
include mk/make-subsys.mk
