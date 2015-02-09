# makefile to manage ovs package
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

.PHONY: install force_install config force_make

# install depends on make
force_install: force_make

WORK_DIR = ovs
TAG_DONE_FLAG = $(WORK_DIR)/.$(OVS_TAG).done
CONFIG_CMD =
CONFIG_CMD += ./configure
CONFIG_CMD += --with-linux=$(LINUX_BUILD)
CONFIG_CMD += --prefix=$(INSTALL_DIR)/usr
CONFIG_CMD += --localstatedir=$(INSTALL_DIR)/usr/local
CONFIG_CMD += --with-dpdk=../../dpdk/dpdk/build

all: force_make
	@echo "Finished making $(WORK_DIR) "

config $(WORK_DIR)/Makefile: $(WORK_DIR)/configure
	$(AT)cd $(WORK_DIR); $(CONFIG_CMD)
	@echo "Configure done"

INSTALL_TARGET = force_install force_make

force_make: $(WORK_DIR)/Makefile
	$(AT)$(MAKE) -C $(WORK_DIR) $(MORE_MAKE_FLAGS)
	@echo "Make done"

force_install:
	$(AT)sudo make -C $(WORK_DIR) modules_install
	$(AT)sudo $(MAKE) -C $(WORK_DIR) install

install: $(INSTALL_TARGET)

# hard way to clean and clobber
clean:
clobber:
	$(AT)rm -rf $(WORK_DIR)

# cleanse is for developer who would like to keep the
# clone git repo, saving time to fetch again from url
cleanse:
ifneq ($(wildcard $(WORK_DIR/Makefile)),)	
	$(AT)$(MAKE) -C $(WORK_DIR) clean
endif
	$(AT)rm -rf $(WORK_DIR)/configure
	$(AT)rm -rf $(WORK_DIR)/Makefile
	$(AT)rm -rf $(WORK_DIR)/link.done
	$(AT)find $(WORK_DIR) -name *.a -delete
	$(AT)find $(WORK_DIR) -name *.o -delete
	$(AT)rm -rf $(TAG_DONE_FLAG)
	$(AT)cd $(WORK_DIR); git reset --hard;

.PHONY: boot
boot $(WORK_DIR)/configure:
	@echo "booting up ovs"
	$(AT)cd $(WORK_DIR); ./boot.sh
	@echo "done booting ovs"

boot $(WORK_DIR)/configure: $(TAG_DONE_FLAG)

$(WORK_DIR):
	$(AT)git clone $(OVS_URL)

$(TAG_DONE_FLAG): $(WORK_DIR)
	$(AT)cd ovs; git checkout $(OVS_TAG);
ifneq ($(PATCH_FILE),)
	$(AT)cd $(WORK_DIR); patch -p1 < ../$(PATCH_FILE)
endif
	$(AT)touch $@
