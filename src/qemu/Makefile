# makefile to manage qemu package
#

# Copyright (c) 2015 OPNFV and Intel Corporation.
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

WORK_DIR = qemu
TAG_DONE_FLAG = $(WORK_DIR)/.$(QEMU_TAG).done
INSTALL_TARGET = force_make force_install
CONFIG_CMD =
CONFIG_CMD += ./configure
CONFIG_CMD += --target-list="x86_64-softmmu"
QEMU_VANILLA = ../../src_vanilla/qemu
QEMU_CUSE = ../../src_cuse/qemu

all: force_make

.PHONY: install force_install config force_make

config $(WORK_DIR)/Makefile: $(WORK_DIR)/configure
	$(AT)cd $(WORK_DIR); $(CONFIG_CMD)
	@echo "Configure done"

force_make: $(WORK_DIR)/Makefile
	$(AT)cd $(WORK_DIR) && git pull $(QEMU_URL) $(QEMU_TAG)
	$(AT)echo "git pull done"
	$(AT)$(MAKE) -C $(WORK_DIR) $(MORE_MAKE_FLAGS)
	@echo "Make done"

force_install:
	$(AT)sudo $(MAKE) -C $(WORK_DIR) install

install: $(INSTALL_TARGET)

# hard way to clean and clobber
clean:
	$(AT)cd $(WORK_DIR) && git clean -xfd *.o
clobber:
	$(AT)rm -rf $(WORK_DIR)
	$(AT)rm -rf $(QEMU_VANILLA)
	$(AT)rm -rf $(QEMU_CUSE)

# distclean is for developer who would like to keep the
# clone git repo, saving time to fetch again from url
distclean:
	$(AT)cd $(WORK_DIR) && git clean -xfd && git checkout -f

test:
	@echo "Make test in $(WORK_DIR) (stub) "

sanity:
	@echo "Make sanity in $(WORK_DIR) (stub) "

$(WORK_DIR)/configure: $(TAG_DONE_FLAG)

$(WORK_DIR):
	$(AT)git clone $(QEMU_URL)
	$(AT)mkdir -p $(QEMU_VANILLA)
	$(AT)cp -rf ./* $(QEMU_VANILLA)
	$(AT)mkdir -p $(QEMU_CUSE)
	$(AT)cp -rf ./* $(QEMU_CUSE)

$(TAG_DONE_FLAG): $(WORK_DIR)
	$(AT)cd $(WORK_DIR); git checkout $(QEMU_TAG)
ifneq ($(PATCH_FILE),)
	$(AT)cd $(WORK_DIR); patch -p1 < ../$(PATCH_FILE)
endif
	$(AT)touch $@
