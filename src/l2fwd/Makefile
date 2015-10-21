# Copyright 2015 Futurewei Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# A copy of the license is included with this distribution. If you did not
# recieve a copy you may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

obj-m += l2fwd.o

KBUILD_CFLAGS += -Wno-unused-function -Wno-unused-label -Wno-unused-variable
# Allow kernel version to be overridden by environment
KERNEL_VERSION ?= $(shell uname -r)

KERNELDIR := /lib/modules/$(KERNEL_VERSION)/build
PWD := $(shell pwd)

all:
	$(MAKE) -C $(KERNELDIR) M=$(PWD) modules

force_make: all

sanity:
	@echo "Make sanity in $(WORK_DIR) (stub) "

clean:
	$(MAKE) -C $(KERNELDIR) M=$(PWD) clean
	rm -f l2fwd*deb

distclean: clean

clobber: clean


install:
	sudo mkdir /lib/modules/`uname -r`/kernel/net/core
	sudo cp *.ko /lib/modules/`uname -r`/kernel/net/core

uninstall:
	sudo rm /lib/modules/`uname -r`/kernel/net/core/l2fwd.ko

debian-package: all
	./gen_debian_package.sh
