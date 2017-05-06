# makefile to manage trex package
#

# Copyright 2017 Martin Goldammer, OPNFV
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
	@echo "Finished pulling $(WORK_DIR) "

force_pull: $(WORK_DIR) Makefile
	$(AT)cd $(WORK_DIR) && git pull $(TREX_URL) $(TREX_TAG)
	@echo "git pull done"

$(WORK_DIR):
	$(AT)git clone $(TREX_URL) $(WORK_DIR)

$(TAG_DONE_FLAG): $(WORK_DIR)
	$(AT)cd $(WORK_DIR); git checkout $(QEMU_TAG)

install:
	@echo "Make install in $(WORK_DIR) (stub) "

clobber:
	$(AT)rm -rf $(WORK_DIR)

distclean:
	@echo "Make distclean in $(WORK_DIR) (stub) "

clean:
	@echo "Make clean in $(WORK_DIR) (stub) "

test:
	@echo "Make test in $(WORK_DIR) (stub) "

sanity:
	@echo "Make sanity in $(WORK_DIR) (stub) "
