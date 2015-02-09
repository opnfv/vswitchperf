# Master makefile definitions for project opnfv vswitchperf
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

.PHONY: $(SUBDIRS)

all clean clobber install uninstall: $(SUBDIRS)
	$(AT)echo "finished making $@"

$(SUBDIRS):
	$(AT)echo "Enter directory $@"
	$(AT)$(MAKE) -C $@ $(MAKECMDGOALS)
