# makefile to manage dpdk package 
#
# Copyright (C) 2015 OPNFV 
#
# Copying and distribution of this file, with or without modification,
# are permitted in any medium without royalty provided the copyright
# notice and this notice are preserved.  This file is offered as-is,
# without warranty of any kind.
#
# Contributors:
#   Aihua Li, Huawei Technologies.

include ../mk/master.mk
include ../package-list.mk

.PHONY: install force_make 

# the name has been changed from version to version
ifeq ($(DPDK_TAG),v1.6.0r0)
DPDK_TARGET=x86_64-default-linuxapp-gcc
PATCH_FILE=patch-v1.6.0r0.diff
else	
DPDK_TARGET=x86_64-native-linuxapp-gcc
PATCH_FILE=
endif

WORK_DIR = dpdk
TAG_DONE_FLAG = $(WORK_DIR)/.$(DPDK_TAG).tag.done

all: force_make 
	@echo "Finished making $(WORK_DIR) "

INSTALL_TARGET = force_make

force_make: $(TAG_DONE_FLAG) 
	$(AT)cd $(WORK_DIR); make config T=$(DPDK_TARGET) && make
	@echo "Make done"

install: $(INSTALL_TARGET) 
	$(AT)sudo cp -a $(WORK_DIR)/$(DPDK_TARGET)/kmod $(INSTALL_DIR)/lib/modules/$(KERNEL_VERSION)
	@echo "install done"

# hard way to clean and clobber
clean:
clobber:
	$(AT)rm -rf $(WORK_DIR)

# cleanse is for developer who would like to keep the
# clone git repo, saving time to fetch again from url
ifneq ($(wildcard $(WORK_DIR/Makefile)),)	
	$(AT)$(MAKE) -C $(WORK_DIR) clean
endif
	$(AT)find $(WORK_DIR) -name *.a -delete
	$(AT)find $(WORK_DIR) -name *.o -delete
	$(AT)rm -rf $(TAG_DONE_FLAG)
	$(AT)cd $(WORK_DIR); git reset --hard;

$(WORK_DIR):
	$(AT)git clone $(DPDK_URL)

$(TAG_DONE_FLAG): $(WORK_DIR)
	$(AT)cd $(WORK_DIR); git checkout $(DPDK_TAG);
ifneq ($(PATCH_FILE),)
	$(AT)cd $(WORK_DIR); patch -p1 < ../$(PATCH_FILE)
endif
	$(AT)touch $@
