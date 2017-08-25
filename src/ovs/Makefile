# makefile to manage ovs package
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

include ../mk/master.mk
include ../package-list.mk

WORK_DIR = ovs
TAG_DONE_FLAG = $(WORK_DIR)/.$(OVS_TAG).done
CONFIG_CMD =
CONFIG_CMD += ./configure
OVS_VANILLA = ../../src_vanilla/ovs

# If WITH_LINUX is defined, OVS is built without DPDK but with kernel
# module
# By default, OVS is built with DPDK

# WITH_LINUX is the Linux kernel build directory used for building
# OVS kernel module as documented in OVS --with-linux switch
ifneq ($(WITH_LINUX),) # Building with Linux kernel
CONFIG_CMD += --with-linux=$(WITH_LINUX)

else # Building with DPDK

# DPDK_DIR is the top directory for dpdk source tree
# it can be passed in from Makefile command
# if it is not set, try to read it in from environment
# if it is still not set, then set it using relative path
DPDK_DIR ?= $(shell echo $$DPDK_DIR)
ifeq ($(DPDK_DIR),)
DPDK_DIR = ../../dpdk/dpdk
endif

ifeq ($(DPDK_TARGET),)
DPDK_TARGET = x86_64-native-linuxapp-gcc
endif
CONFIG_CMD += --with-dpdk=$(DPDK_DIR)/$(DPDK_TARGET)
CONFIG_CMD += CFLAGS="-g -O2 -Wno-cast-align"

endif # Kernel vs. DPDK

.PHONY: install force_install config force_make

# install depends on make
force_install: force_make

all: force_make
	@echo "Finished making $(WORK_DIR) "

config $(WORK_DIR)/Makefile: $(WORK_DIR)/configure
	$(AT)cd $(WORK_DIR); $(CONFIG_CMD)
	@echo "Configure done"

INSTALL_TARGET = force_install force_make

force_make: $(WORK_DIR)/Makefile
	$(AT)cd $(WORK_DIR) && git pull $(OVS_URL) $(OVS_TAG)
	@echo "git pull done"
	$(AT)echo "WITH_LINUX = $(WITH_LINUX)"
	$(AT)$(MAKE) -C $(WORK_DIR) $(MORE_MAKE_FLAGS)
	@echo "Make done"

force_install:
	$(AT)sudo make -C $(WORK_DIR) modules_install
	$(AT)sudo $(MAKE) -C $(WORK_DIR) install

install: $(INSTALL_TARGET)

# hard way to clean and clobber
clean:
	$(AT)cd $(WORK_DIR) && git clean -xfd *.o
clobber:
	$(AT)rm -rf $(WORK_DIR)
	$(AT)rm -rf $(OVS_VANILLA)

# distclean is for developer who would like to keep the
# clone git repo, saving time to fetch again from url
distclean:
	$(AT)cd $(WORK_DIR) && git clean -xfd && git checkout -f

test:
	@echo "Make test in $(WORK_DIR) (stub) "

sanity:
	@echo "Make sanity in $(WORK_DIR) (stub) "

.PHONY: boot
# boot ovs is the process to produce the script 'configure'
boot $(WORK_DIR)/configure:
	@echo "booting up ovs"
	$(AT)cd $(WORK_DIR); ./boot.sh
	@echo "done booting ovs"

boot $(WORK_DIR)/configure: $(TAG_DONE_FLAG)

$(WORK_DIR):
	$(AT)git clone $(OVS_URL) ovs
	$(AT)mkdir -p $(OVS_VANILLA)
	$(AT)cp -rf ./* $(OVS_VANILLA)

$(TAG_DONE_FLAG): $(WORK_DIR)
	$(AT)cd ovs; git checkout $(OVS_TAG)
ifneq ($(PATCH_FILE),)
	$(AT)cd $(WORK_DIR); patch -p1 < ../$(PATCH_FILE)
endif
	$(AT)touch $@
