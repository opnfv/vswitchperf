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

WORK_DIR = trex
TAG_DONE_FLAG = $(WORK_DIR)/.$(TREX_TAG).done

.PHONY: force_pull

all: force_pull
	@echo "Finished making $(WORK_DIR) "

config $(WORK_DIR)/Makefile: $(WORK_DIR)/configure
#	$(AT)cd $(WORK_DIR); $(CONFIG_CMD)
	@echo "Configure done"

force_pull: $(WORK_DIR)/Makefile
	$(AT)cd $(WORK_DIR) && git pull $(TREX_URL) $(TREX_TAG)
	@echo "git pull done"

$(WORK_DIR)/configure: $(TAG_DONE_FLAG)

$(WORK_DIR):
	$(AT)git clone $(TREX_URL) $(WORK_DIR)

$(TAG_DONE_FLAG): $(WORK_DIR)
	$(AT)cd trex; git checkout $(TREX_TAG)
