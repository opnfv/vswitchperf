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
#     Aihua Li, Huawei Technologies.
#   ...

# user has the full control to decide where to put the build by specifying INSTALL_DIR from the make input
# try to read it in from environment
INSTALL_DIR ?= $(shell echo $$INSTALL_DIR)

# if it is stillnot set, then set it to default
ifeq ($(INSTALL_DIR),)
INSTALL_DIR = /opt/nfv
endif

KERNEL_VERSION ?= $(shell uname -r)

LINUX_BUILD = /lib/modules/$(KERNEL_VERSION)/build
LINUX_SOURCE = $(LINUX_BUILD)

# control the project versions we are building
DPDK_VERSION ?= dpdk-dpdk-1.6.0r0
OVS_VERSION ?= openvswitch-2.3.0

# for debugging Makefile
# Make V as a synonum for VERBOSE
ifdef V
VERBOSE = $(V)
endif

VERBOSE ?= 0

ifeq ($(VERBOSE),0)
    AT = @
else
    BASH_X = -x
endif

DEBUG_MAKE_VARS += LINUX_BUILD
DEBUG_MAKE_VARS += INSTALL_TARGET

.DEFAULT_GOAL := all
.PHONY: all clean clobber

# print out individual make variables by asking for target "print-<VAR_NAME>"
PRINT_VARIABLES = $(patsubst %, print-%, $(filter-out ^% <% ?% @% *% \%% +% $(DEBUG_MAKE_VARS), $(.VARIABLES)) $(DEBUG_MAKE_VARS))

.PHONY : $(PRINT_VARIABLES)
$(PRINT_VARIABLES) :
	@echo '$(subst ',",$($(@:print-%=%)))'

