# makefile to manage VPP package
#

# Copyright 2017 Intel Corporation.
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

include ../mk/master.mk
include ../package-list.mk

WORK_DIR = vpp
TAG_DONE_FLAG = $(WORK_DIR)/.$(VPP_TAG).done

.PHONY: install force_install force_make

all: force_make
	@echo "Finished making $(WORK_DIR) "

config $(WORK_DIR)/Makefile: $(WORK_DIR)/configure
	$(AT)cd $(WORK_DIR); $(CONFIG_CMD)
	@echo "Configure done"

force_make: $(WORK_DIR)/Makefile
	$(AT)cd $(WORK_DIR) && git pull $(VPP_URL) $(VPP_TAG)
	@echo "git pull done"
	# install vpp dependecies, currently it works for RHEL, CentOS and Ubuntu
	# another option is to copy all required VPP dependencies into VSPERF
	# installation files and keep them updated
	$(AT)$(MAKE) -C $(WORK_DIR) UNATTENDED=y install-dep
	$(AT)$(MAKE) -C $(WORK_DIR) build-release $(MORE_MAKE_FLAGS)
	# vppctl expects that vpp_api_test is installed in system directories
	# in order to execute vppctl from src/ subtree we have to use absolute path
	$(AT)sed -i -e 's|vpp_api_test|$(CURDIR)/$(WORK_DIR)/build-root/install-vpp-native/vpp/bin/vpp_api_test|g' $(WORK_DIR)/build-root/install-vpp-native/vpp/bin/vppctl
	@echo "Make done"

install:
	@echo "Make install in $(WORK_DIR) (stub) "

# hard way to clean and clobber
clean:
	$(AT)cd $(WORK_DIR) && git clean -xfd *.o
clobber:
	$(AT)rm -rf $(WORK_DIR)

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
	$(AT)git clone $(VPP_URL) vpp

$(TAG_DONE_FLAG): $(WORK_DIR)
	$(AT)cd vpp; git checkout $(VPP_TAG)
ifneq ($(PATCH_FILE),)
	$(AT)cd $(WORK_DIR); patch -p1 < ../$(PATCH_FILE)
endif
	$(AT)touch $@
